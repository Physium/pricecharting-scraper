"""
Batch processor for scraping multiple PriceCharting URLs from a CSV file.
"""

import csv
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

from pricecharting_scraper import PriceChartingScraper


class BatchProcessor:
    """Batch processor for multiple PriceCharting URLs."""
    
    def __init__(self, delay: float = 1.0, timeout: int = 10):
        """
        Initialize the batch processor.
        
        Args:
            delay: Delay between requests in seconds (be respectful to the server)
            timeout: Request timeout in seconds
        """
        self.scraper = PriceChartingScraper(timeout=timeout)
        self.delay = delay
        
    def process_csv(self, input_file: str, output_file: str, url_column: str = 'url') -> Dict[str, int]:
        """
        Process a CSV file of URLs and output results to a new CSV file.
        
        Args:
            input_file: Path to input CSV file containing URLs
            output_file: Path to output CSV file for results
            url_column: Name of the column containing URLs (default: 'url')
            
        Returns:
            Dict with processing statistics
        """
        # Read input CSV
        urls = self._read_input_csv(input_file, url_column)
        
        if not urls:
            print(f"❌ No URLs found in {input_file}")
            return {"total": 0, "success": 0, "failed": 0}
        
        print(f"📋 Found {len(urls)} URLs to process")
        print(f"⏱️  Using {self.delay}s delay between requests")
        
        # Process URLs
        results = []
        failed_count = 0
        
        for i, url in enumerate(tqdm(urls, desc="Processing URLs")):
            try:
                # Scrape the URL
                card_data = self.scraper.scrape_card(url)
                
                if card_data:
                    results.append({
                        'link': url,
                        'name': card_data['card_name'],
                        'ungraded_price': card_data['ungraded_price'] or '',
                        'psa10_price': card_data['psa10_price'] or ''
                    })
                    tqdm.write(f"✅ {card_data['card_name']}: ${card_data['ungraded_price']} / ${card_data['psa10_price']}")
                else:
                    results.append({
                        'link': url,
                        'name': 'ERROR',
                        'ungraded_price': '',
                        'psa10_price': ''
                    })
                    failed_count += 1
                    tqdm.write(f"❌ Failed to scrape: {url}")
                
            except Exception as e:
                results.append({
                    'link': url,
                    'name': f'ERROR: {str(e)}',
                    'ungraded_price': '',
                    'psa10_price': ''
                })
                failed_count += 1
                tqdm.write(f"❌ Error processing {url}: {e}")
            
            # Be respectful to the server
            if i < len(urls) - 1:  # Don't delay after the last request
                time.sleep(self.delay)
        
        # Write output CSV
        self._write_output_csv(output_file, results)
        
        stats = {
            "total": len(urls),
            "success": len(urls) - failed_count,
            "failed": failed_count
        }
        
        print(f"\n📊 Processing complete!")
        print(f"   Total URLs: {stats['total']}")
        print(f"   Successful: {stats['success']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Output saved to: {output_file}")
        
        return stats
    
    def _read_input_csv(self, input_file: str, url_column: str) -> List[str]:
        """Read URLs from input CSV file."""
        urls = []
        
        try:
            with open(input_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                if url_column not in reader.fieldnames:
                    available_columns = ', '.join(reader.fieldnames or [])
                    raise ValueError(f"Column '{url_column}' not found. Available columns: {available_columns}")
                
                for row in reader:
                    url = row[url_column].strip()
                    if url and self._is_pricecharting_url(url):
                        urls.append(url)
                    elif url:
                        print(f"⚠️  Skipping invalid URL: {url}")
                        
        except FileNotFoundError:
            print(f"❌ Input file not found: {input_file}")
        except Exception as e:
            print(f"❌ Error reading input file: {e}")
            
        return urls
    
    def _write_output_csv(self, output_file: str, results: List[Dict[str, Any]]) -> None:
        """Write results to output CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['link', 'name', 'ungraded_price', 'psa10_price']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(results)
                
        except Exception as e:
            print(f"❌ Error writing output file: {e}")
    
    def _is_pricecharting_url(self, url: str) -> bool:
        """Check if URL is a valid PriceCharting URL."""
        return "pricecharting.com" in url.lower()


def main():
    """CLI for batch processing."""
    if len(sys.argv) < 3:
        print("Usage: python batch_processor.py <input_csv> <output_csv> [url_column] [delay]")
        print()
        print("Arguments:")
        print("  input_csv   - Path to CSV file containing URLs")
        print("  output_csv  - Path for output CSV file")
        print("  url_column  - Column name containing URLs (default: 'url')")
        print("  delay       - Delay between requests in seconds (default: 1.0)")
        print()
        print("Example:")
        print("  python batch_processor.py cards.csv results.csv url 1.5")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    url_column = sys.argv[3] if len(sys.argv) > 3 else 'url'
    delay = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    
    # Validate input file exists
    if not Path(input_file).exists():
        print(f"❌ Input file does not exist: {input_file}")
        sys.exit(1)
    
    # Set up logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise
        format='%(levelname)s: %(message)s'
    )
    
    # Process the CSV file
    processor = BatchProcessor(delay=delay)
    stats = processor.process_csv(input_file, output_file, url_column)
    
    # Exit with error code if there were failures
    if stats["failed"] > 0 and stats["success"] == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
