"""
TCG Price API - A service for extracting trading card pricing information.
"""

from pricecharting_scraper import PriceChartingScraper
from typing import Optional, Dict, Any
import logging
import json


class TCGPriceAPI:
    """Main API class for TCG pricing information."""
    
    def __init__(self, timeout: int = 10, log_level: int = logging.WARNING):
        """Initialize the API with optional configuration."""
        self.scraper = PriceChartingScraper(timeout=timeout)
        logging.basicConfig(level=log_level)
        
    def get_card_prices(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get pricing information for a card from a PriceCharting URL.
        
        Args:
            url: The PriceCharting URL for the card
            
        Returns:
            Dict with card information or None if failed
        """
        return self.scraper.scrape_card(url)
    
    def get_card_prices_json(self, url: str) -> str:
        """
        Get pricing information as JSON string.
        
        Args:
            url: The PriceCharting URL for the card
            
        Returns:
            JSON string with card information or error message
        """
        result = self.get_card_prices(url)
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return json.dumps({"error": "Failed to scrape URL", "url": url}, indent=2)
    
    def is_pricecharting_url(self, url: str) -> bool:
        """Check if the URL is a valid PriceCharting URL."""
        return "pricecharting.com" in url.lower()


def main():
    """Simple CLI for the TCG Price API."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python tcg_price_api.py <pricecharting_url>")
        print("Example: python tcg_price_api.py https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239")
        sys.exit(1)
    
    url = sys.argv[1]
    api = TCGPriceAPI()
    
    if not api.is_pricecharting_url(url):
        print("Error: Please provide a valid PriceCharting URL")
        sys.exit(1)
    
    print("Fetching card pricing information...")
    result_json = api.get_card_prices_json(url)
    print(result_json)


if __name__ == "__main__":
    main()
