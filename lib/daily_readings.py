#!/usr/bin/env python3
"""
USCCB Daily Bible Readings Scraper

Retrieves daily Bible readings from the United States Conference of Catholic Bishops website.
Outputs markdown by default for LLM parsing, or JSON with --json flag.
"""

import sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BASE_URL = "https://bible.usccb.org"


def get_daily_readings(date=None, titles=None):
    """
    Fetch daily Bible readings for a specific date.
    
    Args:
        date: Optional date string in YYYY-MM-DD format. Defaults to today.
        titles: Optional list of reading titles to filter (e.g., ['Gospel', 'Reading 1'])
        
    Returns:
        dict: Daily readings data including all readings, psalm, gospel, etc.
    """
    if date:
        # Parse date and format for URL
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": f"Invalid date format: {date}. Use YYYY-MM-DD"}
    else:
        # Use today's date
        dt = datetime.now()
    
    # Format URL as MMDDYY.cfm
    url = f"{BASE_URL}/bible/readings/{dt.strftime('%m%d%y')}.cfm"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch readings: {str(e)}"}
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Parse the readings
    readings_data = {
        "date": dt.strftime("%Y-%m-%d"),
        "url": url,
        "liturgical_date": None,
        "readings": []
    }
    
    # Get liturgical date/title from page title or og:title meta tag
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        title = og_title.get('content')
        # Remove " | USCCB" suffix if present
        readings_data["liturgical_date"] = title.replace(' | USCCB', '').strip()
    
    # Find all reading blocks (they're in div with both classes)
    reading_blocks = soup.find_all('div', class_='b-verse')
    
    for block in reading_blocks:
        reading = {}
        
        # Find the content-header within this block
        header = block.find('div', class_='content-header')
        if not header:
            continue
        
        # Get reading title (e.g., "Reading 1", "Responsorial Psalm", "Gospel")
        title_elem = header.find('h3', class_='name')
        if title_elem:
            reading['title'] = title_elem.get_text(strip=True)
        
        # Get citation (e.g., "Joel 2:12-18")
        citation_elem = header.find('div', class_='address')
        if citation_elem:
            # Extract text from the citation, it might have links
            citation_text = citation_elem.get_text(strip=True)
            reading['citation'] = citation_text
        
        # Get the actual reading text from content-body
        content = block.find('div', class_='content-body')
        if content:
            # Replace <br> tags with newlines before extracting text
            for br in content.find_all('br'):
                br.replace_with('\n')
            
            # Replace <em> and <strong> tags to preserve spacing
            for tag in content.find_all(['em', 'strong']):
                tag.insert_before(' ')
                tag.insert_after(' ')
            
            # Clean up the text - get all paragraphs
            text_parts = []
            for p in content.find_all('p'):
                text = p.get_text()
                # Clean up extra whitespace while preserving newlines
                lines = [line.strip() for line in text.split('\n')]
                cleaned_text = '\n'.join(line for line in lines if line)
                if cleaned_text:
                    text_parts.append(cleaned_text)
            reading['text'] = '\n\n'.join(text_parts)
        
        if reading:  # Only add if we found something
            readings_data['readings'].append(reading)
    
    # Filter by titles if requested
    if titles:
        readings_data['readings'] = [
            r for r in readings_data['readings'] 
            if r.get('title') in titles
        ]
    
    return readings_data


def format_as_markdown(readings_data):
    """Format readings data as markdown for LLM parsing."""
    if "error" in readings_data:
        return f"Error: {readings_data['error']}"
    
    output = []
    
    # Header
    output.append(f"# Daily Bible Readings - {readings_data['liturgical_date']}")
    output.append(f"**Date:** {readings_data['date']}")
    output.append(f"**Source:** {readings_data['url']}")
    output.append("")
    
    # Each reading
    for reading in readings_data['readings']:
        output.append(f"## {reading['title']}")
        output.append(f"**Citation:** {reading['citation']}")
        output.append("")
        output.append(reading['text'])
        output.append("")
        output.append("---")
        output.append("")
    
    return '\n'.join(output)


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Get daily Bible readings from USCCB')
    parser.add_argument('--date', '-d', help='Date in YYYY-MM-DD format')
    parser.add_argument('--titles', '-t', nargs='+', help='Filter by reading titles (e.g., Gospel "Reading 1")')
    parser.add_argument('--json', action='store_true', help='Output as JSON instead of markdown')
    args = parser.parse_args()
    
    result = get_daily_readings(args.date, args.titles)
    
    # Output format based on flag
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_as_markdown(result))
    
    # Exit with error code if there was an error
    if "error" in result:
        sys.exit(1)
