#!/usr/bin/env python3
"""
USCCB Mass Times Scraper

Find nearby Catholic churches and their Mass schedules using location search.
Uses the USCCB parish data API and geocoding to convert locations to coordinates.
"""

import sys
import json
import requests
import argparse
from urllib.parse import quote

PARISH_API_URL = "https://apiv4.updateparishdata.org/Churchs/"
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"


def geocode_location(location):
    """
    Convert a location (city, zipcode, address) to latitude/longitude coordinates.
    
    Args:
        location: Location string (e.g., "Boston, MA", "02108", "New York")
        
    Returns:
        tuple: (latitude, longitude) or None if not found
    """
    try:
        params = {
            'q': location,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'  # Limit to US since USCCB is US-based
        }
        headers = {
            'User-Agent': 'USCCB-CLI/1.0'  # Nominatim requires a user agent
        }
        
        response = requests.get(GEOCODE_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
        return None
        
    except requests.RequestException as e:
        return None


def get_mass_times(location, page=1, limit=None):
    """
    Find nearby Catholic churches and their Mass times.
    
    Args:
        location: Location string to search near (city, zipcode, address)
        page: Page number for pagination (default: 1)
        limit: Maximum number of churches to return (default: all)
        
    Returns:
        dict: Results with churches array and metadata
    """
    # First, geocode the location
    coords = geocode_location(location)
    if not coords:
        return {
            "error": f"Could not find coordinates for location: {location}",
            "location_searched": location
        }
    
    lat, lon = coords
    
    # Call the parish API
    try:
        params = {
            'lat': lat,
            'long': lon,
            'pg': page
        }
        
        headers = {
            'accept': '*/*',
            'origin': 'https://www.usccb.org',
            'referer': 'https://www.usccb.org/',
            'user-agent': 'Mozilla/5.0 (compatible; USCCB-CLI/1.0)'
        }
        
        response = requests.get(PARISH_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Apply limit if specified
        if limit and isinstance(data, list):
            data = data[:limit]
        
        # Return raw API response with search metadata
        result = {
            "location_searched": location,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            },
            "page": page,
            "total_results": len(data) if isinstance(data, list) else 0,
            "churches": data if isinstance(data, list) else []
        }
        
        return result
        
    except requests.RequestException as e:
        return {
            "error": f"Failed to fetch church data: {str(e)}",
            "location_searched": location,
            "coordinates": {"latitude": lat, "longitude": lon}
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find nearby Catholic churches and Mass times'
    )
    parser.add_argument('location', help='Location to search (city, zipcode, or address)')
    parser.add_argument('--page', '-p', type=int, default=1, help='Page number for pagination')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of churches to return')
    
    args = parser.parse_args()
    
    result = get_mass_times(args.location, args.page, args.limit)
    
    # Output JSON to stdout
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Exit with error code if there was an error
    if "error" in result:
        sys.exit(1)
