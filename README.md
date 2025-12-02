# MTG Draft Tournament Tracker

A comprehensive web application for hosting and tracking Magic: The Gathering draft tournaments with real-time match tracking, player profiles, and live dashboard updates.

## Features

### Admin Panel
- Create tournaments with customizable settings
- Generate round-robin schedules automatically
- Monitor all matches in real-time
- Manually edit results or force-end matches
- View tournament history

### Live Dashboard (Desktop)
- Real-time display of current round matches
- Live health tracking for all players
- Player avatars and Magic color indicators
- Current standings table
- Full tournament schedule

### Player Interface (Mobile-Optimized)
- Join tournaments with custom profiles
- Upload avatars or choose presets
- Select Magic colors (W/U/B/R/G)
- View current and upcoming matches
- In-match health counter with +/- controls
- Confirm defeat when health reaches 0

### Technical Features
- **Real-time Updates**: WebSocket-based live updates
- **Round-Robin Scheduling**: Automatic fair pairing generation
- **RESTful API**: Complete API for all operations
- **Mobile-First**: Optimized for mobile player experience
- **Desktop Dashboard**: Large-screen optimized live view

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (optional, for frontend if built)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run server
uvicorn main:app --reload
```

Server runs at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

Default admin password: `admin123` (change in `.env`)

### 2. Test with Simulator

```bash
# In a new terminal
cd tests
pip install -r requirements-dev.txt

# Run simulation with 8 bot players
python simulate_tournament.py --players 8 --speed medium

# Or join as a player with 7 bots
python simulate_tournament.py --players 8 --manual-player "YourName"
```

## Usage Guide

### Creating a Tournament

#### Option 1: Using the API

```bash
# 1. Login as admin
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin123"}'

# Save the token from response

# 2. Create tournament
curl -X POST http://localhost:8000/api/admin/tournament \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Friday Night Draft",
    "draft_type": "Booster Draft",
    "max_players": 8,
    "starting_life": 20
  }'

# 3. Players join
curl -X POST http://localhost:8000/api/players/join \
  -H "Content-Type: application/json" \
  -d '{"tournament_id": 1, "name": "Alice"}'

# 4. Generate schedule (after all players joined)
curl -X POST http://localhost:8000/api/admin/tournament/1/generate-schedule \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Option 2: Using the Simulator

```bash
# Automatic tournament with bots
python tests/simulate_tournament.py --players 8 --speed fast
```

### Player Workflow

1. **Join Tournament**
   ```bash
   POST /api/players/join
   {
     "tournament_id": 1,
     "name": "Alice"
   }
   ```

2. **Update Profile**
   ```bash
   PUT /api/players/{player_id}/profile
   FormData: {
     colors: ["W", "U"],
     avatar: <file> or preset_id: "avatar_1"
   }
   ```

3. **View Matches**
   ```bash
   GET /api/players/{player_id}/matches
   ```

4. **Join Match**
   ```bash
   POST /api/matches/{match_id}/join
   {"player_id": 1}
   ```

5. **Update Health**
   ```bash
   PUT /api/matches/{match_id}/health
   {"player_id": 1, "health_change": -5}
   ```

6. **Confirm Defeat**
   ```bash
   POST /api/matches/{match_id}/defeat
   {"player_id": 1}
   ```

### Live Dashboard

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch(message.type) {
    case 'health_update':
      // Update player health display
      break;
    case 'match_complete':
      // Mark match as complete
      break;
    case 'round_complete':
      // Advance to next round
      break;
  }
};
```

## Project Structure

```
mtgtrack/
├── backend/                  # FastAPI backend
│   ├── api/                 # API endpoints
│   │   ├── admin.py
│   │   ├── players.py
│   │   ├── matches.py
│   │   ├── tournament.py
│   │   └── websockets.py
│   ├── database/            # Database config
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── auth.py
│   │   ├── scheduler.py
│   │   ├── tournament_service.py
│   │   └── match_service.py
│   ├── scripts/             # Utility scripts
│   │   └── init_db.py
│   ├── main.py
│   └── requirements.txt
├── tests/                   # Testing tools
│   ├── simulate_tournament.py
│   └── requirements-dev.txt
├── PROJECT_SPECIFICATION.md # Full technical spec
└── README.md
```

## API Reference

### Complete Endpoint List

**Admin** (requires JWT token)
- `POST /api/admin/login` - Get admin token
- `POST /api/admin/tournament` - Create tournament
- `POST /api/admin/tournament/{id}/generate-schedule` - Generate schedule
- `POST /api/admin/tournament/{id}/next-round` - Advance round manually
- `PUT /api/admin/match/{id}/result` - Update match result
- `DELETE /api/admin/match/{id}/force-end` - Force end match
- `GET /api/admin/tournaments/history` - View history

**Players**
- `POST /api/players/join` - Join tournament
- `PUT /api/players/{id}/profile` - Update profile (avatar, colors)
- `GET /api/players/{id}/profile` - Get profile with stats
- `GET /api/players/{id}/matches` - Get current & upcoming matches

**Matches**
- `POST /api/matches/{id}/join` - Join assigned match
- `PUT /api/matches/{id}/health` - Update health
- `POST /api/matches/{id}/defeat` - Confirm defeat

**Tournament**
- `GET /api/tournament/current` - Current tournament info
- `GET /api/tournament/{id}/standings` - Rankings
- `GET /api/tournament/{id}/schedule` - Full schedule
- `GET /api/tournament/{id}/current-round` - Live round data

**WebSockets**
- `WS /ws/dashboard` - Dashboard real-time updates
- `WS /ws/match/{id}` - Match-specific updates

## Configuration

### Environment Variables (.env)

```bash
DATABASE_URL=sqlite:///./mtg_tournament.db
ADMIN_PASSWORD=your_secure_password
JWT_SECRET=your_random_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
UPLOAD_DIR=./uploads
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Testing

