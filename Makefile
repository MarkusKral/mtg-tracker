.PHONY: help setup start stop test simulate clean

help:
	@echo "MTG Draft Tournament Tracker - Available Commands"
	@echo ""
	@echo "  make setup      - Initial setup (install dependencies, init database)"
	@echo "  make start      - Start the backend server"
	@echo "  make test       - Run tournament simulator (8 players, medium speed)"
	@echo "  make simulate   - Interactive simulator menu"
	@echo "  make clean      - Clean database and caches"
	@echo "  make reset      - Reset database"
	@echo ""

setup:
	@echo "Setting up backend..."
	cd backend && python3 -m venv venv
	cd backend && ./venv/bin/pip install -r requirements.txt
	cd backend && ./venv/bin/python scripts/init_db.py
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next: make start"

start:
	@echo "Starting backend server..."
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo ""
	cd backend && ./venv/bin/uvicorn main:app --reload

test:
	@echo "Running tournament simulator with 8 players..."
	cd tests && python3 simulate_tournament.py --players 8 --speed medium

simulate:
	@echo "Tournament Simulator Options:"
	@echo ""
	@echo "1. Quick test (4 players, fast)"
	@echo "2. Standard test (8 players, medium)"
	@echo "3. Join as player (7 bots + you)"
	@echo "4. Stress test (20 players, fast)"
	@echo ""
	@read -p "Choice (1-4): " choice; \
	case $$choice in \
		1) cd tests && python3 simulate_tournament.py --players 4 --speed fast;; \
		2) cd tests && python3 simulate_tournament.py --players 8 --speed medium;; \
		3) read -p "Your name: " name; cd tests && python3 simulate_tournament.py --players 8 --manual-player "$$name";; \
		4) cd tests && python3 simulate_tournament.py --players 20 --speed fast;; \
		*) echo "Invalid choice";; \
	esac

clean:
	@echo "Cleaning caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Cleaned"

reset:
	@echo "Resetting database..."
	rm -f backend/mtg_tournament.db
	cd backend && ./venv/bin/python scripts/init_db.py
	@echo "✓ Database reset"
