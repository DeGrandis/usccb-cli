#!/usr/bin/env python3
"""
USCCB Mass Times Scraper

Find nearby Catholic churches and their Mass schedules using location search.
Uses the USCCB parish data API and geocoding to convert locations to coordinates.
Outputs markdown by default for LLM parsing, or JSON with --json flag.
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


def format_as_markdown(result):
    """Format mass times data as markdown for LLM parsing."""
    if "error" in result:
        return f"Error: {result['error']}"
    
    output = []
    
    # Header
    output.append(f"# Catholic Churches Near {result['location_searched']}")
    output.append(f"**Coordinates:** {result['coordinates']['latitude']:.4f}, {result['coordinates']['longitude']:.4f}")
    output.append(f"**Results:** {result['total_results']} churches (Page {result['page']})")
    output.append("")
    
    # Each church
    for i, church in enumerate(result['churches'], 1):
        output.append(f"## {i}. {church.get('name', 'Unknown Church')}")
        
        # Address
        street = church.get('church_address_street_address', '')
        city = church.get('church_address_city_name', '')
        state = church.get('church_address_providence_name', '')
        zip_code = church.get('church_address_postal_code', '')
        
        if street:
            output.append(f"**Address:** {street}")
        if city or state or zip_code:
            city_state_zip = f"{city}, {state} {zip_code}".strip(', ')
            output.append(f"**Location:** {city_state_zip}")
        
        # Contact
        phone = church.get('phone_number', '')
        if phone:
            output.append(f"**Phone:** {phone}")
        
        website = church.get('url', '')
        if website:
            output.append(f"**Website:** {website}")
        
        # Distance
        distance = church.get('distance', '')
        if distance:
            output.append(f"**Distance:** {distance} miles")
        
        # Mass times
        worship_times = church.get('church_worship_times', [])
        if worship_times and isinstance(worship_times, list):
            output.append("")
            output.append("**Mass Times:**")
            
            # Group by day of week
            days_schedule = {}
            for service in worship_times:
                day = service.get('day_of_week', '').strip()
                service_type = service.get('service_typename', '')
                time_start = service.get('time_start', '')
                comment = service.get('comment', '')
                language = service.get('language', '')
                
                if day and time_start:
                    # Format time (remove seconds if present)
                    if len(time_start) == 8 and time_start.count(':') == 2:
                        time_parts = time_start.split(':')
                        time_formatted = f"{time_parts[0]}:{time_parts[1]}"
                    else:
                        time_formatted = time_start
                    
                    # Build service description
                    service_desc = time_formatted
                    if service_type and service_type != 'Week Days' and service_type != 'Weekend':
                        service_desc += f" ({service_type})"
                    if comment:
                        service_desc += f" - {comment}"
                    if language and language.strip():
                        service_desc += f" [{language.strip()}]"
                    
                    if day not in days_schedule:
                        days_schedule[day] = []
                    days_schedule[day].append(service_desc)
            
            # Output by day
            day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Weekdays']
            for day in day_order:
                if day in days_schedule:
                    output.append(f"- **{day}:** {', '.join(days_schedule[day])}")
            
            # Add any other days not in standard order
            for day, times in days_schedule.items():
                if day not in day_order:
                    output.append(f"- **{day}:** {', '.join(times)}")
        
        output.append("")
        output.append("---")
        output.append("")
    
    return '\n'.join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find nearby Catholic churches and Mass times'
    )
    parser.add_argument('location', help='Location to search (city, zipcode, or address)')
    parser.add_argument('--page', '-p', type=int, default=1, help='Page number for pagination')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of churches to return')
    parser.add_argument('--json', action='store_true', help='Output as JSON instead of markdown')
    
    args = parser.parse_args()
    
    result = get_mass_times(args.location, args.page, args.limit)
    
    # Output format based on flag
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_as_markdown(result))
    
    # Exit with error code if there was an error
    if "error" in result:
        sys.exit(1)
