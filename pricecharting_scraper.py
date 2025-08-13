"""
PriceCharting scraper for extracting Pokemon card pricing information.
"""

import re
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import logging

# Disable SSL warnings for scraping
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PriceChartingScraper:
    """Scraper for PriceCharting.com to extract card pricing information."""
    
    def __init__(self, timeout: int = 10):
        """Initialize the scraper with optional timeout."""
        self.timeout = timeout
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_card(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a PriceCharting URL and extract card information.
        
        Args:
            url: The PriceCharting URL for the card
            
        Returns:
            Dict containing card_name, ungraded_price, and psa10_price, or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract card name from the page title or h1
            card_name = self._extract_card_name(soup)
            ungraded_price = self._extract_ungraded_price(soup)
            psa10_price = self._extract_psa10_price(soup)
            
            if not card_name:
                logging.warning("Could not extract card name from the page")
                return None
                
            return {
                'card_name': card_name,
                'ungraded_price': ungraded_price,
                'psa10_price': psa10_price,
                'url': url
            }
            
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error while scraping: {e}")
            return None
    
    def _extract_card_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the card name from the page."""
        # Try to find the card name in the h1 tag
        h1_tag = soup.find('h1')
        if h1_tag:
            # Clean up the text - remove "Pokemon Surging Sparks" part
            card_text = h1_tag.get_text(strip=True)
            # Extract just the card name part (before "Pokemon")
            if 'Pokemon' in card_text:
                card_name = card_text.split('Pokemon')[0].strip()
                return card_name
            return card_text
            
        # Fallback: try to extract from title tag
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # Similar cleanup for title
            if 'Pokemon' in title_text:
                card_name = title_text.split('Pokemon')[0].strip()
                return card_name
            return title_text
            
        return None
    
    def _extract_ungraded_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract the ungraded price from the pricing table."""
        return self._extract_price_by_grade(soup, 'Ungraded')
    
    def _extract_psa10_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract the PSA 10 price from the pricing table."""
        return self._extract_price_by_grade(soup, 'PSA 10')
    
    def _extract_price_by_grade(self, soup: BeautifulSoup, grade_name: str) -> Optional[float]:
        """
        Extract price for a specific grade from the pricing table.
        
        Args:
            soup: BeautifulSoup object of the page
            grade_name: Grade to search for (e.g., 'Ungraded', 'PSA 10')
            
        Returns:
            Price as float or None if not found
        """
        # Strategy 1: Look for the main comparison table (first table with grade headers)
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) >= 2:
                # Check if this is the main pricing table by looking for grade headers
                header_row = rows[0]
                price_row = rows[1] if len(rows) > 1 else None
                
                header_cells = header_row.find_all(['td', 'th'])
                price_cells = price_row.find_all(['td', 'th']) if price_row else []
                
                # Look for the grade in header cells
                for i, cell in enumerate(header_cells):
                    cell_text = cell.get_text(strip=True)
                    if grade_name.lower() in cell_text.lower():
                        # Found the grade column, get corresponding price
                        if i < len(price_cells):
                            price_text = price_cells[i].get_text(strip=True)
                            # Extract just the dollar amount, ignore +/- changes
                            price_match = re.search(r'\$[\d,]+\.?\d*', price_text)
                            if price_match:
                                return self._parse_price(price_match.group())
        
        # Strategy 2: Look for the full price guide table (simple two-column format)
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    grade_cell = cells[0].get_text(strip=True)
                    price_cell = cells[1].get_text(strip=True)
                    
                    if grade_name.lower() == grade_cell.lower():
                        return self._parse_price(price_cell)
        
        # Strategy 3: Look for price spans with class 'price js-price'
        price_spans = soup.find_all('span', class_=['price', 'js-price'])
        
        # For the main comparison table, we need to find the right position
        if grade_name == 'Ungraded':
            # The first price span should be ungraded
            if price_spans:
                return self._parse_price(price_spans[0].get_text(strip=True))
        elif grade_name == 'PSA 10':
            # PSA 10 is typically the 6th price in the main table (0-indexed: 5)
            # Or we can search more systematically
            for span in price_spans:
                # Look for nearby text that mentions PSA 10
                parent_text = span.parent.get_text() if span.parent else ""
                if 'psa' in parent_text.lower() and '10' in parent_text:
                    return self._parse_price(span.get_text(strip=True))
        
        return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price text and return as float.
        
        Args:
            price_text: Text containing price (e.g., '$146.64', '$420.00')
            
        Returns:
            Price as float or None if parsing fails
        """
        if not price_text or price_text.strip() == '-':
            return None
            
        # Remove currency symbols, commas, and extra whitespace
        clean_price = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
        
        try:
            return float(clean_price)
        except ValueError:
            logging.warning(f"Could not parse price: {price_text}")
            return None


def main():
    """Simple CLI for testing the scraper."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pricecharting_scraper.py <pricecharting_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    scraper = PriceChartingScraper()
    
    logging.basicConfig(level=logging.INFO)
    
    result = scraper.scrape_card(url)
    
    if result:
        print(f"Card Name: {result['card_name']}")
        print(f"Ungraded Price: ${result['ungraded_price']:.2f}" if result['ungraded_price'] else "Ungraded Price: Not found")
        print(f"PSA 10 Price: ${result['psa10_price']:.2f}" if result['psa10_price'] else "PSA 10 Price: Not found")
    else:
        print("Failed to scrape the URL")
        sys.exit(1)


if __name__ == "__main__":
    main()
