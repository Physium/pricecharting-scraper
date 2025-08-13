"""
Test script to debug the PriceCharting scraper and improve parsing accuracy.
"""

from pricecharting_scraper import PriceChartingScraper
import logging

def test_url():
    """Test the scraper with the Latias ex URL."""
    url = "https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239"
    
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    scraper = PriceChartingScraper()
    result = scraper.scrape_card(url)
    
    print("=== Scraping Results ===")
    if result:
        print(f"Card Name: {result['card_name']}")
        print(f"Ungraded Price: ${result['ungraded_price']:.2f}" if result['ungraded_price'] else "Ungraded Price: Not found")
        print(f"PSA 10 Price: ${result['psa10_price']:.2f}" if result['psa10_price'] else "PSA 10 Price: Not found")
        print(f"URL: {result['url']}")
    else:
        print("Failed to scrape the URL")
    
    # Expected results based on websearch:
    print("\n=== Expected Results ===")
    print("Card Name: Latias ex #239")
    print("Ungraded Price: $146.64")
    print("PSA 10 Price: $420.00")

if __name__ == "__main__":
    test_url()
