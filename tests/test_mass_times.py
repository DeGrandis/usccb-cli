#!/usr/bin/env python3
"""
Unit tests for mass_times module
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.mass_times import geocode_location, get_mass_times, format_as_markdown


class TestMassTimes(unittest.TestCase):
    
    @patch('lib.mass_times.requests.get')
    def test_geocode_location_success(self, mock_get):
        """Test successful geocoding of a location"""
        mock_response = Mock()
        mock_response.json.return_value = [{
            'lat': '42.3601',
            'lon': '-71.0589',
            'display_name': 'Boston, MA, USA'
        }]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = geocode_location('Boston, MA')
        
        self.assertEqual(result, (42.3601, -71.0589))
        
    @patch('lib.mass_times.requests.get')
    def test_geocode_location_zipcode(self, mock_get):
        """Test geocoding with a zipcode"""
        mock_response = Mock()
        mock_response.json.return_value = [{
            'lat': '40.7589',
            'lon': '-73.9851',
            'display_name': 'New York, NY 10001'
        }]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = geocode_location('10001')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)  # Should be a tuple of (lat, lon)
        
    @patch('lib.mass_times.requests.get')
    def test_geocode_location_not_found(self, mock_get):
        """Test geocoding when location is not found"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = geocode_location('InvalidLocationXYZ123')
        
        self.assertIsNone(result)
        
    @patch('lib.mass_times.requests.get')
    def test_get_mass_times_success(self, mock_get):
        """Test successful retrieval of Mass times"""
        # Mock geocoding response
        geocode_response = Mock()
        geocode_response.json.return_value = [{
            'lat': '42.3601',
            'lon': '-71.0589',
            'display_name': 'Boston, MA'
        }]
        geocode_response.raise_for_status = Mock()
        
        # Mock parish API response - returns array directly, not wrapped in 'data'
        parish_response = Mock()
        parish_response.json.return_value = [
            {
                'name': 'St. Patrick Church',
                'church_address_street': '123 Main St',
                'church_address_city': 'Boston',
                'church_address_state': 'MA',
                'distance': 0.5,
                'church_worship_times': [
                    {'day': 'Sunday', 'time': '9:00 AM'}
                ]
            },
            {
                'name': 'Holy Name Church',
                'church_address_street': '456 Oak Ave',
                'church_address_city': 'Boston',
                'church_address_state': 'MA',
                'distance': 1.2,
                'church_worship_times': []
            }
        ]
        parish_response.raise_for_status = Mock()
        
        # Set up mock to return different responses for different URLs
        def side_effect(url, *args, **kwargs):
            if 'nominatim' in url:
                return geocode_response
            else:
                return parish_response
        
        mock_get.side_effect = side_effect
        
        result = get_mass_times('Boston, MA')
        
        self.assertIn('churches', result)
        self.assertEqual(len(result['churches']), 2)
        self.assertEqual(result['churches'][0]['name'], 'St. Patrick Church')
        self.assertEqual(result['location_searched'], 'Boston, MA')
        
    @patch('lib.mass_times.requests.get')
    def test_get_mass_times_with_limit(self, mock_get):
        """Test limiting the number of results"""
        geocode_response = Mock()
        geocode_response.json.return_value = [{
            'lat': '42.3601',
            'lon': '-71.0589',
            'display_name': 'Boston, MA'
        }]
        geocode_response.raise_for_status = Mock()
        
        parish_response = Mock()
        parish_response.json.return_value = [
            {'name': f'Church {i}', 'distance': i * 0.5} 
            for i in range(10)
        ]
        parish_response.raise_for_status = Mock()
        
        def side_effect(url, *args, **kwargs):
            if 'nominatim' in url:
                return geocode_response
            else:
                return parish_response
        
        mock_get.side_effect = side_effect
        
        result = get_mass_times('Boston, MA', limit=3)
        
        self.assertEqual(len(result['churches']), 3)
        
    @patch('lib.mass_times.requests.get')
    def test_get_mass_times_geocoding_fails(self, mock_get):
        """Test when geocoding fails"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_mass_times('InvalidLocation123')
        
        self.assertIn('error', result)
        self.assertIn('coordinates', result['error'].lower())
    
    def test_format_as_markdown(self):
        """Test markdown formatting of mass times"""
        mock_result = {
            "location_searched": "Boston, MA",
            "coordinates": {"latitude": 42.3601, "longitude": -71.0589},
            "page": 1,
            "total_results": 1,
            "churches": [
                {
                    "name": "St. Patrick",
                    "church_address_street_address": "123 Main St",
                    "church_address_city_name": "Boston",
                    "church_address_providence_name": "Massachusetts",
                    "church_address_postal_code": "02108",
                    "phone_number": "(617) 555-1234",
                    "url": "www.stpatrick.org",
                    "distance": "0.5",
                    "church_worship_times": [
                        {
                            "day_of_week": "Sunday",
                            "service_typename": "Weekend",
                            "time_start": "09:00:00",
                            "comment": "",
                            "language": "English"
                        },
                        {
                            "day_of_week": "Saturday",
                            "service_typename": "Confessions",
                            "time_start": "15:00:00",
                            "comment": "Before Mass",
                            "language": ""
                        }
                    ]
                }
            ]
        }
        
        markdown = format_as_markdown(mock_result)
        
        self.assertIn("# Catholic Churches Near Boston, MA", markdown)
        self.assertIn("**Coordinates:** 42.3601, -71.0589", markdown)
        self.assertIn("**Results:** 1 churches", markdown)
        self.assertIn("## 1. St. Patrick", markdown)
        self.assertIn("**Address:** 123 Main St", markdown)
        self.assertIn("**Location:** Boston, Massachusetts 02108", markdown)
        self.assertIn("**Phone:** (617) 555-1234", markdown)
        self.assertIn("**Website:** www.stpatrick.org", markdown)
        self.assertIn("**Distance:** 0.5 miles", markdown)
        self.assertIn("**Mass Times:**", markdown)
        self.assertIn("**Sunday:**", markdown)
        self.assertIn("09:00", markdown)
        self.assertIn("**Saturday:**", markdown)
        self.assertIn("15:00 (Confessions) - Before Mass", markdown)
    
    def test_format_as_markdown_error(self):
        """Test markdown formatting of error"""
        error_result = {
            "error": "Could not find location",
            "location_searched": "Invalid"
        }
        
        markdown = format_as_markdown(error_result)
        
        self.assertEqual(markdown, "Error: Could not find location")


if __name__ == '__main__':
    unittest.main()
