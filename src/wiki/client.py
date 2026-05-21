import httpx

class MinecraftWiki:
    BASE_URL = "https://minecraft.wiki/api.php"
    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "AgentMinecraft/1.0"
            },
            timeout=8
        )
        
    def get_extract(self, title):
        response = self.client.get(
            self.BASE_URL,
            params={
                "action": "query",
                "prop": "extracts",
                "titles": title,
                "explaintext": 1,
                "format": "json"
            }
        )
        
        return response.json()
    
    def close(self):
        self.client.close()

 
