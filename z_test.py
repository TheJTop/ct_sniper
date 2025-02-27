from utils.jupiter import JupiterClient
from utils.webscraper import WebScraper
from typing import List, Optional
from urllib.parse import quote

#jupiter = JupiterClient()

def scrape_page(url):

    
    with WebScraper() as scraper:
        content = scraper.scrape_page(url)
        print(content)

scrape_page(url = "https://nitter.space/search?f=tweets&q=from:the_jtop")