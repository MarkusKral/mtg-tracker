# MTG Draft Tournament Tracker - Backend

FastAPI backend for tracking Magic: The Gathering draft tournaments with real-time updates.

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `ADMIN_PASSWORD` - Admin panel password
- `JWT_SECRET` - Random secret key for JWT tokens

### 3. Initialize Database

```bash
python scripts/init_db.py
```

This creates the database and admin user.

### 4. Run Server

```bash
uvicorn main:app --reload
```

Server runs at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## API Endpoints

### Admin
- `POST /api/admin/login` - Admin login
- `POST /api/admin/tournament` - Create tournament
- `POST /api/admin/tournament/{id}/generate-schedule` - Generate schedule
- `POST /api/admin/tournament/{id}/next-round` - Advance round
- `PUT /api/admin/match/{id}/result` - Update match result
- `DELETE /api/admin/match/{id}/force-end` - Force end match
- `GET /api/admin/tournaments/history` - Tournament history

### Players
- `POST /api/players/join` - Join tournament
- `PUT /api/players/{id}/profile` - Update profile
- `GET /api/players/{id}/profile` - Get profile
- `GET /api/players/{id}/matches` - Get player matches

### Matches
- `POST /api/matches/{id}/join` - Join match
- `PUT /api/matches/{id}/health` - Update health
- `POST /api/matches/{id}/defeat` - Confirm defeat

### Tournament
- `GET /api/tournament/current` - Get current tournament
- `GET /api/tournament/{id}/standings` - Get standings
- `GET /api/tournament/{id}/schedule` - Get schedule
- `GET /api/tournament/{id}/current-round` - Get current round

### WebSockets
- `WS /ws/dashboard` - Live dashboard updates
- `WS /ws/match/{id}` - Match-specific updates

## Project Structure

```
backend/
├── api/              # API endpoints
│   ├── admin.py
│   ├── players.py
│   ├── matches.py
│   ├── tournament.py
│   └── websockets.py
├── database/         # Database configuration
│   └── database.py
├── models/           # SQLAlchemy models
│   ├── tournament.py
│   ├── player.py
│   ├── round.py
│   ├── match.py
│   └── admin.py
├── schemas/          # Pydantic schemas
│   ├── tournament.py
│   ├── player.py
│   ├── match.py
│   └── admin.py
├── services/         # Business logic
│   ├── auth.py
│   ├── scheduler.py
│   ├── tournament_service.py
│   └── match_service.py
├── scripts/          # Utility scripts
│   └── init_db.py
├── main.py           # FastAPI application
└── requirements.txt
```

## Development

### Run Tests

```bash
pytest
```

### Format Code

```bash
black .
```

### Lint

```bash
flake8
```

## Production Deployment

1. Change `ADMIN_PASSWORD` and `JWT_SECRET` in `.env`
2. Use a production ASGI server:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

3. Set up reverse proxy (nginx)
4. Enable HTTPS
5. Configure firewall
6. Set up database backups

## Troubleshooting

### Database Issues

Reset database:
```bash
rm mtg_tournament.db
python scripts/init_db.py
```

### WebSocket Issues

Check CORS settings in `.env` ALLOWED_ORIGINS.

### Import Errors

Ensure you're in the backend directory and venv is activated.
