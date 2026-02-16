#!/bin/bash
# Test runner script for unit-2-1

set -e

echo "========================================="
echo "Unit 2-1: Base Scraper & HTTP Client Tests"
echo "========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 || echo "Python not found")
echo "Python version: $python_version"
echo ""

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Running tests..."
echo ""

# Run HTTP client tests
echo ">>> Testing HTTP Client..."
python3 -m pytest test_http_client.py -v

echo ""
echo ">>> Testing Base Scraper..."
python3 -m pytest test_base_scraper.py -v

echo ""
echo ">>> Running all scraper tests..."
python3 -m pytest test_*.py -v

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
python3 -m pytest test_http_client.py test_base_scraper.py --tb=no -q

echo ""
echo "All tests completed!"
