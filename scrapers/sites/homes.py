"""
HOMES Scraper

Scrapes property listings from HOMES (https://www.homes.co.jp), one of Japan's major
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


class HomesScraper(BaseScraper):
    """Scraper for HOMES property listings."""
    
    def __init__(self):
        """Initialize the HOMES scraper."""
        super().__init__(name="homes", base_url="https://www.homes.co.jp")
        self.session = RequestsSession()
    
    def scrape(self, location: str = "tokyo", property_type: str = "rent", 
               max_pages: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape HOMES property listings.
        
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
        url = "https://www.homes.co.jp/kodate/chuko/okayama/list/"
        
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
            logger.info(f"Scraping HOMES page {page_count + 1}: {next_page_url}")
            
            try:
                # Get the HTML content
                html = get_html(next_page_url, session=self.session)
                
                # Save the HTML for debugging
                with open(f"homes_page_{page_count + 1}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info(f"Saved HTML content to homes_page_{page_count + 1}.html for debugging")
                
                # Extract property listings
                listings = self._extract_listings(html, property_type)
                
                # If we didn't find any listings, try a fallback method
                if not listings:
                    logger.info("No listings found with standard extraction, trying fallback method")
                    fallback_listings = self._fallback_extract_listings(html, property_type)
                    listings = fallback_listings
                    logger.info(f"Fallback method found {len(fallback_listings)} listings")
                
                self.results.extend(listings)
                
                # Find the next page URL
                next_page_url = self._get_next_page_url(html)
                
                # Increment the page counter
                page_count += 1
                
            except Exception as e:
                logger.error(f"Error scraping HOMES page {page_count + 1}: {str(e)}")
                break
        
        logger.info(f"Scraped {len(self.results)} HOMES property listings")
        
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
        
        # Log the title of the page for debugging
        title_element = soup.select_one('title')
        if title_element:
            logger.info(f"Page title: {title_element.text.strip()}")
        
        # Try multiple selectors for property listings
        # These are different possible selectors that might contain property listings
        property_selectors = [
            '.moduleInner.property',  # Original selector
            '.property-item',         # Alternative selector
            '.property-card',         # Another common pattern
            '.object-item',           # Another possibility
            'article.property',       # Yet another possibility
            '.property-list-item',    # Another selector format
            '.bukken-cassette',       # Japanese property listing format
            '.cassette',              # Simpler selector that might match
            '.itembox'                # Common item container
        ]
        
        # Try each selector and use the first one that returns results
        listing_elements = []
        found_selector = None
        
        for selector in property_selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 0:
                listing_elements = elements
                found_selector = selector
                logger.info(f"Found {len(elements)} property listings using selector: {selector}")
                break
        
        if not listing_elements:
            logger.warning("Could not find any property listings using standard selectors")
            
            # As a last resort, look for any elements that might contain property information
            # by searching for common property-related text
            price_elements = soup.find_all(string=re.compile(r'\d+万円'))
            if price_elements:
                logger.info(f"Found {len(price_elements)} elements with price information")
                
            # Log some of the HTML structure for debugging
            body = soup.select_one('body')
            if body:
                main_divs = body.select('div[id], div[class]')
                logger.info(f"Found {len(main_divs)} main div elements on the page")
                for i, div in enumerate(main_divs[:5]):  # Log the first 5 main divs
                    div_id = div.get('id', '')
                    div_class = div.get('class', [])
                    logger.info(f"Main div {i+1}: id='{div_id}', class='{' '.join(div_class)}'")
        
        # Different processing based on property type
        if property_type.lower() == "rent":
            # For rental properties
            
            for element in listing_elements:
                try:
                    listing_data = {}
                    
                    # Get the property URL
                    url_element = element.select_one('h2.devMansionTitle a')
                    if url_element and 'href' in url_element.attrs:
                        listing_data["url"] = urljoin(self.base_url, url_element['href'])
                    else:
                        listing_data["url"] = None
                    
                    # Get the property title
                    if url_element:
                        listing_data["title"] = url_element.text.strip()
                    
                    # Get the property price
                    price_element = element.select_one('.priceLabel')
                    if price_element:
                        listing_data["price"] = price_element.text.strip()
                    
                    # Get initial fees if available
                    fees_element = element.select_one('.initialLabel')
                    if fees_element:
                        listing_data["initial_fees"] = fees_element.text.strip()
                    
                    # Get the location
                    location_element = element.select_one('.abAddress')
                    if location_element:
                        listing_data["location"] = location_element.text.strip()
                    
                    # Get the station and access information
                    access_element = element.select_one('.abAccess')
                    if access_element:
                        listing_data["access"] = access_element.text.strip()
                    
                    # Get room layout
                    layout_element = element.select_one('.madoriInfo')
                    if layout_element:
                        listing_data["layout"] = layout_element.text.strip()
                    
                    # Get room size
                    size_element = element.select_one('.areaInfo')
                    if size_element:
                        listing_data["size"] = size_element.text.strip()
                    
                    # Get property features
                    features_elements = element.select('ul.articleTagList li')
                    features = [feature.text.strip() for feature in features_elements]
                    if features:
                        listing_data["features"] = features
                    
                    # Get property URL for fetching high-res images later
                    detail_url = None
                    url_element = element.select_one('a[href*="detail"]')
                    if url_element and 'href' in url_element.attrs:
                        detail_url = urljoin(self.base_url, url_element['href'])
                        listing_data["detail_url"] = detail_url
                    
                    # Still get thumbnail images as fallback
                    image_elements = element.select('.mainvisual img')
                    listing_data["images"] = []
                    for img in image_elements:
                        if 'data-src' in img.attrs:
                            img_src = img['data-src']
                            # Skip loading images or icons
                            if not (img_src.endswith('.gif') or 'loading' in img_src or 'icon' in img_src):
                                listing_data["images"].append(img_src)
                        elif 'src' in img.attrs and not (img['src'].endswith('blank.png') or '.gif' in img['src'] or 'loading' in img['src'] or 'icon' in img['src']):
                            listing_data["images"].append(img['src'])
                    
                    # Fetch high-resolution images from detail page if available
                    if detail_url:
                        try:
                            high_res_images = self._fetch_high_res_images(detail_url)
                            if high_res_images:
                                listing_data["images"] = high_res_images
                        except Exception as e:
                            logger.error(f"Error fetching high-res images from {detail_url}: {str(e)}")
                    
                    # Clean and standardize the data
                    cleaned_data = self.clean_data(listing_data)
                    listings.append(cleaned_data)
                
                except Exception as e:
                    logger.error(f"Error extracting HOMES rental listing: {str(e)}")
                    continue
        
        else:  # Buy
            # The listing_elements variable is already set by the selector search above
            
            for element in listing_elements:
                try:
                    listing_data = {}
                    
                    # Get the property URL
                    url_element = element.select_one('h2.devMansionTitle a')
                    if url_element and 'href' in url_element.attrs:
                        listing_data["url"] = urljoin(self.base_url, url_element['href'])
                    else:
                        listing_data["url"] = None
                    
                    # Get the property title
                    if url_element:
                        listing_data["title"] = url_element.text.strip()
                    
                    # Get the property price
                    price_element = element.select_one('.priceLabel')
                    if price_element:
                        listing_data["price"] = price_element.text.strip()
                    
                    # Get the location
                    location_element = element.select_one('.abAddress')
                    if location_element:
                        listing_data["location"] = location_element.text.strip()
                    
                    # Get the station and access information
                    access_element = element.select_one('.abAccess')
                    if access_element:
                        listing_data["access"] = access_element.text.strip()
                    
                    # Get property layout
                    layout_element = element.select_one('.madoriInfo')
                    if layout_element:
                        listing_data["layout"] = layout_element.text.strip()
                    
                    # Get property size
                    size_element = element.select_one('.areaInfo')
                    if size_element:
                        listing_data["size"] = size_element.text.strip()
                    
                    # Get property type
                    type_element = element.select_one('.buildingTypeInfo')
                    if type_element:
                        listing_data["building_type"] = type_element.text.strip()
                    
                    # Get construction year
                    year_element = element.select_one('.builtDateInfo')
                    if year_element:
                        listing_data["year_built"] = year_element.text.strip()
                    
                    # Get property features
                    features_elements = element.select('ul.articleTagList li')
                    features = [feature.text.strip() for feature in features_elements]
                    if features:
                        listing_data["features"] = features
                    
                    # Get property URL for fetching high-res images later
                    detail_url = None
                    url_element = element.select_one('a[href*="detail"]')
                    if url_element and 'href' in url_element.attrs:
                        detail_url = urljoin(self.base_url, url_element['href'])
                        listing_data["detail_url"] = detail_url
                    
                    # Still get thumbnail images as fallback
                    image_elements = element.select('.mainvisual img')
                    listing_data["images"] = []
                    for img in image_elements:
                        if 'data-src' in img.attrs:
                            img_src = img['data-src']
                            # Skip loading images or icons
                            if not (img_src.endswith('.gif') or 'loading' in img_src or 'icon' in img_src):
                                listing_data["images"].append(img_src)
                        elif 'src' in img.attrs and not (img['src'].endswith('blank.png') or '.gif' in img['src'] or 'loading' in img['src'] or 'icon' in img['src']):
                            listing_data["images"].append(img['src'])
                    
                    # Fetch high-resolution images from detail page if available
                    if detail_url:
                        try:
                            high_res_images = self._fetch_high_res_images(detail_url)
                            if high_res_images:
                                listing_data["images"] = high_res_images
                        except Exception as e:
                            logger.error(f"Error fetching high-res images from {detail_url}: {str(e)}")
                    
                    # Clean and standardize the data
                    cleaned_data = self.clean_data(listing_data)
                    listings.append(cleaned_data)
                
                except Exception as e:
                    logger.error(f"Error extracting HOMES sale listing: {str(e)}")
                    continue
        
        return listings
    
    def _fallback_extract_listings(self, html: str, property_type: str) -> List[Dict[str, Any]]:
        """
        Fallback method to extract property listings when standard selectors fail.
        Uses more generic approaches to find property information.
        
        Args:
            html: HTML content to parse
            property_type: Type of property listing ("rent" or "buy")
            
        Returns:
            List of property listings
        """
        soup = BeautifulSoup(html, 'html.parser')
        listings = []
        
        # Common patterns that may indicate property listings
        # Look for any div or article that might contain property information
        potential_containers = [
            # Any div with property-related class names or IDs
            soup.select('div[class*="property"], div[class*="bukken"], div[class*="estate"], div[class*="item"], div[class*="cassette"]'),
            # Any article element (often used for listing items)
            soup.select('article'),
            # Any list items that might contain property information
            soup.select('li[class*="property"], li[class*="bukken"], li[class*="item"]'),
            # Any div with a price element inside
            [div for div in soup.select('div') if div.select('*[class*="price"]') or div.find(string=re.compile(r'\d+万円'))]
        ]
        
        # Flatten the list of potential containers
        all_containers = []
        for container_list in potential_containers:
            all_containers.extend(container_list)
        
        # Get unique containers (no duplicates)
        unique_containers = list(set(all_containers))
        logger.info(f"Found {len(unique_containers)} potential property containers")
        
        for container in unique_containers:
            try:
                listing_data = {}
                
                # Extract the URL if there's a link in the container
                links = container.select('a[href]')
                for link in links:
                    href = link.get('href')
                    if href and ('detail' in href or 'property' in href or 'bukken' in href):
                        listing_data["url"] = urljoin(self.base_url, href)
                        break
                
                # If no URL was found, this might not be a property listing
                if "url" not in listing_data:
                    continue
                
                # Extract title - look for heading elements or strong text
                title_elements = container.select('h1, h2, h3, h4, strong, *[class*="title"]')
                if title_elements:
                    listing_data["title"] = title_elements[0].get_text(strip=True)
                
                # Extract price - look for elements with price-related class or content
                price_pattern = re.compile(r'\d+[,\d]*万円')
                price_elements = [
                    el for el in container.select('*[class*="price"], span, div, p')
                    if el.find(string=price_pattern) or price_pattern.search(el.get_text(strip=True))
                ]
                
                if price_elements:
                    price_text = price_elements[0].get_text(strip=True)
                    price_match = price_pattern.search(price_text)
                    if price_match:
                        listing_data["price"] = price_match.group(0)
                
                # Extract location - look for address-related content
                location_elements = container.select('*[class*="address"], *[class*="location"]')
                if location_elements:
                    listing_data["location"] = location_elements[0].get_text(strip=True)
                
                # Extract property features if available
                feature_elements = container.select('*[class*="feature"], *[class*="tag"], li')
                if feature_elements:
                    listing_data["features"] = [el.get_text(strip=True) for el in feature_elements[:5]]
                
                # Extract images
                image_elements = container.select('img')
                listing_data["images"] = []
                for img in image_elements:
                    img_src = img.get('src') or img.get('data-src')
                    if img_src and not (img_src.endswith('blank.png') or 'spacer' in img_src):
                        listing_data["images"].append(img_src)
                
                # Only add the listing if we found at least a price or title
                if "price" in listing_data or "title" in listing_data:
                    # Clean and standardize the data
                    cleaned_data = self.clean_data(listing_data)
                    listings.append(cleaned_data)
            
            except Exception as e:
                logger.error(f"Error in fallback extraction: {str(e)}")
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
        next_button = soup.select_one('li.nextPage a')
        
        if next_button and 'href' in next_button.attrs:
            return urljoin(self.base_url, next_button['href'])
        
        return None
    
    def _fetch_high_res_images(self, detail_url: str) -> List[str]:
        """
        Fetch high-resolution images from the property detail page.
        
        Args:
            detail_url: URL of the property detail page
            
        Returns:
            List of high-resolution image URLs
        """
        logger.info(f"Fetching high-resolution images from {detail_url}")
        
        try:
            # Get the HTML content of the detail page
            html = get_html(detail_url, session=self.session)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find high-resolution images
            high_res_images = []
            
            # Try different selectors for image galleries
            image_selectors = [
                # Selector for main property images
                'div.detailGallery img', 
                # Selector for photo gallery
                'div.photoGallery img',
                # Carousel images
                'div.carousel img',
                # General high-quality images on the page
                'div.detailPhotos img',
                # Fallback to any large images
                'img[width="600"], img[width="800"], img[width="1024"]',
                # Another common pattern for detail images
                'div.photo img, div.mainPhoto img',
                # Last resort - any image that's not obviously a small thumbnail or icon
                'img[src*="/img.homes.jp/"]'
            ]
            
            for selector in image_selectors:
                images = soup.select(selector)
                if images:
                    logger.info(f"Found {len(images)} high-resolution images using selector: {selector}")
                    
                    # Process found images
                    for img in images:
                        img_src = None
                        # Try different image attributes
                        for attr in ['src', 'data-src', 'data-original', 'data-lazy-src']:
                            if attr in img.attrs:
                                img_src = img[attr]
                                break
                        
                        if img_src:
                            # Skip loading images, icons, tiny thumbnails
                            if not (img_src.endswith('.gif') or 
                                    'loading' in img_src or 
                                    'icon' in img_src or 
                                    'blank.png' in img_src or
                                    'spacer' in img_src):
                                
                                # Convert relative URLs to absolute
                                img_src = urljoin(self.base_url, img_src)
                                
                                # Try to get original image instead of smallimg
                                if 'smallimg' in img_src:
                                    # Extract the original image URL from the smallimg URL
                                    parsed_url = urlparse(img_src)
                                    query_params = parse_qs(parsed_url.query)
                                    if 'file' in query_params and query_params['file']:
                                        original_url = query_params['file'][0]
                                        logger.info(f"Extracted original image URL: {original_url}")
                                        img_src = original_url
                                
                                high_res_images.append(img_src)
                    
                    # If we found images, no need to try other selectors
                    if high_res_images:
                        break
            
            # Remove duplicates while preserving order
            seen = set()
            unique_images = []
            for img in high_res_images:
                if img not in seen:
                    seen.add(img)
                    unique_images.append(img)
            
            logger.info(f"Found {len(unique_images)} unique high-resolution images for {detail_url}")
            return unique_images
            
        except Exception as e:
            logger.error(f"Error fetching high-resolution images from {detail_url}: {str(e)}")
            return []
    
    def _get_location_path(self, location: str) -> str:
        """
        Get the location path used by HOMES for a given location.
        
        Args:
            location: Location name in English (e.g., "tokyo", "osaka")
            
        Returns:
            Location path used by HOMES
        """
        # Mapping of English location names to HOMES location paths
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
