from playwright.sync_api import sync_playwright

def get_info_wiki(titles):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        page = browser.new_page()
        
        url = f"https://minecraft.wiki/api.php?action=query&prop=extracts&titles={titles}&explaintext=1&format=json"
        
        response = page.goto(url=url)

        data = page.text_content("body")

        page.close()
        
        return data
    
print(get_info_wiki("Mace"))