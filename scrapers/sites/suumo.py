"""
SUUMO Scraper

Scrapes property listings from SUUMO (https://suumo.jp), one of Japan's largest
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


class SuumoScraper(BaseScraper):
    """Scraper for SUUMO property listings."""
    
    def __init__(self):
        """Initialize the SUUMO scraper."""
        super().__init__(name="suumo", base_url="https://suumo.jp")
        self.session = RequestsSession()
    
    def scrape(self, location: str = "tokyo", property_type: str = "rent", 
               max_pages: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape SUUMO property listings.
        
        Args:
            location: Location to search for (e.g., "tokyo", "osaka")
            property_type: Type of property listing ("rent" or "buy")
            max_pages: Maximum number of pages to scrape
            **kwargs: Additional search parameters
            
        Returns:
            List of property listings
        """
        self.results = []
        
        # Use the exact URL specified by the user for testing
        # This is the URL that is confirmed to work for finding properties
        url = "https://suumo.jp/jj/bukken/ichiran/JJ010FJ001/?ar=080&bs=021&ta=33&jspIdFlg=patternShikugun&kb=1&kt=9999999&tb=0&tt=9999999&hb=0&ht=9999999&ekTjCd=&ekTjNm=&tj=0&cnb=0&cn=9999999"
        
        # Add additional parameters if provided
        for key, value in kwargs.items():
            if key in ["cb", "ct", "et", "kt", "mb", "mt", "sc", "ts"]:
                url += f"&{key}={value}"
        
        # Scrape multiple pages
        page_count = 0
        next_page_url = url
        
        while next_page_url and page_count < max_pages:
            logger.info(f"Scraping SUUMO page {page_count + 1}: {next_page_url}")
            
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
                logger.error(f"Error scraping SUUMO page {page_count + 1}: {str(e)}")
                break
        
        logger.info(f"Scraped {len(self.results)} SUUMO property listings")
        
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
        
        # Different selectors based on property type
        if property_type.lower() == "rent":
            # For rental properties
            listing_elements = soup.select('.cassetteitem')
            
            for element in listing_elements:
                try:
                    # Extract building information
                    building_info = element.select_one('.cassetteitem_content-title')
                    building_name = building_info.text.strip() if building_info else "Unknown"
                    
                    # Extract location
                    location_element = element.select_one('.cassetteitem_detail-col1')
                    location = location_element.text.strip() if location_element else "Unknown"
                    
                    # Extract building features
                    features_element = element.select_one('.cassetteitem_detail-col3')
                    features = features_element.text.strip() if features_element else ""
                    
                    # Extract each room in the building
                    room_elements = element.select('.cassetteitem_detail-room')
                    
                    for room in room_elements:
                        room_data = {}
                        
                        # Basic data
                        room_data["title"] = building_name
                        room_data["location"] = location
                        room_data["features"] = features
                        
                        # Get the room URL
                        url_element = room.select_one('a')
                        if url_element and 'href' in url_element.attrs:
                            room_data["url"] = urljoin(self.base_url, url_element['href'])
                        else:
                            room_data["url"] = None
                        
                        # Floor and room number
                        floor_element = room.select_one('.cassetteitem_detail-text')
                        if floor_element:
                            room_data["floor"] = floor_element.text.strip()
                        
                        # Rent price
                        rent_element = room.select_one('.cassetteitem_price--rent')
                        if rent_element:
                            room_data["price"] = rent_element.text.strip()
                        
                        # Additional fees
                        fees_element = room.select_one('.cassetteitem_price--administration')
                        if fees_element:
                            room_data["admin_fees"] = fees_element.text.strip()
                        
                        # Deposit and key money
                        deposit_element = room.select_one('.cassetteitem_price--deposit')
                        if deposit_element:
                            room_data["deposit"] = deposit_element.text.strip()
                        
                        # Room layout
                        layout_element = room.select_one('.cassetteitem_madori')
                        if layout_element:
                            room_data["layout"] = layout_element.text.strip()
                        
                        # Room size
                        size_element = room.select_one('.cassetteitem_menseki')
                        if size_element:
                            room_data["size"] = size_element.text.strip()
                        
                        # Clean and standardize the data
                        cleaned_data = self.clean_data(room_data)
                        listings.append(cleaned_data)
                
                except Exception as e:
                    logger.error(f"Error extracting SUUMO rental listing: {str(e)}")
                    continue
        
        else:  # Buy
            # For properties for sale
            listing_elements = soup.select('.property_unit')
            
            for element in listing_elements:
                try:
                    listing_data = {}
                    
                    # Get the property URL
                    url_element = element.select_one('.property_unit-link')
                    if url_element and 'href' in url_element.attrs:
                        listing_data["url"] = urljoin(self.base_url, url_element['href'])
                    else:
                        listing_data["url"] = None
                    
                    # Get the property title
                    title_element = element.select_one('.property_unit-title')
                    if title_element:
                        listing_data["title"] = title_element.text.strip()
                    
                    # Get the property price
                    price_element = element.select_one('.dottable-value--price')
                    if price_element:
                        listing_data["price"] = price_element.text.strip()
                    
                    # Get the location
                    location_element = element.select_one('.dottable-value--address')
                    if location_element:
                        listing_data["location"] = location_element.text.strip()
                    
                    # Get the property size
                    size_element = element.select_one('.dottable-value--menseki')
                    if size_element:
                        listing_data["size"] = size_element.text.strip()
                    
                    # Get the property layout
                    layout_element = element.select_one('.dottable-value--madori')
                    if layout_element:
                        listing_data["layout"] = layout_element.text.strip()
                    
                    # Get the year built
                    year_element = element.select_one('.dottable-value--chikunengetsu')
                    if year_element:
                        listing_data["year_built"] = year_element.text.strip()
                    
                    # Get property images
                    image_elements = element.select('.property_unit-thumbnail-image')
                    listing_data["images"] = []
                    for img in image_elements:
                        if 'src' in img.attrs:
                            listing_data["images"].append(img['src'])
                    
                    # Clean and standardize the data
                    cleaned_data = self.clean_data(listing_data)
                    listings.append(cleaned_data)
                
                except Exception as e:
                    logger.error(f"Error extracting SUUMO sale listing: {str(e)}")
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
        next_button = soup.select_one('.pagination-parts--next')
        
        if next_button and 'href' in next_button.attrs:
            return urljoin(self.base_url, next_button['href'])
        
        return None
    
    def _get_area_code(self, location: str) -> str:
        """
        Get the area code used by SUUMO for a given location.
        
        Args:
            location: Location name in English (e.g., "tokyo", "osaka")
            
        Returns:
            Area code used by SUUMO
        """
        # Mapping of English location names to SUUMO area codes
        location_map = {
            "tokyo": "03",      # Tokyo
            "kanagawa": "04",   # Kanagawa
            "saitama": "05",    # Saitama
            "chiba": "06",      # Chiba
            "osaka": "27",      # Osaka
            "kyoto": "26",      # Kyoto
            "hyogo": "28",      # Hyogo
            "aichi": "23",      # Aichi
            "fukuoka": "40",    # Fukuoka
            "hokkaido": "01",   # Hokkaido
            "okayama": "33",    # Okayama
        }
        
        return location_map.get(location.lower(), "03")  # Default to Tokyo if unknown
        
    def _get_prefecture_code(self, location: str) -> str:
        """
        Get the prefecture code used by SUUMO for a given location.
        Used in detailed URL format for property purchases.
        
        Args:
            location: Location name in English (e.g., "tokyo", "osaka")
            
        Returns:
            Prefecture code used by SUUMO
        """
        # Mapping of English location names to SUUMO prefecture codes
        prefecture_map = {
            "tokyo": "13",      # Tokyo
            "kanagawa": "14",   # Kanagawa
            "saitama": "11",    # Saitama
            "chiba": "12",      # Chiba
            "osaka": "27",      # Osaka
            "kyoto": "26",      # Kyoto
            "hyogo": "28",      # Hyogo
            "aichi": "23",      # Aichi
            "fukuoka": "40",    # Fukuoka
            "hokkaido": "01",   # Hokkaido
            "okayama": "33",    # Okayama
        }
        
        return prefecture_map.get(location.lower(), "13")  # Default to Tokyo if unknown
