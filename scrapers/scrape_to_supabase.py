#!/usr/bin/env python
"""
JapanHouse Scraper to Supabase

This script runs the scrapers and directly uploads the results to Supabase.
"""
import os
import argparse
from typing import Dict, List, Any, Optional
import time
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger

# Add the current directory to the path to enable proper imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import scrapers
from sites import SCRAPERS
from common.db_connector import SupabaseConnector


def setup_logger():
    """Set up the logger."""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up log file with rotation
    log_file = os.path.join(log_dir, "supabase_upload_{time}.log")
    logger.add(log_file, rotation="1 day", retention="7 days")


def process_images(listing):
    """
    Process and clean up image URLs in a listing.
    
    Args:
        listing: A property listing dictionary
        
    Returns:
        Listing with processed images
    """
    if 'images' not in listing or not listing['images']:
        return listing
    
    # Process images to ensure valid URLs and remove loading/icon images
    processed_images = []
    for img_url in listing['images']:
        # Skip loading indicators, tiny icons, and other non-property images
        if any(skip_pattern in img_url.lower() for skip_pattern in [
            'loading', 'icon_', 'blank.png', 'spacer', '.gif',
            'utility/loading', 'icon_visited', 'icon_sokunyu'
        ]):
            continue
            
        # Keep only unique, valid image URLs
        if img_url and img_url not in processed_images:
            processed_images.append(img_url)
    
    # Extract original images from smallimg URLs if possible
    high_res_images = []
    for img_url in processed_images:
        if 'smallimg' in img_url and 'file=' in img_url:
            # Try to extract the original image URL from the smallimg URL
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(img_url)
            query_params = parse_qs(parsed_url.query)
            if 'file' in query_params and query_params['file']:
                original_url = query_params['file'][0]
                high_res_images.append(original_url)
            else:
                high_res_images.append(img_url)
        else:
            high_res_images.append(img_url)
    
    # Update the listing with processed images
    listing['images'] = high_res_images if high_res_images else processed_images
    return listing

def get_existing_listing_ids(db, table_name):
    """
    Get IDs of existing listings from Supabase to avoid duplicates.
    
    Args:
        db: SupabaseConnector instance
        table_name: Name of the table to query
        
    Returns:
        Dictionary of existing listings keyed by their unique identifiers
    """
    try:
        # Query existing listings from Supabase
        response = db.client.table(table_name).select("id,source_id,source,url").execute()
        listings = response.data
        
        # Create dictionaries for fast lookup
        source_id_dict = {}
        url_dict = {}
        id_by_source_id = {}
        
        for listing in listings:
            if listing.get('source_id'):
                source_key = f"{listing['source']}:{listing['source_id']}"
                source_id_dict[source_key] = True
                id_by_source_id[source_key] = listing['id']
            
            if listing.get('url'):
                url_dict[listing['url']] = True
        
        return {
            'source_id_dict': source_id_dict,
            'url_dict': url_dict,
            'id_by_source_id': id_by_source_id
        }
    except Exception as e:
        logger.error(f"Error getting existing listings: {str(e)}")
        return {'source_id_dict': {}, 'url_dict': {}, 'id_by_source_id': {}}


