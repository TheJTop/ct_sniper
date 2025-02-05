from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Dict, Any
import time
import logging

class WebScraper:
    def __init__(self, headless: bool = True, wait_time: int = 10, 
                 custom_options: Optional[Dict[str, Any]] = None):
        """
        Initialize the WebScraper with customizable options.
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
            wait_time (int): Default wait time for elements to load
            custom_options (dict): Additional Chrome options to add
        """
        self.wait_time = wait_time
        self.driver = None
        self.options = self._setup_options(headless, custom_options)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _setup_options(self, headless: bool, custom_options: Optional[Dict[str, Any]] = None) -> Options:
        """Set up Chrome options with customizable settings."""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Default options for stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Add any custom options
        if custom_options:
            for option, value in custom_options.items():
                chrome_options.add_argument(f'--{option}={value}')
        
        return chrome_options

    def start_driver(self):
        """Initialize and start the Chrome driver."""
        if not self.driver:
            self.driver = webdriver.Chrome(options=self.options)
            self.logger.info("Chrome driver started successfully")

    def quit_driver(self):
        """Safely quit the Chrome driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Chrome driver closed successfully")

    def scrape_page(self, url: str, 
                    wait_for_element: str = "body",
                    by: By = By.TAG_NAME,
                    additional_wait: int = 5) -> Optional[str]:
        """
        Scrape content from a JavaScript-rendered page.
        
        Args:
            url (str): The URL to scrape
            wait_for_element (str): Element to wait for before scraping
            by (selenium.webdriver.common.by.By): Method to locate element
            additional_wait (int): Extra time to wait for JS content
            
        Returns:
            Optional[str]: The scraped content or None if failed
        """
        try:
            if not self.driver:
                self.start_driver()

            self.logger.info(f"Fetching {url}...")
            self.driver.get(url)

            # Wait for specified content to load
            wait = WebDriverWait(self.driver, self.wait_time)
            wait.until(EC.presence_of_element_located((by, wait_for_element)))

            # Additional wait for JavaScript content
            if additional_wait:
                time.sleep(additional_wait)

            # Get the page source after JavaScript has rendered
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.logger.info("Content extracted successfully")
            
            return page_text

        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            return None

    def __enter__(self):
        """Enable use of context manager (with statement)."""
        self.start_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure driver is closed when exiting context."""
        self.quit_driver()