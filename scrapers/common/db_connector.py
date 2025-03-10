"""
Database Connector for JapanHouse

This module provides functionality to connect to Supabase and
save property listings to the database.
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from loguru import logger
from dotenv import load_dotenv
from supabase import create_client, Client


class SupabaseConnector:
    """Connector for Supabase database."""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None, service_key: Optional[str] = None):
        """
        Initialize the Supabase connector.
        
        Args:
            url: Supabase URL (if None, will try to get from environment)
            key: Supabase API key (if None, will try to get from environment)
            service_key: Supabase service role key for bypassing RLS (if None, will try to get from environment)
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Get Supabase credentials
        self.url = url or os.getenv("SUPABASE_URL")
        
        # First try to get the service key (which can bypass RLS)
        self.service_key = service_key or os.getenv("SUPABASE_SERVICE_KEY")
        self.standard_key = key or os.getenv("SUPABASE_KEY")
        
        # Use service key if available, otherwise standard key
        if self.service_key:
            self.key = self.service_key
            self.using_service_role = True
            logger.info("Service role key detected. Will bypass RLS policies.")
        else:
            self.key = self.standard_key
            self.using_service_role = False
        
        if not self.url or not self.key:
            logger.warning("Supabase URL or key not provided. Database operations will not work.")
            self.client = None
        else:
            # Log URL and key format (partially masked) at INFO level for visibility
            logger.info(f"Connecting to Supabase URL: {self.url}")
            if self.key:
                masked_key = self.key[:5] + "*****" + self.key[-5:] if len(self.key) > 10 else "*****"
                logger.info(f"Using key: {masked_key}")
            
            # Ensure URL has correct format
            # Remove trailing slashes if present
            if self.url and self.url.endswith("/"):
                self.url = self.url.rstrip("/")
                
            try:
                # Create Supabase client
                self.client = create_client(self.url, self.key)
                
                if self.using_service_role:
                    logger.info("Connected to Supabase with service role key (RLS bypassed)")
                else:
                    logger.info("Connected to Supabase with standard key (subject to RLS policies)")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {str(e)}")
                self.client = None
    
    def save_listings(self, listings: List[Dict[str, Any]], table_name: str = "property_listings") -> bool:
        """
        Save property listings to Supabase.
        
        Args:
            listings: List of property listings to save
            table_name: Name of the table to save to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("No Supabase connection available")
            return False
        
        if not listings:
            logger.warning("No listings to save")
            return False
        
        try:
            # Format listings for database insertion
            formatted_listings = []
            
            # Known valid fields in the Supabase schema
            # Update this list based on your actual database schema
            valid_fields = [
                "id", "title", "url", "price", "location", "description", 
                "images", "features", "size", "layout", "year_built", 
                "building_type", "access", "source", "property_type", 
                "created_at", "updated_at", "initial_fees"
            ]
            
            for listing in listings:
                # Add timestamps if not present
                if "created_at" not in listing:
                    listing["created_at"] = datetime.now().isoformat()
                
                # Filter listing to only include valid fields
                filtered_listing = {}
                for key, value in listing.items():
                    # Skip fields that aren't in our valid fields list
                    if key not in valid_fields:
                        logger.debug(f"Skipping unknown field '{key}' for database upload")
                        continue
                        
                    # Convert complex objects to JSON strings
                    if isinstance(value, (dict, list)):
                        filtered_listing[key] = json.dumps(value)
                    else:
                        filtered_listing[key] = value
                
                formatted_listings.append(filtered_listing)
            
            # Ensure all listings have the same keys by standardizing them
            # This prevents the "All object keys must match" error from Supabase
            if formatted_listings:
                # Get all unique keys across all listings
                all_keys = set()
                for listing in formatted_listings:
                    all_keys.update(listing.keys())
                
                # Ensure all listings have all keys (with null values for missing ones)
                for listing in formatted_listings:
                    for key in all_keys:
                        if key not in listing:
                            listing[key] = None
            
            # Insert data in batches to avoid payload size limits
            batch_size = 100
            for i in range(0, len(formatted_listings), batch_size):
                batch = formatted_listings[i:i+batch_size]
                
                # Create a query for inserting data
                query = self.client.table(table_name)
                
                # If not using service role key, try to handle RLS differently
                if not self.using_service_role:
                    # Log a warning about potential RLS issues
                    logger.warning("Not using service role key - uploads may fail due to RLS policies")
                
                try:
                    # Upsert data (insert or update based on constraints)
                    result = query.upsert(batch).execute()
                    
                    if hasattr(result, 'error') and result.error:
                        logger.error(f"Error inserting batch {i//batch_size + 1}: {result.error}")
                        return False
                        
                    logger.info(f"Successfully inserted batch {i//batch_size + 1} ({len(batch)} listings)")
                except Exception as e:
                    logger.error(f"Error saving listings to Supabase: {str(e)}")
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving listings to Supabase: {str(e)}")
            return False
    
    def get_listings(self, 
                     filters: Optional[Dict[str, Any]] = None, 
                     limit: int = 100, 
                     table_name: str = "property_listings") -> List[Dict[str, Any]]:
        """
        Get property listings from Supabase.
        
        Args:
            filters: Dictionary of column-value pairs to filter by
            limit: Maximum number of listings to return
            table_name: Name of the table to query
            
        Returns:
            List of property listings
        """
        if not self.client:
            logger.error("No Supabase connection available")
            return []
        
        try:
            # Start query builder
            query = self.client.table(table_name).select("*")
            
            # Add filters if provided
            if filters:
                for column, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(column, value)
                    else:
                        query = query.eq(column, value)
            
            # Set limit and execute
            result = query.limit(limit).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Error querying listings: {result.error}")
                return []
            
            # Parse JSON strings back to objects
            listings = result.data
            for listing in listings:
                for key, value in listing.items():
                    if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                        try:
                            listing[key] = json.loads(value)
                        except json.JSONDecodeError:
                            pass  # Not a valid JSON string, keep as is
            
            return listings
        
        except Exception as e:
            logger.error(f"Error getting listings from Supabase: {str(e)}")
            return []
