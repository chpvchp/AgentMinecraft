from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    
    page = browser.new_page()
    
    response = page.goto("https://minecraft.wiki/api.php?action=query&prop=extracts&titles=Mace&explaintext=1&format=json")
    
    print(page.text_content("body"))
    
    page.close()