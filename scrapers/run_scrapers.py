#!/usr/bin/env python
"""
JapanHouse Scraper Runner

This script runs all the scrapers and saves the results to JSON files.
It can be used to test the scrapers and collect data for the database.
"""
import os
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

from loguru import logger

# Import scrapers
from sites import SCRAPERS


def setup_logger():
    """Set up the logger."""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up log file with rotation
    log_file = os.path.join(log_dir, "scraper_{time}.log")
    logger.add(log_file, rotation="1 day", retention="7 days")


def run_scrapers(args):
    """
    Run the scrapers based on command line arguments.
    
    Args:
        args: Command line arguments parsed by argparse
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the list of scrapers to run
    scraper_names = args.scrapers.split(",") if args.scrapers else list(SCRAPERS.keys())
    
    # Validate scraper names
    invalid_scrapers = [name for name in scraper_names if name not in SCRAPERS]
    if invalid_scrapers:
        logger.error(f"Invalid scraper names: {', '.join(invalid_scrapers)}")
        logger.info(f"Available scrapers: {', '.join(SCRAPERS.keys())}")
        return
    
    # Run the scrapers
    for scraper_name in scraper_names:
        logger.info(f"Running {scraper_name} scraper")
        
        try:
            # Initialize the scraper
            scraper_class = SCRAPERS[scraper_name]
            scraper = scraper_class()
            
            # Run the scraper
            results = scraper.scrape(
                location=args.location,
                property_type=args.property_type,
                max_pages=args.max_pages
            )
            
            # Save the results
            if results:
                timestamp = int(time.time())
                output_path = os.path.join(
                    output_dir, 
                    f"{scraper_name}_{args.location}_{args.property_type}_{timestamp}.json"
                )
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                logger.success(f"Saved {len(results)} results from {scraper_name} to {output_path}")
            else:
                logger.warning(f"No results from {scraper_name}")
        
        except Exception as e:
            logger.error(f"Error running {scraper_name} scraper: {str(e)}")


def main():
    """Main entry point."""
    # Set up the logger
    setup_logger()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run JapanHouse scrapers")
    parser.add_argument("--scrapers", type=str, help="Comma-separated list of scrapers to run (default: all)")
    parser.add_argument("--location", type=str, default="tokyo", help="Location to search for (default: tokyo)")
    parser.add_argument("--property-type", type=str, default="rent", help="Property type to search for (rent or buy) (default: rent)")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to scrape (default: 5)")
    args = parser.parse_args()
    
    # Log the starting configuration
    logger.info(f"Starting JapanHouse scrapers with configuration:")
    logger.info(f"  Scrapers: {args.scrapers if args.scrapers else 'all'}")
    logger.info(f"  Location: {args.location}")
    logger.info(f"  Property Type: {args.property_type}")
    logger.info(f"  Max Pages: {args.max_pages}")
    
    # Run the scrapers
    run_scrapers(args)
    
    logger.info("Finished running scrapers")


if __name__ == "__main__":
    main()
