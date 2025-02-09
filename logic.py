from utils.jupiter import JupiterClient
from utils.webscraper import WebScraper
from typing import List, Optional
from urllib.parse import quote

jupiter = JupiterClient()

def extract_ca(text):
    # Replace non-alphanumeric characters with spaces
    cleaned_text = ''.join(char if char.isalnum() else ' ' for char in text)
    
    # Split into words
    words = cleaned_text.split()
    
    # Find words of length 43 or 44
    target_words = [word for word in words if len(word) in [43, 44]]
    
    return target_words

def find_new_ca(usernames, timeout):

    if not usernames:
        return None
        
    # Build the search query
    query = " OR ".join(f"from:{username}" for username in usernames)
    encoded_query = quote(query)
    url = f"https://nitter.net/search?f=tweets&q={encoded_query}"
    
    with WebScraper() as scraper:
        content = scraper.scrape_page(url)
        old_cas = extract_ca(content)
    
    with WebScraper() as scraper:
        while True:
            content = scraper.scrape_page(url)
            new_cas = extract_ca(content)
            print(new_cas)
            found_new_cas = [ca for ca in new_cas if ca not in old_cas]
                        
            # If we found any new CAs, return them
            if found_new_cas:
                return found_new_cas
            

def make_trade(jupiter, input_token, output_token, amount, slippage_bps = 0.2):

    jupiter.make_trade(
    jupiter.TOKEN_ADDRESSES['SOL'], 
    jupiter.TOKEN_ADDRESSES['USDC'], 
    amount=str(int(0.0005 * 1_000_000_000))
)

