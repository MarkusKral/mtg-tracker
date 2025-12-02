#!/bin/bash

# MTG Tournament Tracker - Quick Start Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     MTG Draft Tournament Tracker - Quick Start          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if backend is set up
if [ ! -d "backend/venv" ]; then
    echo "Setting up backend for the first time..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python scripts/init_db.py
    cd ..
    echo "✓ Backend setup complete!"
    echo ""
fi

# Start backend
echo "Starting backend server..."
cd backend
source venv/bin/activate
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

echo "✓ Backend started at http://localhost:8000"
echo "✓ API docs available at http://localhost:8000/docs"
echo ""
echo "Admin credentials:"
# Read password from .env file if it exists
if [ -f "backend/.env" ]; then
    ADMIN_PASS=$(grep "^ADMIN_PASSWORD=" backend/.env | cut -d'=' -f2)
    if [ -n "$ADMIN_PASS" ]; then
        echo "  Password: $ADMIN_PASS"
    else
        echo "  Password: admin123 (default)"
    fi
else
    echo "  Password: admin123 (default)"
fi
echo "  (Change in backend/.env)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping server...'; kill $BACKEND_PID; exit" INT
wait $BACKEND_PID
