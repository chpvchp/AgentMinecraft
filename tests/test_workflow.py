# ===== TEXT =====#
import re
import json

# ===== LANGSMITH ===== #
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("LANGSMITH_TRACING"))

# ===== LANGGRAPH ===== #
from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# ===== MODULES ===== #
from src.searxng.client import get_list_search
from src.llm.client import llama_cpp


# ===== STATE ===== #
class AgentMC(TypedDict):
    user_input: str
    agent_response: str
    tool_result: list
    count: int
    
    
# ===== TOOLS ===== #
tools = {
    "tools": [
        {
            "name": "get_list_search",
            "description": "Công cụ lấy danh sách các trang web có thông liên quan được tổng hợp từ nhiều nguồn.",
            "arguments": {"query": "Từ khóa tìm kiếm", "top_k": "Số lượng kết trang web trả về, mặc định là 4"}
        }
    ]
}

tools_registry = {
    "get_list_search": get_list_search
}

# ===== NODES ===== #
def agent(state):
    # Debug
    print("INPUT NODE AGENT")
    print(state)
    print("=" * 64, "\n")
    system_prompt = f"""
    # VAI TRÒ
    Bạn là Agent Minecraft.

    # TOOLS
    {tools}
    
    # QUY TẮC CHUNG
    - Ưu tiên sử dụng tool khi cần dữ liệu không chắc chắn.
    - Lựa chọn tools phù hợp với yêu cầu của người dùng.
    - Không bịa đặt, không đoán kiến thức.
    - Trả lời ngắn gọn vào trọng tâm yêu cầu, trừ khi người dùng có yêu cầu khác.
    - Chỉ trả lời khi yêu cầu liên quan đến Minecraft, trường hợp yêu cầu khác hãy trả lời rằng nó nằm ngoài lĩnh vực.
    
    # QUY TẮC KHI DÙNG TOOL VÀ NHẬN DỮ LIỆU TỪ TOOL
    - Khi muốn gọi tool, BẮT BUỘC CHỈ trả về text có cấu trúc như sau:
    
    Thought: <suy nghĩ của bạn về yêu cầu người dùng>
    Action: <tên tool muốn gọi>
    Action Input: {{"tham_so_1":"<_>" "tham_so_2":"<_>"}}
    
    Ví dụ:
    Thought: Người dùng yêu cầu "Minecraft là gì?". Tôi cần tìm kiếm từ Internet
    Action: get_list_search
    Action Input: {{"query":"Minecraft là gì?", "top_k":4}}

    # QUY TẮC KHI NHẬN Observation
    Khi nhận dữ liệu từ Observation:
    - Phân tích dữ liệu trả về
    - TUYỆT ĐỐI không bịa thêm thông tin ngoài Observation
    - BẮT BUỘC trả lời theo format:

    Answer: <câu trả lời ngắn gọn, rõ ràng>
    
    - Nếu dữ liệu tool không đủ, gọi lại tool với tham số tối ưu hơn.
    - Nếu hết hạn gọi tool, hãy đưa ra câu trả lời cuối cùng dựa trên dữ liệu hiện có.
    
    # QUY TẮC TƯ DUY (CHAIN)
    - Luôn suy nghĩ trước khi gọi tool
    - Chọn tool chính xác nhất, tránh gọi dư thừa
    - Nếu nhiều tool phù hợp → chọn tool đơn giản nhất trước

    # QUY TẮC AN TOÀN LOGIC
    - Không tự tạo recipe, command, hoặc mechanics nếu không có tool xác nhận
    - Không “đoán theo kinh nghiệm”
    - Minecraft data phải dựa vào tool hoặc nguồn hệ thống
    """
    user_prompt = f"""
    # USER INPUT
    {state.get("user_input")}
    
    # OBSERVATION
    {state.get("tool_result", "")}
    """
    llm_response = llama_cpp(system_prompt=system_prompt, user_prompt=user_prompt)
    return {
        "agent_response": llm_response
    }

def route_node(state):
    if "Action" not in state.get("agent_response") or "Action Input" not in state.get("agent_response") or state.get("count") > 3:
        return "end"
    else:
        return "tool"
    
    
def tool_node(state):
    # Debug
    print("INPUT NODE TOOL")
    print(state)
    print("=" * 64, "\n")
    agent_response = state.get("agent_response")
    tool_ = re.search(r"Action: \s*(.*)", agent_response).group(1)
    args = json.loads(re.search(r"Action Input: \s*(.*)", agent_response).group(1))
    results = tools_registry[tool_](**args)
    return {
        "tool_result": state.get("tool_result", []) + [results],
        "count": state.get("count") + 1
    }
    
# ===== GRAPH ===== #
graph = StateGraph(AgentMC)
graph.add_node("agent", agent)
graph.add_node("tool", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    route_node,
    {
        "end": END,
        "tool": "tool"
    }
)
graph.add_edge("tool", "agent")
graph = graph.compile()

with open("graph.png", "wb") as png:
    png.write(graph.get_graph().draw_mermaid_png())
    

# ===== WORKFLOWS ===== #
state: AgentMC = {
            "user_input": "Bản 26.2 khi nào ra",
            "agent_response": "",
            "tool_result": [],
            "count": 0
        }

for step in graph.stream(state):
    node_name = list(step.keys())[0]
    state.update(step[node_name])

# Debug
print("OUTPUT STATE")
print(state)
print("=" * 64, "\n")
    
    
    
    