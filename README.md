# TCG Sorter - PriceCharting Scraper

A Python service for extracting Pokemon card pricing information from PriceCharting.com.

## Features

- Extract card name, ungraded price, and PSA 10 price from PriceCharting URLs
- Simple API that can be integrated into larger systems
- Command-line interface for quick testing
- JSON output support
- **Batch processing from CSV files**
- Progress tracking with visual progress bars
- Respectful rate limiting (configurable delays)

## Installation

### Option 1: Using Virtual Environment (Recommended)

1. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# On Windows
# .venv\Scripts\activate

# Or use the provided script (macOS/Linux only)
source activate.sh
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. To deactivate the virtual environment when done:
```bash
deactivate
```

### Option 2: Global Installation

1. Install dependencies globally:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

**Note**: If using a virtual environment, make sure it's activated first:
```bash
source .venv/bin/activate  # or source activate.sh
```

#### Basic Scraper
```bash
python pricecharting_scraper.py "https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239"
```

#### API Interface (JSON output)
```bash
python tcg_price_api.py "https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239"
```

#### Batch Processing (CSV input/output)
```bash
# Process a CSV file of URLs
python batch_processor.py input.csv output.csv

# With custom column name and delay
python batch_processor.py cards.csv results.csv url 2.0
```

**CSV Input Format:**
```csv
url
https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239
https://www.pricecharting.com/game/pokemon-surging-sparks/pikachu-ex-229
```

**CSV Output Format:**
```csv
link,name,ungraded_price,psa10_price
https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239,Latias ex #239,146.64,420.0
https://www.pricecharting.com/game/pokemon-surging-sparks/pikachu-ex-229,Pikachu Ex 229 Prices,260.0,
```

### Python API

```python
from tcg_price_api import TCGPriceAPI

# Initialize the API
api = TCGPriceAPI()

# Get card pricing information
url = "https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239"
result = api.get_card_prices(url)

if result:
    print(f"Card: {result['card_name']}")
    print(f"Ungraded: ${result['ungraded_price']}")
    print(f"PSA 10: ${result['psa10_price']}")
```

### Example Output

```json
{
  "card_name": "Latias ex #239",
  "ungraded_price": 146.64,
  "psa10_price": 420.0,
  "url": "https://www.pricecharting.com/game/pokemon-surging-sparks/latias-ex-239"
}
```

## Files

- `pricecharting_scraper.py` - Core scraper class
- `tcg_price_api.py` - High-level API wrapper  
- `batch_processor.py` - CSV batch processing script
- `test_scraper.py` - Test script for debugging
- `requirements.txt` - Python dependencies
- `activate.sh` - Virtual environment activation helper script
- `sample_input.csv` - Example input CSV file
- `.venv/` - Virtual environment directory (created after setup)

## Notes

- The scraper bypasses SSL verification for PriceCharting.com
- Prices are extracted from the main pricing table on the card's page
- The service is designed to be modular for integration into larger systems
- **Batch processing includes rate limiting** (default 1 second delay between requests)
- Missing prices (PSA 10, ungraded) are left as empty strings in CSV output
- Progress bars show real-time processing status

## Future Enhancements

- Support for additional grading companies (BGS, SGC, etc.)
- Database storage of pricing history
- Caching for frequently accessed URLs
- Retry logic for failed requests
- Export to additional formats (Excel, JSON)