def run_scrapers_and_upload(args):
    """
    Run the scrapers and upload results to Supabase.
    
    Args:
        args: Command line arguments parsed by argparse
    """
    # Initialize Supabase connector
    db = SupabaseConnector()
    
    if not db.client:
        logger.error("Could not connect to Supabase. Check your credentials.")
        return
    
    # Get the list of scrapers to run
    scraper_names = args.scrapers.split(",") if args.scrapers else list(SCRAPERS.keys())
    
    # Validate scraper names
    invalid_scrapers = [name for name in scraper_names if name not in SCRAPERS]
    if invalid_scrapers:
        logger.error(f"Invalid scraper names: {', '.join(invalid_scrapers)}")
        logger.info(f"Available scrapers: {', '.join(SCRAPERS.keys())}")
        return
    
    # Get existing listings if in update mode
    existing_listings = {}
    if args.update_mode:
        logger.info(f"Running in update mode - checking for existing listings")
        existing_listings = get_existing_listing_ids(db, args.table_name)
        logger.info(f"Found {len(existing_listings['source_id_dict'])} existing listings")
    
    # Run the scrapers and upload results
    total_uploaded = 0
    total_updated = 0
    total_skipped = 0
    
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
            
            # Process listings to ensure high-quality images
            if results:
                logger.info(f"Processing {len(results)} results from {scraper_name}")
                processed_results = [process_images(listing) for listing in results]
                
                # Filter out listings with no valid images if image quality is enforced
                if args.enforce_image_quality:
                    original_count = len(processed_results)
                    processed_results = [listing for listing in processed_results 
                                        if 'images' in listing and listing['images']]
                    filtered_count = original_count - len(processed_results)
                    if filtered_count > 0:
                        logger.info(f"Filtered out {filtered_count} listings with no valid images")
                
                # Limit the number of listings if max_listings is specified
                if args.max_listings and args.max_listings > 0 and len(processed_results) > args.max_listings:
                    logger.info(f"Limiting results to {args.max_listings} listings (from {len(processed_results)})")
                    processed_results = processed_results[:args.max_listings]
                
                # Handle updates and duplicates if in update mode
                new_listings = []
                update_listings = []
                
                if args.update_mode:
                    for listing in processed_results:
                        # Check if listing already exists by source_id or URL
                        is_duplicate = False
                        listing_id = None
                        
                        if 'source_id' in listing and listing['source_id']:
                            source_key = f"{listing['source']}:{listing['source_id']}"
                            if source_key in existing_listings['source_id_dict']:
                                is_duplicate = True
                                listing_id = existing_listings['id_by_source_id'].get(source_key)
                        
                        if not is_duplicate and 'url' in listing and listing['url']:
                            if listing['url'] in existing_listings['url_dict']:
                                is_duplicate = True
                        
                        if is_duplicate:
                            if args.update_existing and listing_id:
                                # Update the existing listing
                                listing['id'] = listing_id
                                update_listings.append(listing)
                            else:
                                # Skip this listing
                                total_skipped += 1
                        else:
                            # New listing
                            new_listings.append(listing)
                    
                    logger.info(f"Found {len(new_listings)} new listings and {len(update_listings)} to update")
                    processed_results = new_listings
                
                # Upload new listings to Supabase
                if processed_results:
                    logger.info(f"Uploading {len(processed_results)} results from {scraper_name} to Supabase")
                    
                    success = db.save_listings(processed_results, args.table_name)
                    
                    if success:
                        logger.success(f"Successfully uploaded {len(processed_results)} listings from {scraper_name}")
                        total_uploaded += len(processed_results)
                    else:
                        logger.error(f"Failed to upload listings from {scraper_name}")
                
                # Update existing listings if needed
                if update_listings and args.update_existing:
                    logger.info(f"Updating {len(update_listings)} existing listings")
                    for listing in update_listings:
                        try:
                            # Update the existing listing
                            db.client.table(args.table_name).update(listing).eq('id', listing['id']).execute()
                            total_updated += 1
                        except Exception as e:
                            logger.error(f"Error updating listing {listing.get('id')}: {str(e)}")
                    
                    logger.success(f"Updated {total_updated} existing listings")
                
                if not processed_results and not update_listings:
                    logger.warning(f"No valid results from {scraper_name} after filtering")
            else:
                logger.warning(f"No results from {scraper_name}")
        
        except Exception as e:
            logger.error(f"Error running {scraper_name} scraper: {str(e)}")
    
    logger.info(f"Summary: {total_uploaded} new listings uploaded, {total_updated} listings updated, {total_skipped} duplicates skipped")


def main():
    """Main entry point."""
    # Load environment variables from the root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root_dir, '.env')
    
    # Check if .env file exists and load it
    if os.path.exists(env_path):
        logger.info(f"Loading environment variables from {env_path}")
        load_dotenv(env_path)
    else:
        logger.warning(f"No .env file found at {env_path}")
    
    # Set up the logger
    setup_logger()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run JapanHouse scrapers and upload to Supabase")
    parser.add_argument("--scrapers", type=str, help="Comma-separated list of scrapers to run (default: all)")
    parser.add_argument("--location", type=str, default="tokyo", help="Location to search for (default: tokyo)")
    parser.add_argument("--property-type", type=str, default="rent", help="Property type to search for (rent or buy) (default: rent)")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to scrape (default: 5)")
    parser.add_argument("--max-listings", type=int, help="Maximum number of listings to process per scraper (default: no limit)")
    parser.add_argument("--table-name", type=str, default="property_listings", help="Supabase table name (default: property_listings)")
    parser.add_argument("--enforce-image-quality", action="store_true", help="Filter out listings with no valid images")
    parser.add_argument("--detail-pages", action="store_true", help="Visit detail pages to get high-resolution images (slower but better quality)")
    parser.add_argument("--update-mode", action="store_true", help="Skip listings that already exist in the database")
    parser.add_argument("--update-existing", action="store_true", help="Update existing listings instead of skipping them (requires --update-mode)")
    args = parser.parse_args()
    
    # Log the starting configuration
    logger.info(f"Starting JapanHouse scrapers with configuration:")
    logger.info(f"  Scrapers: {args.scrapers if args.scrapers else 'all'}")
    logger.info(f"  Location: {args.location}")
    logger.info(f"  Property Type: {args.property_type}")
    logger.info(f"  Max Pages: {args.max_pages}")
    logger.info(f"  Max Listings: {args.max_listings if args.max_listings else 'No limit'}")
    logger.info(f"  Table Name: {args.table_name}")
    logger.info(f"  Update Mode: {'Enabled' if args.update_mode else 'Disabled'}")
    logger.info(f"  Update Existing: {'Enabled' if args.update_existing else 'Disabled'}")
    logger.info(f"  Enforce Image Quality: {'Enabled' if args.enforce_image_quality else 'Disabled'}")
    logger.info(f"  Detail Pages: {'Enabled' if args.detail_pages else 'Disabled'}")
    
    # Run the scrapers and upload to Supabase
    run_scrapers_and_upload(args)
    
    logger.info("Finished scraping and uploading to Supabase")


if __name__ == "__main__":
    main()
