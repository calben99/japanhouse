"""
Base Scraper Class for JapanHouse
This module provides a base class for all scrapers to inherit from,
ensuring consistent behavior and interfaces.
"""
import abc
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger


class BaseScraper(abc.ABC):
    """
    Base scraper class that defines the interface for all scrapers.
    Each property site scraper should inherit from this class.
    """
    
    def __init__(self, name: str, base_url: str):
        """
        Initialize the base scraper.
        
        Args:
            name: Name of the scraper (usually the website name)
            base_url: Base URL of the website to scrape
        """
        self.name = name
        self.base_url = base_url
        self.results = []
        logger.info(f"Initialized {name} scraper for {base_url}")
    
    @abc.abstractmethod
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Main scraping method that must be implemented by child classes.
        
        Args:
            **kwargs: Additional arguments specific to each scraper
            
        Returns:
            List of property listings as dictionaries
        """
        pass
    
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize the scraped data.
        
        Args:
            data: Raw data from the scraper
            
        Returns:
            Cleaned and standardized data
        """
        # Basic cleaning operations common to all scrapers
        cleaned = {}
        
        # Set standard fields
        cleaned["source"] = self.name
        cleaned["source_url"] = data.get("url", "")
        cleaned["scraped_at"] = datetime.now().isoformat()
        
        # Convert prices to integers (remove currency symbols, commas, etc.)
        if "price" in data:
            try:
                cleaned["price"] = self._extract_numeric_price(data["price"])
            except (ValueError, TypeError):
                logger.warning(f"Could not parse price: {data.get('price')}")
                cleaned["price"] = None
                cleaned["price_raw"] = data.get("price")
        
        # Handle other fields
        standard_fields = [
            "title", "description", "address", "size", "rooms", 
            "bathrooms", "location", "coordinates", "images"
        ]
        
        for field in standard_fields:
            if field in data:
                cleaned[field] = data[field]
        
        # Add any other fields as raw data
        for key, value in data.items():
            if key not in cleaned and key not in ["url", "price"]:
                cleaned[f"raw_{key}"] = value
        
        return cleaned
    
    def save_results(self, filepath: str = None) -> None:
        """
        Save scraped results to a JSON file.
        
        Args:
            filepath: Path to save the JSON file, defaults to 'data/{name}_{timestamp}.json'
        """
        if not filepath:
            timestamp = int(time.time())
            filepath = f"data/{self.name}_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.results)} results to {filepath}")
    
    def _extract_numeric_price(self, price_str: str) -> Optional[int]:
        """
        Extract numeric price from a string.
        
        Args:
            price_str: Price string (e.g., '¥50,000,000', '5000万円')
            
        Returns:
            Numeric price in JPY
        """
        import re
        
        # Remove currency symbols, commas, spaces
        numeric_str = re.sub(r'[^\d.]', '', price_str)
        
        # Check if it's empty after cleaning
        if not numeric_str:
            return None
        
        # Convert to int if possible
        try:
            return int(float(numeric_str))
        except ValueError:
            # If conversion fails, return None
            return None
    
    def _format_listing_for_db(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a listing for insertion into the database.
        
        Args:
            listing: Property listing data
            
        Returns:
            Formatted data ready for database insertion
        """
        # Convert data types as needed for the database
        formatted = dict(listing)
        
        # Handle timestamps
        for field in ["scraped_at", "created_at", "updated_at"]:
            if field in formatted and isinstance(formatted[field], str):
                formatted[field] = formatted[field]  # Keep ISO format for Supabase
        
        # Handle JSON fields
        json_fields = ["images", "features", "details", "raw_data"]
        for field in json_fields:
            if field in formatted and not isinstance(formatted[field], str):
                formatted[field] = json.dumps(formatted[field])
        
        return formatted
