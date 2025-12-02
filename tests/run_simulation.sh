#!/bin/bash

# MTG Tournament Simulator - Quick Run Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      MTG Draft Tournament Simulator                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if server is running
echo "Checking if server is running..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Server is not running!"
    echo "Please start the server first with: ./start.sh"
    exit 1
fi

echo "✓ Server is running"
echo ""

# Install requirements if needed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r tests/requirements-dev.txt
fi

# Run simulation
cd tests
python3 simulate_tournament.py "$@"

