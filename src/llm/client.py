import httpx

def llama_cpp(system_prompt, user_prompt):
    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }
    response = httpx.post("http://localhost:8081/v1/chat/completions", json=body, timeout=None)
    content = response.json().get("choices")[0].get("message").get("content")
    return content

