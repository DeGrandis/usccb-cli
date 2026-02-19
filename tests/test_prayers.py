#!/usr/bin/env python3
"""
Unit tests for prayers module
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.prayers import search_prayers, get_prayer


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
        
        self.assertEqual(result['text'], '')
        self.assertIn('error', result)
        
    @patch('lib.prayers.requests.get')
    def test_get_prayer_request_failure(self, mock_get):
        """Test handling of request failures"""
        mock_get.side_effect = Exception("Network error")
        
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


if __name__ == '__main__':
    unittest.main()