### Simulator Options

```bash
# Quick 4-player test
python tests/simulate_tournament.py --players 4 --speed fast

# Join as player with 7 bots
python tests/simulate_tournament.py --players 8 --manual-player "YourName"

# Stress test with 20 players
python tests/simulate_tournament.py --players 20 --speed fast

# Slow realistic gameplay
python tests/simulate_tournament.py --players 6 --speed slow
```

### What the Simulator Tests

✅ Tournament creation
✅ Player registration (bulk)
✅ Profile updates (colors)
✅ Round-robin schedule generation
✅ Match joining
✅ Real-time health updates via API
✅ Defeat confirmation
✅ Round completion detection
✅ Multi-round tournament flow
✅ Final standings calculation
✅ Concurrent match simulation
✅ WebSocket broadcasting (visible on dashboard)

## Database Schema

### Tables

- **tournaments** - Tournament configuration and state
- **players** - Player profiles and stats
- **rounds** - Tournament rounds
- **matches** - Individual matches
- **match_events** - Health change log
- **admin_config** - Admin credentials (single row)

### Relationships

```
Tournament (1) → (many) Players
Tournament (1) → (many) Rounds
Round (1) → (many) Matches
Match (2) → (1) Player (player1, player2)
Match (1) → (many) MatchEvents
```

## Round-Robin Algorithm

The scheduler ensures:
- Every player plays every other player exactly once
- Handles odd numbers of players (bye rounds)
- No repeat pairings
- Balanced distribution

Example for 8 players: 7 rounds, 4 matches per round, 28 total matches

## Deployment

### Production Checklist

1. **Security**
   - [ ] Change `ADMIN_PASSWORD`
   - [ ] Generate secure `JWT_SECRET`
   - [ ] Enable HTTPS
   - [ ] Configure firewall

2. **Server**
   ```bash
   # Use production ASGI server
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Reverse Proxy** (nginx example)
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

4. **Database Backups**
   ```bash
   # Daily backup
   cp mtg_tournament.db backups/mtg_tournament_$(date +%Y%m%d).db
   ```

## Troubleshooting

### Database Reset

```bash
cd backend
rm mtg_tournament.db
python scripts/init_db.py
```

### WebSocket Connection Issues

1. Check `ALLOWED_ORIGINS` in `.env`
2. Ensure no firewall blocking WebSocket connections
3. Try polling as fallback in production

### Player Registration Fails

- Tournament might be full (check `max_players`)
- Tournament status must be "registration"
- Player name must be unique within tournament

### Matches Not Advancing

- All matches must complete before round advances
- Check for stuck matches in dashboard
- Admin can force-end matches if needed

## Development Roadmap

### Future Enhancements (v2.0)

- [ ] Multiple simultaneous tournaments
- [ ] In-app booster draft (pack passing)
- [ ] Deck builder integration
- [ ] Enhanced statistics & analytics
- [ ] Player chat during matches
- [ ] Push notifications
- [ ] Swiss pairing alternatives
- [ ] Mobile apps (iOS/Android)
- [ ] Tiebreaker systems
- [ ] Email/SMS notifications

## Technical Stack

**Backend:**
- FastAPI (Python)
- SQLAlchemy (ORM)
- SQLite (Database)
- WebSockets (Real-time)
- JWT (Authentication)
- Pydantic (Validation)

**Frontend:** (To be implemented)
- React 18+ with TypeScript
- Vite (Build tool)
- TailwindCSS (Styling)
- WebSocket client

## Contributing

This project follows the specification in `PROJECT_SPECIFICATION.md`.

### Adding Features

1. Update models if needed (`backend/models/`)
2. Add/update schemas (`backend/schemas/`)
3. Implement service logic (`backend/services/`)
4. Create API endpoints (`backend/api/`)
5. Update documentation

## License

MIT License - See LICENSE file

## Support

For issues or questions:
- Review `PROJECT_SPECIFICATION.md` for detailed technical docs
- Check API docs at `/docs` endpoint
- Review this README

## Credits

Created for hosting Magic: The Gathering draft tournaments with real-time tracking and live updates.

---

**Current Version:** 1.0.0
**Status:** Backend Complete, Frontend Pending
**Last Updated:** 2025-12-02
