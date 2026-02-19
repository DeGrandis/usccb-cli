#!/bin/bash
# Run all unit tests

echo "Running unit tests for USCCB CLI..."
echo ""

# Run tests with pytest if available, otherwise use unittest
if command -v pytest &> /dev/null; then
    echo "Using pytest..."
    pytest tests/ -v --tb=short
else
    echo "Using unittest..."
    python3 -m unittest discover -s tests -p 'test_*.py' -v
fi

echo ""
echo "Done!"
