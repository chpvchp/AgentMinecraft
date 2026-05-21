"""
title: Agent Minecraft
author: me
version: alpha0
"""

from typing import TypedDict, List, Generator, Iterator, Union
from langgraph.graph import StateGraph, START, END
from src.wiki.client import MinecraftWiki
from src.llm.client import llama_cpp

# ===== API ===== #
API_URL = "http://localhost:8081/v1/chat/completions"

# ===== SETUP DEBUG ===== #
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("LANGSMITH_TRACING"))


# ===== TOOLS ===== #
wiki = MinecraftWiki()
tools = {
    "get_info": wiki.get_extract()
}

# ===== STATE ===== #
class AgentMC(TypedDict):
    user_input: str
    agent_response: str
    

# ===== NODES ===== #
def agent_node(state: AgentMC):
    system_prompt = f"""
    Bạn là một Agent Minecraft hữu ích.
    Nhiệm vụ của bạn là trả lời các câu hỏi của người dùng.

    # Các tools bạn có
    {tools}
    
    # Quy tắc
    - BẮT BUỘC dùng tool khi người dùng hỏi về Minecraft.
    - Nếu người dùng hỏi các lĩnh vực ngoài Minecraft, hãy từ chối trả lời vì chuyên môn không đủ.
    - Khi dùng tool, BẮT BUỘC chỉ được trả về một json có format: {{"tools": "<tên_tool>"}}.
    """
    
    user_prompt = state.get("user_input")
    response = llama_cpp(API_URL, system_prompt=system_prompt, user_prompt=user_prompt)
    return {
        "agent_response": response
    }


# ===== GRAPH ===== #
def build_graph():
    graph = StateGraph(AgentMC)
    graph.add_node("agent", agent_node)
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)
    return graph.compile()


# ========================== #
# ===== PIPELINES MAIN ===== #
# ========================== #
class Pipeline:
    
    NODES_STATUS = {
        "agent": "Agent đang phân tích..."
    }
    
    def __init__(self):
        self.name = "Agent Minecraft"
        self.graph = build_graph()
        
    def __status(self, description, done = False):
        return {
            "event": {
                "type": "status",
                "data": {"description": description, "done": done}
            }
        }
        
    def pipe(self, user_message, model_id, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        
        state: AgentMC = {
            "user_input": user_message,
            "agent_response": ""
        }
        
        for step in self.graph.stream(state):
            node_name = list(step.keys())[0]
            step_status = self.NODES_STATUS.get(node_name)
            yield self.__status(step_status)
            state.update(step[node_name])
            
        yield self.__status("Đã xong", done = True)
        yield state.get("agent_response", "Không tìm thấy kết quả")
    