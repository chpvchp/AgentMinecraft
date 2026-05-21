from playwright.sync_api import sync_playwright

class MincraftWiki:
    BASE_URL = "https://minecraft.wiki/api.php"
    
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.request = self.playwright.request.new_context()
        
    def get_extract(self, title):
        response = self.request.get(
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
        self.request.dispose()
        self.playwright.stop()
    
wiki = MincraftWiki()

print(wiki.get_extract("Mace"))