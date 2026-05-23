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
    tool_result: str
    
    
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


# ===== NODES ===== #
def agent(state):
    # Debug
    print("INPUT NODE AGENT")
    print(state)
    print("#" * 8)
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
    Name: <tên tool muốn gọi>
    Args: tham_so_1="<_>" tham_so_2="<_>"
    
    Ví dụ:
    Thought: Người dùng yêu cầu "Minecraft là gì?". Tôi cần tìm kiếm từ Internet
    Name: get_list_search
    Args: query="Minecraft là gì?", top_k=4
    
    # QUY TẮC KHI NHẬN TOOL RESULT
    Khi nhận dữ liệu từ TOOL_RESULTS:
    - Phân tích dữ liệu trả về
    - TUYỆT ĐỐI không bịa thêm thông tin ngoài tool result
    - BẮT BUỘC trả lời theo format:

    Answer: <câu trả lời ngắn gọn, rõ ràng>
    
    - Nếu dữ liệu tool không đủ, gọi lại tool tối ưu hơn.
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
    user_prompt = state.get("user_input")
    llm_response = llama_cpp(system_prompt=system_prompt, user_prompt=user_prompt)
    return {
        "agent_response": llm_response
    }

def tool_node(state):
    pass
    
# ===== GRAPH ===== #
graph = StateGraph(AgentMC)
graph.add_node("agent", agent)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)
graph = graph.compile()

with open("graph.png", "wb") as png:
    png.write(graph.get_graph().draw_mermaid_png())
    

# ===== WORKFLOWS ===== #
state: AgentMC = {
            "user_input": "Mace là gì",
            "agent_response": "",
            "tool_result": ""
        }

for step in graph.stream(state):
    node_name = list(step.keys())[0]
    print(node_name)
    state.update(step[node_name])

print(state.get("agent_response"))
    
    
    
    