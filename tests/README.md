# Running Tests

## Quick Start

Run all tests:
```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Or use the test runner script:
```bash
./run_tests.sh
```

## Test Coverage

The test suite includes unit tests for:

- **test_daily_readings.py**: Daily Bible readings scraper
  - Successful retrieval and parsing
  - Date formatting (MMDDYY.cfm)
  - Title filtering
  - Error handling

- **test_mass_times.py**: Mass times and church finder  
  - Geocoding locations (city names, zipcodes)
  - Parish API integration
  - Result limiting
  - Error handling

- **test_prayers.py**: Prayer search and retrieval
  - Prayer search with pagination
  - Individual prayer text extraction
  - Line break preservation
  - Error handling

## Test Strategy

All tests use `unittest.mock` to mock HTTP requests, so they don't hit real APIs during testing. This makes tests:
- Fast (no network calls)
- Reliable (no external dependencies)
- Safe (won't rate-limit APIs)

## Running Individual Test Files

```bash
# Test only daily readings
python3 -m unittest tests.test_daily_readings

# Test only mass times  
python3 -m unittest tests.test_mass_times

# Test only prayers
python3 -m unittest tests.test_prayers
```

## Running Specific Tests

```bash
# Run a single test
python3 -m unittest tests.test_prayers.TestPrayers.test_search_prayers_success
```

## Current Status

Most core functionality is tested. Some edge cases may need additional test coverage.
