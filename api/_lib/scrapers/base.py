from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import time
import random
import re

class BaseScraper(ABC):
    """Base class for all property scrapers"""

    use_playwright = False  # Override in subclass to use Playwright

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        self._playwright = None
        self._browser = None

    @property
    @abstractmethod
    def fuente(self) -> str:
        """Return the source name (mercadolibre, zonaprop, argenprop)"""
        pass

    @abstractmethod
    def get_search_url(self, barrio: str, page: int = 1) -> str:
        """Build the search URL for a specific neighborhood"""
        pass

    @abstractmethod
    def parse_listing(self, element: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Parse a single listing element and return property data"""
        pass

    @abstractmethod
    def get_listings_from_page(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        """Extract listing elements from a search results page"""
        pass

    def _start_browser(self):
        """Start Playwright browser"""
        if self._browser is None:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            print(f"Started Playwright browser for {self.fuente}")

    def _stop_browser(self):
        """Stop Playwright browser"""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return parsed BeautifulSoup object"""
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(2, 5))

            if self.use_playwright:
                return self._fetch_with_playwright(url)
            else:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, "lxml")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _fetch_with_playwright(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch page using Playwright browser"""
        try:
            self._start_browser()
            page = self._browser.new_page()
            page.set_extra_http_headers({
                "Accept-Language": "es-AR,es;q=0.9,en;q=0.8"
            })

            # Navigate and wait for content to load
            page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait a bit for dynamic content
            page.wait_for_timeout(2000)

            content = page.content()
            page.close()

            return BeautifulSoup(content, "lxml")
        except Exception as e:
            print(f"Playwright error fetching {url}: {e}")
            return None

    def scrape_barrio(self, barrio: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Scrape properties from a specific neighborhood"""
        properties = []

        for page in range(1, max_pages + 1):
            url = self.get_search_url(barrio, page)
            soup = self.fetch_page(url)

            if not soup:
                break

            listings = self.get_listings_from_page(soup)

            if not listings:
                break

            for listing in listings:
                try:
                    prop = self.parse_listing(listing)
                    if prop:
                        prop["barrio"] = barrio
                        prop["fuente"] = self.fuente
                        prop["operacion"] = "venta"
                        properties.append(prop)
                except Exception as e:
                    print(f"Error parsing listing: {e}")
                    continue

        return properties

    def scrape_all(self, barrios: List[str], max_pages_per_barrio: int = 2) -> List[Dict[str, Any]]:
        """Scrape properties from multiple neighborhoods"""
        all_properties = []

        try:
            for barrio in barrios:
                print(f"Scraping {barrio}...")
                properties = self.scrape_barrio(barrio, max_pages_per_barrio)
                all_properties.extend(properties)
                print(f"  Found {len(properties)} properties in {barrio}")
        finally:
            # Always close browser if using Playwright
            if self.use_playwright:
                self._stop_browser()

        return all_properties

    @staticmethod
    def clean_price(price_text: str) -> tuple[Optional[float], str]:
        """Extract price and currency from text"""
        if not price_text:
            return None, "USD"

        price_text = price_text.strip().upper()

        # Determine currency
        currency = "USD"
        if "$" in price_text and "US" not in price_text and "U$" not in price_text:
            currency = "ARS"

        # Extract numbers
        numbers = re.findall(r"[\d.,]+", price_text)
        if numbers:
            # Take the first number found
            price_str = numbers[0].replace(".", "").replace(",", ".")
            try:
                return float(price_str), currency
            except ValueError:
                pass

        return None, currency

    @staticmethod
    def clean_number(text: str) -> Optional[int]:
        """Extract integer from text"""
        if not text:
            return None
        numbers = re.findall(r"\d+", text)
        return int(numbers[0]) if numbers else None

    @staticmethod
    def clean_area(text: str) -> Optional[float]:
        """Extract area in m2 from text"""
        if not text:
            return None
        # Match patterns like "50 m²", "50m2", "50 m2"
        match = re.search(r"([\d.,]+)\s*m", text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(",", "."))
            except ValueError:
                pass
        return None
