"""
Akiya-Mart Scraper

Scrapes property listings from Akiya-Mart (https://www.akiya-mart.com/), a site
specializing in abandoned houses and other Japanese real estate listings.
"""
import re
import json
import asyncio
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import async_playwright, Page

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from common.base_scraper import BaseScraper


class AkiyaMartScraper(BaseScraper):
    """Scraper for Akiya-Mart property listings, specializing in abandoned houses."""
    
    def __init__(self):
        """Initialize the Akiya-Mart scraper."""
        super().__init__(name="akiyamart", base_url="https://www.akiya-mart.com")
    
    def scrape(self, location: str = "tokyo", property_type: str = "all", 
               max_pages: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape Akiya-Mart property listings.
        
        Args:
            location: Location to search for (e.g., "tokyo", "osaka")
            property_type: Type of property listing ("all", "akiya", "land", etc.)
            max_pages: Maximum number of pages to scrape
            **kwargs: Additional search parameters
            
        Returns:
            List of property listings
        """
        self.results = []
        
        # Run the async scraper through an event loop
        asyncio.run(self._async_scrape(location, property_type, max_pages, **kwargs))
        
        logger.info(f"Scraped {len(self.results)} Akiya-Mart property listings")
        
        return self.results
    
    async def _async_scrape(self, location: str, property_type: str, 
                           max_pages: int, **kwargs) -> None:
        """
        Asynchronously scrape Akiya-Mart property listings using Playwright.
        
        Args:
            location: Location to search for
            property_type: Type of property listing
            max_pages: Maximum number of pages to scrape
            **kwargs: Additional search parameters
        """
        # Construct the search URL
        # Use the main search page of Akiya-Mart
        search_url = f"{self.base_url}/"
        
        # We'll interact with the search form on the page to find properties by location
        logger.info(f"Using main Akiya-Mart site and will search for location: {location}")
        
        # Add additional parameters if provided
        for key, value in kwargs.items():
            search_url += f"&{key}={value}"
        
        logger.info(f"Starting Akiya-Mart scraper with URL: {search_url}")
        
        # Initialize Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            
            try:
                # Navigate to the search page with longer timeout
                logger.info(f"Navigating to {search_url}")
                await page.goto(search_url, wait_until="networkidle", timeout=60000)
                
                # Take a screenshot for debugging
                screenshot_path = "akiyamart_initial_page.png"
                await page.screenshot(path=screenshot_path)
                logger.info(f"Saved initial page screenshot to {screenshot_path}")
                
                # Add a small delay to ensure page is fully loaded
                await page.wait_for_timeout(3000)
                
                # For Akiya-Mart, we need to directly try known URL patterns that might work
                # since the site structure can vary
                try:
                    # Try these specific URLs for Okayama properties on Akiya-Mart
                    possible_urls = [
                        "https://www.akiya-mart.com/akiyabank/prefecture/33",  # Direct Okayama prefecture code (33)
                        "https://www.akiya-mart.com/bukken/search/prefecture/33",  # Another possible pattern
                        "https://www.akiya-mart.com/bukken/search?prefecture=33",  # Query parameter style
                        "https://www.akiya-mart.com/akiyabank/search?prefecture=%E5%B2%A1%E5%B1%B1",  # Japanese name (Okayama)
                        "https://www.akiya-mart.com/bukken/search?keyword=%E5%B2%A1%E5%B1%B1"  # Keyword search for Okayama
                    ]
                    
                    # Try each URL pattern
                    for url in possible_urls:
                        try:
                            logger.info(f"Trying direct navigation to: {url}")
                            await page.goto(url, wait_until="networkidle", timeout=30000)
                            
                            # Take a screenshot after each navigation attempt
                            screenshot_path = f"akiyamart_{url.split('/')[-1]}.png"
                            await page.screenshot(path=screenshot_path)
                            logger.info(f"Saved screenshot for {url} to {screenshot_path}")
                            
                            # Check if we found any properties using various possible selectors
                            property_selectors = [
                                ".property-card", ".property-item", ".card", "article", ".bukken-item", ".search-result-item",
                                ".akiya-card", ".property", ".listing", ".estate-item", ".bukken-card", ".bukken"
                            ]
                            
                            has_properties = False
                            found_selector = None
                            
                            for selector in property_selectors:
                                elements = await page.query_selector_all(selector)
                                if elements and len(elements) > 0:
                                    logger.info(f"Found {len(elements)} property listings with selector '{selector}' at URL: {url}")
                                    has_properties = True
                                    found_selector = selector
                                    break
                                    
                            if has_properties:
                                # We found property listings, so break the URL loop and continue with extraction
                                logger.info(f"Moving to extract listings using selector: {found_selector}")
                                break
                        except Exception as e:
                            logger.error(f"Error navigating to {url}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error trying direct URL navigation: {str(e)}")
                
                # Take another screenshot after search to help with debugging
                screenshot_path = "akiyamart_after_search.png"
                await page.screenshot(path=screenshot_path)
                logger.info(f"Saved post-search screenshot to {screenshot_path}")
                
                # Dump HTML for debugging
                html = await page.content()
                logger.info(f"Page HTML length: {len(html)}")
                
                # Scrape multiple pages
                page_count = 0
                
                while page_count < max_pages:
                    logger.info(f"Scraping Akiya-Mart page {page_count + 1}")
                    
                    try:
                        # Try different selectors that might contain property listings
                        # with increased timeout (30 seconds)
                        selectors = [
                            ".property-card", ".property-item", ".property", 
                            ".card", ".listing-card", "article", ".estate-card",
                            ".property-listing", ".listing", ".search-result-item"
                        ]
                        
                        found_selector = False
                        for selector in selectors:
                            if await page.query_selector(selector):
                                logger.info(f"Found property elements with selector: {selector}")
                                found_selector = True
                                
                                # Extract property listings using the discovered selector
                                listings = await self._extract_listings(page, selector)
                                if listings:
                                    self.results.extend(listings)
                                    break
                        
                        if not found_selector:
                            # If no known selectors match, try to extract data from any page elements
                            logger.warning("No standard property card selectors found, attempting generic extraction")
                            listings = await self._generic_extract(page)
                            if listings:
                                self.results.extend(listings)
                        
                        # Check if there's a next page button using various selectors
                        next_selectors = [
                            '.pagination-next:not(.disabled)', '.next', '.next-page', 
                            'a[rel="next"]', 'a.next', 'li.next a', 
                            '.pagination .active + li a'
                        ]
                        
                        next_button = None
                        for selector in next_selectors:
                            next_button = await page.query_selector(selector)
                            if next_button:
                                logger.info(f"Found next page button with selector: {selector}")
                                break
                        
                        if next_button:
                            # Click the next page button
                            await next_button.click()
                            # Wait for the page to load
                            await page.wait_for_load_state("networkidle", timeout=30000)
                            page_count += 1
                        else:
                            # No more pages
                            logger.info("No next page button found, ending pagination")
                            break
                            
                    except Exception as e:
                        logger.error(f"Error scraping Akiya-Mart page {page_count + 1}: {str(e)}")
                        # Continue to the next page instead of breaking completely
                        page_count += 1
                        continue
            except Exception as e:
                logger.error(f"Error in main scraper flow: {str(e)}")
            finally:
                # Always close the browser
                await browser.close()
    
    async def _extract_listings(self, page: Page, selector: str = '.property-card') -> List[Dict[str, Any]]:
        """
        Extract property listings from the current page using the specified selector.
        
        Args:
            page: Playwright page object
            selector: CSS selector for property card elements
            
        Returns:
            List of property listings
        """
        listings = []
        
        # Get the HTML content of the page
        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all property cards on the page using the provided selector
        property_cards = soup.select(selector)
        logger.info(f"Found {len(property_cards)} property items with selector '{selector}'")
        
        # Common class names for different elements
        title_selectors = ['.property-title', '.listing-title', 'h2', 'h3', '.title']
        price_selectors = ['.property-price', '.price', '.listing-price', '.cost']
        location_selectors = ['.property-location', '.location', '.address', '.listing-address']
        details_selectors = ['.property-details', '.details', '.specs', '.information']
        link_selectors = ['a', 'a.property-link', '.listing-link', '.card-link']
        image_selectors = ['.property-image img', 'img', '.thumbnail img', '.photo img']
        
        for card in property_cards:
            try:
                listing_data = {}
                
                # Extract the title using multiple possible selectors
                for title_selector in title_selectors:
                    title_element = card.select_one(title_selector)
                    if title_element and title_element.text.strip():
                        listing_data["title"] = title_element.text.strip()
                        break
                
                # Extract the price using multiple possible selectors
                for price_selector in price_selectors:
                    price_element = card.select_one(price_selector)
                    if price_element and price_element.text.strip():
                        listing_data["price"] = price_element.text.strip()
                        break
                
                # Extract the location using multiple possible selectors
                for location_selector in location_selectors:
                    location_element = card.select_one(location_selector)
                    if location_element and location_element.text.strip():
                        listing_data["location"] = location_element.text.strip()
                        break
                
                # Extract property details
                for details_selector in details_selectors:
                    details_element = card.select_one(details_selector)
                    if details_element:
                        # Look for size, rooms, etc. in the details
                        size_candidates = ['.property-size', '.size', '.sqm', '.area']
                        rooms_candidates = ['.property-rooms', '.rooms', '.bedroom-count']
                        
                        for size_selector in size_candidates:
                            size_element = details_element.select_one(size_selector)
                            if size_element and size_element.text.strip():
                                listing_data["size"] = size_element.text.strip()
                                break
                        
                        for room_selector in rooms_candidates:
                            rooms_element = details_element.select_one(room_selector)
                            if rooms_element and rooms_element.text.strip():
                                listing_data["rooms"] = rooms_element.text.strip()
                                break
                        break
                
                # Extract the URL
                for link_selector in link_selectors:
                    link_element = card.select_one(link_selector)
                    if link_element and 'href' in link_element.attrs:
                        listing_data["url"] = urljoin(self.base_url, link_element['href'])
                        break
                
                # Extract any images
                for image_selector in image_selectors:
                    image_elements = card.select(image_selector)
                    if image_elements:
                        listing_data["images"] = [img.get('src', img.get('data-src', '')) 
                                              for img in image_elements 
                                              if img.get('src') or img.get('data-src')]
                        break
                
                # Only add listings with at least some meaningful data
                if listing_data.get("title") or listing_data.get("price") or listing_data.get("location"):
                    # Clean and standardize the data
                    cleaned_data = self.clean_data(listing_data)
                    listings.append(cleaned_data)
                    logger.debug(f"Extracted listing: {cleaned_data.get('title', 'Untitled')}")
                
            except Exception as e:
                logger.error(f"Error extracting Akiya-Mart listing: {str(e)}")
                continue
        
        return listings
        
    async def _generic_extract(self, page: Page) -> List[Dict[str, Any]]:
        """
        Attempt a more generic extraction when standard selectors fail.
        This is a fallback method that looks for common patterns in the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of property listings
        """
        listings = []
        
        try:
            # Get the HTML content of the page
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try to find all articles, divs that might be cards, or other common containers
            potential_listings = []
            
            # Look for articles
            articles = soup.find_all('article')
            if articles:
                potential_listings.extend(articles)
            
            # Look for divs with card-like classes
            card_like_divs = soup.select('div[class*="card"], div[class*="item"], div[class*="listing"], div[class*="property"]')
            if card_like_divs:
                potential_listings.extend(card_like_divs)
            
            # Look for sections with property content
            sections = soup.select('section[class*="property"], section[class*="listing"], section[class*="result"]')
            if sections:
                potential_listings.extend(sections)
            
            logger.info(f"Found {len(potential_listings)} potential generic listings")
            
            for item in potential_listings:
                try:
                    listing_data = {}
                    
                    # Try to determine if this is a property listing
                    # by checking for key elements like price, address, or property-related terms
                    
                    # Get all text in the item
                    all_text = item.get_text(separator=' ', strip=True).lower()
                    
                    # Keywords that suggest this might be a property listing
                    property_keywords = ['property', 'house', 'land', 'estate', 'akiya', 'home', 
                                         'price', 'yen', '円', '万円', 'sqm', 'm²', 'acre']
                    
                    is_property = False
                    for keyword in property_keywords:
                        if keyword in all_text:
                            is_property = True
                            break
                    
                    if not is_property:
                        continue
                    
                    # Find a title - any heading or strong text
                    headings = item.select('h1, h2, h3, h4, strong, b, .title')
                    if headings:
                        listing_data["title"] = headings[0].get_text(strip=True)
                    
                    # Find a price - look for yen symbols, numbers with commas, etc.
                    price_patterns = [
                        r'\d{1,3}(?:,\d{3})+円', 
                        r'\d+万円', 
                        r'\d+\.\d+万円',
                        r'¥\s*\d+(?:,\d{3})*'
                    ]
                    
                    for pattern in price_patterns:
                        price_match = re.search(pattern, all_text)
                        if price_match:
                            listing_data["price"] = price_match.group(0)
                            break
                    
                    # Find location/address - look for prefecture names or address patterns
                    prefectures = ['hokkaido', 'aomori', 'iwate', 'miyagi', 'akita', 'yamagata', 'fukushima',
                                  'ibaraki', 'tochigi', 'gunma', 'saitama', 'chiba', 'tokyo', 'kanagawa',
                                  'niigata', 'toyama', 'ishikawa', 'fukui', 'yamanashi', 'nagano', 'gifu',
                                  'shizuoka', 'aichi', 'mie', 'shiga', 'kyoto', 'osaka', 'hyogo', 'nara',
                                  'wakayama', 'tottori', 'shimane', 'okayama', 'hiroshima', 'yamaguchi',
                                  'tokushima', 'kagawa', 'ehime', 'kochi', 'fukuoka', 'saga', 'nagasaki',
                                  'kumamoto', 'oita', 'miyazaki', 'kagoshima', 'okinawa']
                    
                    for prefecture in prefectures:
                        if prefecture in all_text:
                            # Find the sentence or element containing this prefecture
                            paragraphs = item.find_all(['p', 'div', 'span'])
                            for p in paragraphs:
                                p_text = p.get_text(strip=True).lower()
                                if prefecture in p_text and len(p_text) < 100:  # Not too long
                                    listing_data["location"] = p.get_text(strip=True)
                                    break
                            if "location" not in listing_data:
                                # If we couldn't find a specific element, just extract the context
                                location_match = re.search(f"[^.\n]*{prefecture}[^.\n]*", all_text)
                                if location_match:
                                    listing_data["location"] = location_match.group(0)
                            break
                    
                    # Find the URL
                    link = item.find('a')
                    if link and 'href' in link.attrs:
                        listing_data["url"] = urljoin(self.base_url, link['href'])
                    
                    # Find images
                    images = item.find_all('img')
                    if images:
                        listing_data["images"] = []
                        for img in images:
                            src = img.get('src') or img.get('data-src')
                            if src:
                                listing_data["images"].append(src)
                    
                    # Only add if we have some meaningful data
                    if listing_data.get("title") or listing_data.get("price") or listing_data.get("location"):
                        cleaned_data = self.clean_data(listing_data)
                        listings.append(cleaned_data)
                        logger.debug(f"Extracted generic listing: {cleaned_data.get('title', 'Untitled')}")
                        
                except Exception as e:
                    logger.error(f"Error extracting generic listing: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in generic extraction: {str(e)}")
        
        return listings
