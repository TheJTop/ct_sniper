from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    """Setup Chrome driver with necessary options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    return webdriver.Chrome(options=chrome_options)

def extract_page_content(url):
    """Extract content from a JavaScript-rendered page"""
    driver = setup_driver()
    
    try:
        print(f"Fetching {url}...")
        driver.get(url)
        
        # Wait for content to load (adjust timeout and class name as needed)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Give extra time for JavaScript content to load
        time.sleep(5)
        
        # Get the page source after JavaScript has rendered
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        return page_text
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://nitter.net/elonmusk/with_replies"
    
    print("Starting extraction...")
    content = extract_page_content(url)
    
    if content:
        print("\nExtracted content:")
        print("=" * 50)
        print(content)
        print("=" * 50)
    else:
        print("Failed to extract content")