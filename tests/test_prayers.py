#!/usr/bin/env python3
"""
Unit tests for prayers module
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.prayers import search_prayers, get_prayer, format_search_as_markdown, format_prayer_as_markdown


class TestPrayers(unittest.TestCase):
    
    @patch('lib.prayers.requests.get')
    def test_search_prayers_success(self, mock_get):
        """Test successful prayer search"""
        mock_html = '''
        <html>
            <div class="teaser views-row">
                <p class="views-field views-field-aggregated-title">
                    <a href="https://www.usccb.org/prayers/hail-mary">Hail Mary</a>
                </p>
                <span class="type">Basic Prayers</span>
            </div>
            <div class="teaser views-row">
                <p class="views-field views-field-aggregated-title">
                    <a href="https://www.usccb.org/prayers/our-father">Our Father</a>
                </p>
                <span class="type">Basic Prayers</span>
            </div>
            <div class="teaser views-row">
                <p class="views-field views-field-aggregated-title">
                    <a href="https://www.usccb.org/prayers/prayer-for-peace">Prayer for Peace</a>
                </p>
                <span class="type">World Prayers</span>
            </div>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.url = 'https://www.usccb.org/prayers?key=mary&items_per_page=20'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = search_prayers('mary', items_per_page=20)
        
        self.assertIn('prayers', result)
        self.assertEqual(result['query'], 'mary')
        self.assertGreater(len(result['prayers']), 0)
        
        # Check first result structure
        first_prayer = result['prayers'][0]
        self.assertIn('title', first_prayer)
        self.assertIn('url', first_prayer)
        self.assertIn('type', first_prayer)
        
    @patch('lib.prayers.requests.get')
    def test_search_prayers_with_limit(self, mock_get):
        """Test search with result limit"""
        # Create 10 mock results
        mock_rows = '\n'.join([
            f'''<div class="teaser views-row">
                <p class="views-field views-field-aggregated-title">
                    <a href="https://www.usccb.org/prayers/prayer-{i}">Prayer {i}</a>
                </p>
                <span class="type">Test</span>
            </div>'''
            for i in range(10)
        ])
        
        mock_response = Mock()
        mock_response.content = f'<html>{mock_rows}</html>'.encode('utf-8')
        mock_response.url = 'https://www.usccb.org/prayers?key=test&items_per_page=20'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = search_prayers('test', items_per_page=3)
        
        self.assertEqual(len(result['prayers']), 3)
        self.assertEqual(result['total_results'], 3)
        
    @patch('lib.prayers.requests.get')
    def test_search_prayers_pagination_values(self, mock_get):
        """Test that pagination values are correctly mapped"""
        mock_response = Mock()
        mock_response.content = b'<html></html>'
        mock_response.url = 'https://www.usccb.org/prayers'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test that small limits use 20
        search_prayers('test', items_per_page=10)
        call_args = mock_get.call_args[1]['params']
        self.assertEqual(call_args['items_per_page'], 20)
        
        # Test that medium limits use 50
        search_prayers('test', items_per_page=30)
        call_args = mock_get.call_args[1]['params']
        self.assertEqual(call_args['items_per_page'], 50)
        
        # Test that large limits use 100
        search_prayers('test', items_per_page=75)
        call_args = mock_get.call_args[1]['params']
        self.assertEqual(call_args['items_per_page'], 100)
        
    @patch('lib.prayers.requests.get')
    def test_search_prayers_no_results(self, mock_get):
        """Test search with no results"""
        mock_response = Mock()
        mock_response.content = b'<html><body>No results</body></html>'
        mock_response.url = 'https://www.usccb.org/prayers?key=zzz&items_per_page=20'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = search_prayers('zzz')
        
        self.assertEqual(len(result['prayers']), 0)
        self.assertEqual(result['total_results'], 0)
        
    @patch('lib.prayers.requests.get')
    def test_get_prayer_success(self, mock_get):
        """Test successful retrieval of prayer text"""
        mock_html = '''
        <html>
            <article>
                <h1>Hail Mary</h1>
                <p>Hail, Mary, full of grace,<br/>
                the Lord is with thee.</p>
                <p>Blessed art thou among women<br/>
                and blessed is the fruit of thy womb, Jesus.</p>
                <p>Amen.</p>
            </article>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_prayer('https://www.usccb.org/prayers/hail-mary')
        
        self.assertEqual(result['title'], 'Hail Mary')
        self.assertIn('Hail, Mary, full of grace', result['text'])
        self.assertIn('Blessed art thou among women', result['text'])
        self.assertNotIn('error', result)
        
    @patch('lib.prayers.requests.get')
    def test_get_prayer_with_relative_url(self, mock_get):
        """Test get_prayer converts relative URLs to absolute"""
        mock_response = Mock()
        mock_response.content = b'<html><article><h1>Test</h1><p>Text</p></article></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_prayer('/prayers/test-prayer')
        
        # Verify the full URL was called
        called_url = mock_get.call_args[0][0]
        self.assertTrue(called_url.startswith('http'))
        self.assertIn('usccb.org', called_url)
        
    @patch('lib.prayers.requests.get')
    def test_get_prayer_no_text_found(self, mock_get):
        """Test when prayer text cannot be extracted"""
        mock_response = Mock()
        mock_response.content = b'<html><body>No article content</body></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_prayer('https://www.usccb.org/prayers/test')
        
        self.assertIsNone(result['text'])
        self.assertIn('error', result)
        
    @patch('lib.prayers.requests.get')
    def test_get_prayer_request_failure(self, mock_get):
        """Test handling of request failures"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = get_prayer('https://www.usccb.org/prayers/test')
        
        self.assertIn('error', result)
        
    @patch('lib.prayers.requests.get')
    def test_get_prayer_preserves_line_breaks(self, mock_get):
        """Test that line breaks in prayers are preserved"""
        mock_html = '''
        <html>
            <article>
                <h1>Test Prayer</h1>
                <p>Line one<br/>
                Line two<br/>
                Line three</p>
            </article>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_prayer('https://www.usccb.org/prayers/test')
        
        # Check that newlines are preserved
        self.assertIn('\n', result['text'])
        self.assertIn('Line one', result['text'])
        self.assertIn('Line two', result['text'])
    
    def test_format_search_as_markdown(self):
        """Test markdown formatting of prayer search results"""
        mock_result = {
            "query": "peace",
            "search_url": "https://www.usccb.org/prayers?key=peace",
            "total_results": 2,
            "prayers": [
                {
                    "title": "Prayer for Peace",
                    "url": "https://www.usccb.org/prayers/prayer-peace",
                    "type": "World Prayers"
                },
                {
                    "title": "St. Francis Prayer",
                    "url": "https://www.usccb.org/prayers/st-francis",
                    "type": "Saint Prayers"
                }
            ]
        }
        
        markdown = format_search_as_markdown(mock_result)
        
        self.assertIn('# Prayer Search Results for: "peace"', markdown)
        self.assertIn("**Total Results:** 2", markdown)
        self.assertIn("**Source:**", markdown)
        self.assertIn("## 1. Prayer for Peace", markdown)
        self.assertIn("**Type:** World Prayers", markdown)
        self.assertIn("**URL:** https://www.usccb.org/prayers/prayer-peace", markdown)
        self.assertIn("## 2. St. Francis Prayer", markdown)
    
    def test_format_search_as_markdown_no_results(self):
        """Test markdown formatting when no prayers found"""
        mock_result = {
            "query": "xyz123",
            "search_url": "https://www.usccb.org/prayers?key=xyz123",
            "total_results": 0,
            "prayers": []
        }
        
        markdown = format_search_as_markdown(mock_result)
        
        self.assertIn("*No prayers found matching your search.*", markdown)
    
    def test_format_search_as_markdown_error(self):
        """Test markdown formatting of search error"""
        error_result = {
            "error": "Network failure"
        }
        
        markdown = format_search_as_markdown(error_result)
        
        self.assertEqual(markdown, "Error: Network failure")
    
    def test_format_prayer_as_markdown(self):
        """Test markdown formatting of prayer text"""
        mock_result = {
            "title": "Hail Mary",
            "url": "https://www.usccb.org/prayers/hail-mary",
            "text": "Hail, Mary, full of grace,\nthe Lord is with thee.\n\nBlessed art thou among women\nand blessed is the fruit of thy womb, Jesus.\n\nAmen."
        }
        
        markdown = format_prayer_as_markdown(mock_result)
        
        self.assertIn("# Hail Mary", markdown)
        self.assertIn("**Source:** https://www.usccb.org/prayers/hail-mary", markdown)
        self.assertIn("---", markdown)
        self.assertIn("Hail, Mary, full of grace", markdown)
        self.assertIn("Blessed art thou among women", markdown)
        self.assertIn("Amen.", markdown)
    
    def test_format_prayer_as_markdown_error(self):
        """Test markdown formatting of prayer retrieval error"""
        error_result = {
            "error": "Prayer not found",
            "url": "https://www.usccb.org/prayers/missing"
        }
        
        markdown = format_prayer_as_markdown(error_result)
        
        self.assertEqual(markdown, "Error: Prayer not found")


if __name__ == '__main__':
    unittest.main()
