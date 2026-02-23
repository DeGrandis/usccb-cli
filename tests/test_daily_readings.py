#!/usr/bin/env python3
"""
Unit tests for daily_readings module
"""

import unittest
from unittest.mock import patch, Mock
from datetime import datetime
import sys
import os

# Add parent directory to path so we can import lib modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.daily_readings import get_daily_readings, format_as_markdown


class TestDailyReadings(unittest.TestCase):
    
    @patch('lib.daily_readings.requests.get')
    def test_get_daily_readings_success(self, mock_get):
        """Test successful retrieval of daily readings"""
        # Mock HTML response matching actual USCCB structure
        mock_html = '''
        <html>
            <head>
                <meta property="og:title" content="Ash Wednesday | USCCB" />
            </head>
            <div class="b-verse">
                <div class="content-header">
                    <h3 class="name">Reading 1</h3>
                    <div class="address">Joel 2:12-18</div>
                </div>
                <div class="content-body">
                    <p>Even now, says the LORD,<br/>
                    return to me with your whole heart.</p>
                </div>
            </div>
            <div class="b-verse">
                <div class="content-header">
                    <h3 class="name">Gospel</h3>
                    <div class="address">Matthew 6:1-6, 16-18</div>
                </div>
                <div class="content-body">
                    <p>Jesus said to his disciples:<br/>
                    "Take care not to perform righteous deeds."</p>
                </div>
            </div>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test with today's date
        result = get_daily_readings()
        
        self.assertIn('readings', result)
        self.assertEqual(len(result['readings']), 2)
        self.assertEqual(result['readings'][0]['title'], 'Reading 1')
        self.assertEqual(result['readings'][0]['citation'], 'Joel 2:12-18')
        self.assertIn('return to me with your whole heart', result['readings'][0]['text'])
        
    @patch('lib.daily_readings.requests.get')
    def test_get_daily_readings_with_date(self, mock_get):
        """Test retrieval with specific date"""
        mock_response = Mock()
        mock_response.content = b'<html><div class="b-verse"></div></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test with specific date
        result = get_daily_readings(date='2026-02-18')
        
        # Verify the URL was called with correct date format (021826.cfm)
        called_url = mock_get.call_args[0][0]
        self.assertIn('021826.cfm', called_url)
        
    @patch('lib.daily_readings.requests.get')
    def test_get_daily_readings_with_title_filter(self, mock_get):
        """Test filtering by specific titles"""
        mock_html = '''
        <html>
            <div class="b-verse">
                <div class="content-header">
                    <h3 class="name">Reading 1</h3>
                    <div class="address">Joel 1:1</div>
                </div>
                <div class="content-body"><p>Text 1</p></div>
            </div>
            <div class="b-verse">
                <div class="content-header">
                    <h3 class="name">Gospel</h3>
                    <div class="address">Matt 1:1</div>
                </div>
                <div class="content-body"><p>Gospel text</p></div>
            </div>
            <div class="b-verse">
                <div class="content-header">
                    <h3 class="name">Responsorial Psalm</h3>
                    <div class="address">Psalm 51</div>
                </div>
                <div class="content-body"><p>Psalm text</p></div>
            </div>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test with title filter
        result = get_daily_readings(titles=['Gospel', 'Reading 1'])
        
        self.assertEqual(len(result['readings']), 2)
        titles = [r['title'] for r in result['readings']]
        self.assertIn('Gospel', titles)
        self.assertIn('Reading 1', titles)
        self.assertNotIn('Responsorial Psalm', titles)
        
    @patch('lib.daily_readings.requests.get')
    def test_get_daily_readings_request_failure(self, mock_get):
        """Test handling of request failures"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = get_daily_readings()
        
        self.assertIn('error', result)
        self.assertIn('Network error', result['error'])
        
    @patch('lib.daily_readings.requests.get')
    def test_get_daily_readings_empty_response(self, mock_get):
        """Test handling of empty/malformed HTML"""
        mock_response = Mock()
        mock_response.content = b'<html><body>No readings found</body></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_daily_readings()
        
        self.assertIn('readings', result)
        self.assertEqual(len(result['readings']), 0)
    
    def test_format_as_markdown(self):
        """Test markdown formatting of readings"""
        test_data = {
            "date": "2026-02-22",
            "url": "https://bible.usccb.org/bible/readings/022226.cfm",
            "liturgical_date": "First Sunday of Lent",
            "readings": [
                {
                    "title": "Gospel",
                    "citation": "Matthew 4:1-11",
                    "text": "Jesus was led by the Spirit into the desert\nto be tempted by the devil."
                }
            ]
        }
        
        markdown = format_as_markdown(test_data)
        
        # Check for markdown structure
        self.assertIn('# Daily Bible Readings - First Sunday of Lent', markdown)
        self.assertIn('**Date:** 2026-02-22', markdown)
        self.assertIn('**Source:** https://bible.usccb.org/bible/readings/022226.cfm', markdown)
        self.assertIn('## Gospel', markdown)
        self.assertIn('**Citation:** Matthew 4:1-11', markdown)
        self.assertIn('Jesus was led by the Spirit into the desert', markdown)
        self.assertIn('---', markdown)
    
    def test_format_as_markdown_error(self):
        """Test markdown formatting with error"""
        test_data = {"error": "Network timeout"}
        
        markdown = format_as_markdown(test_data)
        
        self.assertEqual(markdown, "Error: Network timeout")


if __name__ == '__main__':
    unittest.main()
