# JapanHouse Scrapers

This directory contains web scrapers for various Japanese property listing websites.

## Structure

- `common/`: Common utilities and the base scraper class
- `sites/`: Individual scrapers for specific Japanese property listing sites
- `data/`: Directory where scraped data is stored
- `logs/`: Directory where logs are stored
- `run_scrapers.py`: Script to run the scrapers

## Available Scrapers

Currently, the following scrapers are implemented:

1. **SUUMO** (`suumo.py`): Scraper for [SUUMO](https://suumo.jp), one of Japan's largest property listing sites
2. **HOMES** (`homes.py`): Scraper for [HOMES](https://www.homes.co.jp), a popular Japanese real estate website
3. **AtHome** (`athome.py`): Scraper for [AtHome](https://www.athome.co.jp), another major Japanese property listing site

## Usage

### Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Scrapers

Run all scrapers with default settings:

```bash
python run_scrapers.py
```

Run specific scrapers:

```bash
python run_scrapers.py --scrapers suumo,homes
```

Customize the search:

```bash
python run_scrapers.py --location osaka --property-type buy --max-pages 3
```

### Command Line Options

- `--scrapers`: Comma-separated list of scrapers to run (default: all)
- `--location`: Location to search for (default: tokyo)
- `--property-type`: Property type to search for, "rent" or "buy" (default: rent)
- `--max-pages`: Maximum number of pages to scrape (default: 5)

## Output

Scraped data is saved as JSON files in the `data/` directory with the naming format:
`{scraper_name}_{location}_{property_type}_{timestamp}.json`

## Extending

To add a new scraper:

1. Create a new file in the `sites/` directory (e.g., `new_site.py`)
2. Implement a scraper class that inherits from `BaseScraper`
3. Register the scraper in `sites/__init__.py`

## Notes

- These scrapers are designed for educational and personal use only
- Be respectful of websites' terms of service and robots.txt
- Consider implementing rate limiting and proxy rotation for production use
