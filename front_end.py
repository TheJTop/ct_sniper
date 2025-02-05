## Run this to auto scrape, find CA, and buy CA

from utils import JupiterClient
from webscraper import WebScraper
from typing import List, Optional
from urllib.parse import quote

#X Handles
HANDLES = ['elonmusk', 'stoolpresidente', 'cloutdotme', 'pasternak', 'kanyewest', 'realDonaldTrump']




query = " OR ".join(f"from:{username}" for username in usernames)
encoded_query = quote(query)
url = f"https://nitter.net/search?f=tweets&q={encoded_query}"


def extract_ca(text):
    # Replace non-alphanumeric characters with spaces
    cleaned_text = ''.join(char if char.isalnum() else ' ' for char in text)
    
    # Split into words
    words = cleaned_text.split()
    
    # Find words of length 43 or 44
    target_words = [word for word in words if len(word) in [43, 44]]
    
    return target_words

#Initial Run through:
with WebScraper() as scraper:
    content = scraper.scrape_page(url)
    return content

def scrape_twitter_users(usernames: List[str]) -> Optional[str]:
    """
    Scrape tweets from multiple Twitter/X users using Nitter.
    
    Args:
        usernames (List[str]): List of Twitter usernames without the @ symbol
        
    Returns:
        Optional[str]: Combined content of tweets if successful, None if failed
    """
    if not usernames:
        return None
        
    # Build the search query
    query = " OR ".join(f"from:{username}" for username in usernames)
    encoded_query = quote(query)
    url = f"https://nitter.net/search?f=tweets&q={encoded_query}"
    
    with WebScraper() as scraper:
        content = scraper.scrape_page(url)
        return content
    

sample = scrape_twitter_users(["j0hnwang", "the_jtop", "Shmurda"])
