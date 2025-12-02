# Quick Start Guide

## Get Running in 3 Steps

### 1. Setup (First Time Only)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
```

### 2. Start Server

```bash
# Option A: Auto start script
./start.sh

# Option B: Manual start
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Server: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### 3. Test with Simulator

```bash
# In a new terminal
cd tests
pip install -r requirements-dev.txt
python simulate_tournament.py --players 8 --speed medium
```

## What You Get

✅ **Fully functional backend** with all API endpoints
✅ **Real-time WebSocket** support for live updates
✅ **Tournament simulator** with configurable bot players
✅ **Complete API documentation** at /docs
✅ **Admin authentication** with JWT tokens
✅ **Round-robin scheduler** with automatic pairing
✅ **Health tracking** with real-time updates
✅ **SQLite database** with all tables created

## Default Credentials

**Admin Password:** `admin123`

⚠️ Change in `backend/.env` before production use!

## Test Scenarios

```bash
# Quick test with 4 players
python tests/simulate_tournament.py --players 4 --speed fast

# Join as a player with 7 bots
python tests/simulate_tournament.py --players 8 --manual-player "YourName"

# Stress test with 20 players
python tests/simulate_tournament.py --players 20 --speed fast
```

## API Examples

### Create Tournament

```bash
# 1. Login
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin123"}'

# 2. Create tournament (use token from step 1)
curl -X POST http://localhost:8000/api/admin/tournament \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Friday Night Draft",
    "draft_type": "Booster Draft",
    "max_players": 8,
    "starting_life": 20
  }'
```

### Join as Player

```bash
curl -X POST http://localhost:8000/api/players/join \
  -H "Content-Type: application/json" \
  -d '{"tournament_id": 1, "name": "Alice"}'
```

### Update Health

```bash
curl -X PUT http://localhost:8000/api/matches/1/health \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "health_change": -5}'
```

## WebSocket Testing

```javascript
// Connect to dashboard
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
  // { type: 'health_update', match_id: 1, player_id: 1, new_health: 15 }
};
```

## File Structure

```
mtgtrack/
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── main.py          # Application entry
│   └── .env             # Configuration
├── tests/               # Testing tools
│   └── simulate_tournament.py
├── start.sh             # Quick start script
└── README.md            # Full documentation
```

## Next Steps

1. **Read Full Docs**: See `README.md` for complete documentation
2. **API Reference**: Visit http://localhost:8000/docs
3. **Build Frontend**: (Pending implementation)
4. **Customize**: Edit `backend/.env` for your needs

## Troubleshooting

### Database Issues
```bash
rm backend/mtg_tournament.db
cd backend && python scripts/init_db.py
```

### Port Already in Use
```bash
# Change port
uvicorn main:app --port 8001
```

### Import Errors
```bash
# Make sure venv is activated
source backend/venv/bin/activate
```

## What's Working

✅ Tournament CRUD
✅ Player registration
✅ Match management
✅ Health tracking
✅ Round-robin scheduling
✅ WebSocket live updates
✅ Admin authentication
✅ Standings calculation
✅ Tournament simulator

## What's Pending

⏳ Frontend (React/TypeScript)
⏳ Admin UI panel
⏳ Player mobile interface
⏳ Live dashboard

The backend API is **100% complete** and ready to use!

## Get Help

- Full documentation: `README.md`
- Technical spec: `PROJECT_SPECIFICATION.md`
- API docs: http://localhost:8000/docs
- Backend README: `backend/README.md`

---

**Have fun hosting tournaments!** 🎮✨
