import httpx

def rank_core(url):
    if "minecraft.wiki" in url:
        return 10
    elif "minecraft.fandom.com" in url:
        return 8
    else:
        return 1
    
def parse_results(results, top_k):
    list_page = []
    for _ in range(top_k):
        if "www.youtube.com" in results[_].get("url"):
            continue
        core = rank_core(results[_].get("url"))
        list_page.append({
            "url": results[_].get("url"),
            "title": results[_].get("title"),
            "content": results[_].get("content"),
            "core": core
        })
    return list_page

def get_list_search(query: str, top_k: int = 4):
    params = {
        "q": query,
        "format": "json",
    }
    with httpx.Client() as client:
        response = client.get("http://localhost:8082/search", params=params, timeout=8)
        
        if response.status_code != 200:
            return {
                "error": response.status_code
            }
        else:
            results = response.json().get("results")
            data = parse_results(results, top_k)
            list_data = {
                "query": query,
                "results": data
            }
            return list_data