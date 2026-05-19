import httpx

def llama_cpp(api, system_prompt, user_prompt):
    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }
    
    response = httpx.post(api, json=body, timeout=None)
    return response.json()