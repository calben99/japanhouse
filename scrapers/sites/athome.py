"""
AtHome Scraper

Scrapes property listings from AtHome (https://www.athome.co.jp), one of Japan's major
property listing websites.
"""
import re
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup
from loguru import logger

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from common.base_scraper import BaseScraper
from common.http_utils import RequestsSession, get_html


class AtHomeScraper(BaseScraper):
    """Scraper for AtHome property listings."""
    
    def __init__(self):
        """Initialize the AtHome scraper."""
        super().__init__(name="athome", base_url="https://www.athome.co.jp")
        self.session = RequestsSession()
    
    def scrape(self, location: str = "tokyo", property_type: str = "rent", 
               max_pages: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape AtHome property listings.
        
        Args:
            location: Location to search for (e.g., "tokyo", "osaka")
            property_type: Type of property listing ("rent" or "buy")
            max_pages: Maximum number of pages to scrape
            **kwargs: Additional search parameters
            
        Returns:
            List of property listings
        """
        self.results = []
        
        # Build the URL based on location and property type
        property_type_path = "chintai" if property_type.lower() == "rent" else "kodate"
        
        # Map common location names to their AtHome URL path
        location_map = {
            "tokyo": "tokyo",
            "osaka": "osaka",
            "kyoto": "kyoto",
            "yokohama": "kanagawa/yokohamashi",
            "nagoya": "aichi/nagoyashi",
            "sapporo": "hokkaido/sapporoshi",
            "fukuoka": "fukuoka/fukuokashi",
            "kobe": "hyogo/kobeshi",
            "okayama": "okayama"
        }
        
        # Default to tokyo if location not in map
        location_path = location_map.get(location.lower(), "tokyo")
        
        # Build the URL with the correct location and property type
        url = f"https://www.athome.co.jp/{property_type_path}/{location_path}/list/"
        
        # Add additional parameters if provided
        if kwargs:
            url += "?"
            params = []
            for key, value in kwargs.items():
                params.append(f"{key}={value}")
            url += "&".join(params)
        
        # Scrape multiple pages
        page_count = 0
        next_page_url = url
        
        while next_page_url and page_count < max_pages:
            logger.info(f"Scraping AtHome page {page_count + 1}: {next_page_url}")
            
            try:
                # Get the HTML content
                html = get_html(next_page_url, session=self.session)
                
                # Extract property listings
                listings = self._extract_listings(html, property_type)
                self.results.extend(listings)
                
                # Find the next page URL
                next_page_url = self._get_next_page_url(html)
                
                # Increment the page counter
                page_count += 1
                
            except Exception as e:
                logger.error(f"Error scraping AtHome page {page_count + 1}: {str(e)}")
                break
        
        logger.info(f"Scraped {len(self.results)} AtHome property listings")
        
        return self.results
    
    def _extract_listings(self, html: str, property_type: str) -> List[Dict[str, Any]]:
        """
        Extract property listings from HTML.
        
        Args:
            html: HTML content to parse
            property_type: Type of property listing ("rent" or "buy")
            
        Returns:
            List of property listings
        """
        soup = BeautifulSoup(html, 'html.parser')
        listings = []
        
        # Common selector for both rental and sale properties
        listing_elements = soup.select('.property-object')
        
        for element in listing_elements:
            try:
                listing_data = {}
                
                # Get the property URL
                url_element = element.select_one('.property-object-title a')
                if url_element and 'href' in url_element.attrs:
                    listing_data["url"] = urljoin(self.base_url, url_element['href'])
                else:
                    listing_data["url"] = None
                
                # Get the property title
                if url_element:
                    listing_data["title"] = url_element.text.strip()
                
                # Get the property price
                price_element = element.select_one('.property-object-price')
                if price_element:
                    listing_data["price"] = price_element.text.strip()
                
                # Get the location
                location_element = element.select_one('.property-object-place')
                if location_element:
                    listing_data["location"] = location_element.text.strip()
                
                # Get the station and access information
                access_elements = element.select('.property-object-access')
                if access_elements:
                    access_info = [access.text.strip() for access in access_elements]
                    listing_data["access"] = " / ".join(access_info)
                
                # Get property details
                detail_items = element.select('.property-object-detail li')
                for item in detail_items:
                    label_element = item.select_one('.object-label')
                    value_element = item.select_one('.object-value')
                    
                    if label_element and value_element:
                        label = label_element.text.strip().rstrip('：')
                        value = value_element.text.strip()
                        
                        # Map common Japanese terms to English keys
                        if "間取" in label:  # Floor plan
                            listing_data["layout"] = value
                        elif "面積" in label:  # Area
                            listing_data["size"] = value
                        elif "築年" in label:  # Year built
                            listing_data["year_built"] = value
                        elif "階数" in label:  # Floor
                            listing_data["floor"] = value
                        elif "構造" in label:  # Structure
                            listing_data["structure"] = value
                        elif "方角" in label:  # Direction
                            listing_data["direction"] = value
                        else:
                            # Use raw Japanese label for other fields
                            listing_data[f"raw_{label}"] = value
                
                # Get property features
                features_elements = element.select('.property-object-tag li')
                features = [feature.text.strip() for feature in features_elements]
                if features:
                    listing_data["features"] = features
                
                # Get property images
                image_elements = element.select('.property-object-thumb img')
                listing_data["images"] = []
                for img in image_elements:
                    if 'src' in img.attrs and not img['src'].endswith('blank.png'):
                        listing_data["images"].append(img['src'])
                    elif 'data-src' in img.attrs:
                        listing_data["images"].append(img['data-src'])
                
                # Clean and standardize the data
                cleaned_data = self.clean_data(listing_data)
                listings.append(cleaned_data)
            
            except Exception as e:
                logger.error(f"Error extracting AtHome listing: {str(e)}")
                continue
        
        return listings
    
    def _get_next_page_url(self, html: str) -> Optional[str]:
        """
        Get the URL of the next page from the HTML.
        
        Args:
            html: HTML content to parse
            
        Returns:
            URL of the next page or None if there is no next page
        """
        soup = BeautifulSoup(html, 'html.parser')
        next_button = soup.select_one('li.next:not(.disabled) a')
        
        if next_button and 'href' in next_button.attrs:
            return urljoin(self.base_url, next_button['href'])
        
        return None
    
    def _get_location_code(self, location: str) -> str:
        """
        Get the location code used by AtHome for a given location.
        
        Args:
            location: Location name in English (e.g., "tokyo", "osaka")
            
        Returns:
            Location code used by AtHome
        """
        # Mapping of English location names to AtHome location codes
        location_map = {
            "tokyo": "tokyo",
            "kanagawa": "kanagawa",
            "saitama": "saitama",
            "chiba": "chiba",
            "osaka": "osaka",
            "kyoto": "kyoto",
            "hyogo": "hyogo",
            "aichi": "aichi",
            "fukuoka": "fukuoka",
            "hokkaido": "hokkaido",
        }
        
        return location_map.get(location.lower(), "tokyo")  # Default to Tokyo if unknown
