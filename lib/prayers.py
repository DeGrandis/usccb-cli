#!/usr/bin/env python3
"""
USCCB Prayers Scraper

Search for Catholic prayers and retrieve their full text from the USCCB website.
Outputs markdown by default for LLM parsing, or JSON with --json flag.
"""

import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup

BASE_URL = "https://www.usccb.org"


def search_prayers(query, prayer_type="All", office="All", committee="All", items_per_page=100, language="en"):
    """
    Search for prayers on the USCCB website.
    
    Args:
        query: Search keyword(s)
        prayer_type: Type of prayer filter (default: "All")
        office: Office filter (default: "All")
        committee: Committee filter (default: "All")
        items_per_page: Maximum number of results to return (default: 100)
        language: Language filter - 'en' for English, 'es' for Spanish (default: 'en')
        
    Returns:
        dict: Search results with prayer titles and URLs
    """
    # USCCB only accepts specific pagination values: 20, 50, or 100
    # Round up to the nearest valid value to ensure we get enough results
    if items_per_page <= 20:
        fetch_limit = 20
    elif items_per_page <= 50:
        fetch_limit = 50
    else:
        fetch_limit = 100
    
    params = {
        'key': query,
        'items_per_page': fetch_limit
    }
    
    # Add filters if they're not "All"
    if prayer_type and prayer_type != "All":
        params['type'] = prayer_type
    if office and office != "All":
        params['office'] = office
    if committee and committee != "All":
        params['committee'] = committee
    
    try:
        response = requests.get(f'{BASE_URL}/prayers', params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch prayer search results: {str(e)}"}
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    results = {
        "query": query,
        "search_url": response.url,
        "prayers": []
    }
    
    # Find all prayer result items - they're in views-row divs
    prayer_items = soup.find_all('div', class_='views-row')
    
    for item in prayer_items:
        prayer = {}
        
        # Find the title/link - it's in views-field-aggregated-title
        title_field = item.find('p', class_='views-field-aggregated-title')
        
        if title_field:
            link = title_field.find('a', href=True)
            if link:
                prayer['title'] = link.get_text(strip=True)
                prayer['url'] = link['href']
                # Make sure URL is absolute
                if not prayer['url'].startswith('http'):
                    prayer['url'] = BASE_URL + prayer['url']
        
        # Get the type/category if available
        type_field = item.find('span', class_='type')
        if type_field:
            prayer['type'] = type_field.get_text(strip=True)
        
        if prayer.get('title'):
            # Filter by language
            is_spanish = '/es/' in prayer['url']
            if language == 'es' and is_spanish:
                results['prayers'].append(prayer)
            elif language == 'en' and not is_spanish:
                results['prayers'].append(prayer)
    
    # Trim to requested limit
    results['prayers'] = results['prayers'][:items_per_page]
    results['total_results'] = len(results['prayers'])
    
    return results


def get_prayer(url):
    """
    Retrieve the full text of a prayer from its URL.
    
    Args:
        url: Full URL to the prayer page
        
    Returns:
        dict: Prayer details including title and full text
    """
    # Make sure URL is absolute
    if not url.startswith('http'):
        url = BASE_URL + url
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch prayer: {str(e)}", "url": url}
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    result = {
        "url": url,
        "title": None,
        "text": None
    }
    
    # Get the title
    title = soup.find('h1') or soup.find('title')
    if title:
        result['title'] = title.get_text(strip=True).replace(' | USCCB', '')
    
    # Get the prayer text from the article
    article = soup.find('article')
    
    if article:
        # Replace <br> tags with newlines
        for br in article.find_all('br'):
            br.replace_with('\n')
        
        # Get all paragraphs directly from article
        paragraphs = article.find_all('p')
        if paragraphs:
            text_parts = []
            for p in paragraphs:
                text = p.get_text()
                # Clean up extra whitespace while preserving newlines
                lines = [line.strip() for line in text.split('\n')]
                cleaned_text = '\n'.join(line for line in lines if line)
                if cleaned_text:
                    text_parts.append(cleaned_text)
            result['text'] = '\n\n'.join(text_parts)
    
    if not result['text']:
        result['error'] = "Could not extract prayer text from page"
    
    return result


def format_search_as_markdown(result):
    """Format prayer search results as markdown for LLM parsing."""
    if "error" in result:
        return f"Error: {result['error']}"
    
    output = []
    
    # Header
    output.append(f"# Prayer Search Results for: \"{result['query']}\"")
    output.append(f"**Total Results:** {result['total_results']}")
    output.append(f"**Source:** {result['search_url']}")
    output.append("")
    
    # Each prayer
    for i, prayer in enumerate(result['prayers'], 1):
        output.append(f"## {i}. {prayer['title']}")
        if prayer.get('type'):
            output.append(f"**Type:** {prayer['type']}")
        output.append(f"**URL:** {prayer['url']}")
        output.append("")
    
    if not result['prayers']:
        output.append("*No prayers found matching your search.*")
        output.append("")
    
    return '\n'.join(output)


def format_prayer_as_markdown(result):
    """Format prayer text as markdown for LLM parsing."""
    if "error" in result:
        return f"Error: {result['error']}"
    
    output = []
    
    # Header
    output.append(f"# {result['title']}")
    output.append(f"**Source:** {result['url']}")
    output.append("")
    output.append("---")
    output.append("")
    
    # Prayer text
    if result['text']:
        output.append(result['text'])
    
    output.append("")
    output.append("---")
    
    return '\n'.join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Search for Catholic prayers or retrieve prayer text from USCCB'
    )
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for prayers')
    search_parser.add_argument('query', help='Search keyword(s)')
    search_parser.add_argument('--type', default='All', help='Prayer type filter')
    search_parser.add_argument('--limit', type=int, default=20, help='Number of results (default: 20)')
    search_parser.add_argument('--language', default='en', choices=['en', 'es'], help='Language: en (English) or es (Spanish) (default: en)')
    search_parser.add_argument('--json', action='store_true', help='Output as JSON instead of markdown')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get prayer text from URL')
    get_parser.add_argument('url', help='Prayer URL')
    get_parser.add_argument('--json', action='store_true', help='Output as JSON instead of markdown')
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    if args.action == 'search':
        result = search_prayers(args.query, prayer_type=args.type, items_per_page=args.limit, language=args.language)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_search_as_markdown(result))
    elif args.action == 'get':
        result = get_prayer(args.url)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_prayer_as_markdown(result))
    else:
        parser.print_help()
        sys.exit(1)
    
    # Exit with error code if there was an error
    if "error" in result:
        sys.exit(1)
