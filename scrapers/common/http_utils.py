"""
HTTP Utilities for JapanHouse Scrapers

This module provides HTTP utility functions with retry logic, 
proper error handling, and other features useful for web scraping.
"""
import time
import random
from typing import Dict, Any, Optional, Union, List

import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger


class RequestsSession:
    """A wrapper around requests.Session with retry logic and user agent rotation."""
    
    # List of common user agents to rotate through
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.1'
    ]
    
    def __init__(self, default_headers: Optional[Dict[str, str]] = None, 
                 cookies: Optional[Dict[str, str]] = None,
                 proxy: Optional[str] = None,
                 max_retries: int = 3,
                 timeout: int = 30):
        """
        Initialize the requests session.
        
        Args:
            default_headers: Default headers to use for requests
            cookies: Default cookies to set
            proxy: Proxy to use for requests
            max_retries: Maximum number of retries for failed requests
            timeout: Default timeout for requests in seconds
        """
        self.session = requests.Session()
        
        # Set default headers
        if default_headers:
            self.session.headers.update(default_headers)
        else:
            self.session.headers.update({
                'User-Agent': random.choice(self.USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            })
        
        # Set cookies if provided
        if cookies:
            self.session.cookies.update(cookies)
        
        # Set proxy if provided
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
        
        self.max_retries = max_retries
        self.timeout = timeout
    
    def rotate_user_agent(self) -> None:
        """Rotate the user agent to a different one from the list."""
        self.session.headers['User-Agent'] = random.choice(self.USER_AGENTS)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Perform a GET request with retry logic.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests.get
            
        Returns:
            Response object
            
        Raises:
            RequestException: If the request fails after retries
        """
        try:
            # Set default timeout if not provided
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            
            # Random delay to avoid being detected as a bot
            time.sleep(random.uniform(1, 3))
            
            # Rotate user agent before request
            self.rotate_user_agent()
            
            # Make the request
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            
            return response
        
        except RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Perform a POST request with retry logic.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to requests.post
            
        Returns:
            Response object
            
        Raises:
            RequestException: If the request fails after retries
        """
        try:
            # Set default timeout if not provided
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            
            # Random delay to avoid being detected as a bot
            time.sleep(random.uniform(1, 3))
            
            # Rotate user agent before request
            self.rotate_user_agent()
            
            # Make the request
            response = self.session.post(url, **kwargs)
            response.raise_for_status()
            
            return response
        
        except RequestException as e:
            logger.error(f"Error posting to {url}: {str(e)}")
            raise


def get_html(url: str, session: Optional[RequestsSession] = None, **kwargs) -> str:
    """
    Get HTML content from a URL with error handling.
    
    Args:
        url: URL to fetch
        session: RequestsSession instance, creates a new one if None
        **kwargs: Additional arguments to pass to session.get
        
    Returns:
        HTML content as string
        
    Raises:
        ValueError: If the URL is invalid or the request fails
    """
    try:
        if session is None:
            session = RequestsSession()
        
        response = session.get(url, **kwargs)
        return response.text
    
    except Exception as e:
        logger.error(f"Failed to get HTML from {url}: {str(e)}")
        raise ValueError(f"Failed to get HTML from {url}: {str(e)}")


def get_json(url: str, session: Optional[RequestsSession] = None, **kwargs) -> Dict[str, Any]:
    """
    Get JSON content from a URL with error handling.
    
    Args:
        url: URL to fetch
        session: RequestsSession instance, creates a new one if None
        **kwargs: Additional arguments to pass to session.get
        
    Returns:
        JSON content as dict
        
    Raises:
        ValueError: If the URL is invalid, the request fails, or the response is not valid JSON
    """
    try:
        if session is None:
            session = RequestsSession()
        
        response = session.get(url, **kwargs)
        return response.json()
    
    except Exception as e:
        logger.error(f"Failed to get JSON from {url}: {str(e)}")
        raise ValueError(f"Failed to get JSON from {url}: {str(e)}")
