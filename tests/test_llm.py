from src.llm.client import llama_cpp

api = "http://localhost:8081/v1/chat/completions" 

print(llama_cpp(api, system_prompt="Bạn là trợ lý thân thiện", user_prompt="Bạn là ai?"))