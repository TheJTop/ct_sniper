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

import requests
import os
from dotenv import load_dotenv

load_dotenv()
NTFY_CODE = os.getenv('NTFY_CODE')

# Test notification with high priority and sounds
requests.post(
    f"https://ntfy.sh/{NTFY_CODE}",
    data="This is a test notification from CT Sniper!",
    headers={
        "Title": "Test Notification",
        "Priority": "high",
        "Tags": "test,bell,tada"
    }
)