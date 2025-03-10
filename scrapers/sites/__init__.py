"""
Site-specific scrapers for Japanese property listing websites.
"""

import sys
import os

# Add the parent directory to sys.path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from typing import Dict, Type
from common.base_scraper import BaseScraper

# Import all scrapers
from sites.suumo import SuumoScraper
from sites.homes import HomesScraper
from sites.athome import AtHomeScraper
from sites.akiyamart import AkiyaMartScraper

# Register all scrapers by name
SCRAPERS: Dict[str, Type[BaseScraper]] = {
    "suumo": SuumoScraper,
    "homes": HomesScraper,
    "athome": AtHomeScraper,
    "akiyamart": AkiyaMartScraper,
}
