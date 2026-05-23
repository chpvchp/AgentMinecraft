"""
title: Agent Minecraft
author: me
version: alpha0
"""

from typing import TypedDict, List, Generator, Iterator, Union
from langgraph.graph import StateGraph, START, END
from src.llm.client import llama_cpp

# ===== API ===== #
API_URL = "http://localhost:8081/v1/chat/completions"

# ===== SETUP DEBUG ===== #
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("LANGSMITH_TRACING"))


# ===== TOOLS ===== #


# ===== STATE ===== #
class AgentMC(TypedDict):
    user_input: str
    agent_response: str
    tool_result: str
    

# ===== NODES ===== #
def agent_node(state: AgentMC):
    system_prompt = f"""
    You are a Minecraft Agent.

    TOOLS:

    RULES:
    - MUST use tool for Minecraft-related queries
    - If not Minecraft-related → refuse

    OUTPUT FORMAT (STRICT):
    - Output MUST be a single valid JSON object
    - Output MUST contain ONLY JSON, nothing before or after
    - DO NOT use markdown
    - DO NOT use ``` or ```json
    - DO NOT explain anything

    VALID FORMAT:
    {{"tools":"get_info","args":"Mace"}}

    INVALID EXAMPLES:
    - ```json
    - "Here is the result:"
    - any extra text

    ABSOLUTE RULE:
    Return ONLY raw JSON string.
    """
    user_prompt = state.get("user_input")
    response = llama_cpp(API_URL, system_prompt=system_prompt, user_prompt=user_prompt)
    print("A:", response)
    return {
        "agent_response": response
    }
    

# ===== GRAPH ===== #
def build_graph():
    graph = StateGraph(AgentMC)
    graph.add_node("agent", agent_node)
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)
    graph = graph.compile()
    # with open("graph.png", "wb") as png:
    #     png.write(graph.get_graph().draw_mermaid_png())
    return graph


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
            "agent_response": "",
            "tool_result": ""
        }
        
        for step in self.graph.stream(state):
            node_name = list(step.keys())[0]
            step_status = self.NODES_STATUS.get(node_name)
            yield self.__status(step_status)
            state.update(step[node_name])
            
        yield self.__status("Đã xong", done = True)
        yield state.get("agent_response", "Không tìm thấy kết quả")
    
    