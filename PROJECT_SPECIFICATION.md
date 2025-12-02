# MTG Draft Tournament Tracker - Technical Specification

## Project Overview

A web application for hosting and tracking Magic: The Gathering draft tournaments with real-time match tracking, player profiles, and live dashboard updates.

---

## System Architecture

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (REST API + WebSocket support)
- SQLAlchemy (ORM)
- SQLite (Database)
- Uvicorn (ASGI server)
- Python-multipart (file uploads)
- Pydantic (validation)

**Frontend:**
- React 18+ with TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- WebSocket client for real-time updates
- React Router (navigation)
- Axios (HTTP client)

**Deployment:**
- Single machine deployment
- Docker Compose (optional but recommended)
- Nginx reverse proxy (optional)

---

## Application Components

### 1. Admin Panel
- **Access:** Special URL (`/admin`) with password protection
- **Features:**
  - Create new tournament with configuration
  - View player registrations
  - Generate round-robin schedule
  - Advance to next round (automatic when all matches complete)
  - Edit match results manually
  - Force-end matches
  - View tournament history
  - Export tournament data

### 2. Live Dashboard (Desktop)
- **Access:** Public URL (`/dashboard`)
- **Features:**
  - Real-time display of current round
  - Show all pairings for current round
  - Display player avatars, colors, and live health counters
  - Current standings table (wins/losses/points)
  - Tournament schedule overview
  - WebSocket-based real-time updates

### 3. Player Frontend (Mobile)
- **Access:** Public URL (`/`)
- **Features:**
  - Join tournament (enter name)
  - Create/edit player profile (avatar, colors)
  - View assigned matches for current round
  - Join active match
  - In-match health counter with +/- controls
  - Confirm defeat (when health reaches 0)
  - View upcoming matches
  - View current standings

---

## Database Schema

### Tables

#### `tournaments`
```sql
CREATE TABLE tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    draft_type TEXT NOT NULL,  -- e.g., "Booster Draft", "Sealed", "Cube Draft"
    tournament_type TEXT NOT NULL,  -- "Round Robin"
    max_players INTEGER NOT NULL,
    match_format TEXT NOT NULL,  -- "Best of 1", "Best of 3"
    starting_life INTEGER NOT NULL DEFAULT 20,
    status TEXT NOT NULL,  -- "registration", "in_progress", "completed"
    current_round INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### `players`
```sql
CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    avatar_path TEXT,  -- path to uploaded image or preset identifier
    colors TEXT,  -- JSON array: ["W", "U", "B", "R", "G"]
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    UNIQUE(tournament_id, name)
);
```

#### `rounds`
```sql
CREATE TABLE rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    status TEXT NOT NULL,  -- "pending", "in_progress", "completed"
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    UNIQUE(tournament_id, round_number)
);
```

#### `matches`
```sql
CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER NOT NULL,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    player1_health INTEGER,  -- current health, starts at starting_life
    player2_health INTEGER,
    winner_id INTEGER,
    status TEXT NOT NULL,  -- "pending", "in_progress", "completed"
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (round_id) REFERENCES rounds(id),
    FOREIGN KEY (player1_id) REFERENCES players(id),
    FOREIGN KEY (player2_id) REFERENCES players(id),
    FOREIGN KEY (winner_id) REFERENCES players(id)
);
```

#### `match_events`
```sql
CREATE TABLE match_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,  -- "health_change", "match_start", "match_end"
    old_value INTEGER,
    new_value INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);
```

#### `admin_config`
```sql
CREATE TABLE admin_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Single row table
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX idx_players_tournament ON players(tournament_id);
CREATE INDEX idx_rounds_tournament ON rounds(tournament_id);
CREATE INDEX idx_matches_round ON matches(round_id);
CREATE INDEX idx_matches_players ON matches(player1_id, player2_id);
CREATE INDEX idx_match_events_match ON match_events(match_id);
```

---

## API Endpoints

### Admin Endpoints

#### `POST /api/admin/login`
**Request:**
```json
{
  "password": "string"
}
```
**Response:**
```json
{
  "token": "jwt_token",
  "expires_at": "2025-12-02T12:00:00Z"
}
```

#### `POST /api/admin/tournament`
**Headers:** `Authorization: Bearer {token}`
**Request:**
```json
{
  "name": "Friday Night Draft",
  "draft_type": "Booster Draft",
  "tournament_type": "Round Robin",
  "max_players": 8,
  "match_format": "Best of 1",
  "starting_life": 20
}
```
**Response:**
```json
{
  "tournament_id": 1,
  "status": "registration"
}
```

#### `POST /api/admin/tournament/{id}/generate-schedule`
**Headers:** `Authorization: Bearer {token}`
**Response:**
```json
{
  "rounds_created": 7,
  "total_matches": 28,
  "message": "Schedule generated successfully"
}
```

#### `POST /api/admin/tournament/{id}/next-round`
**Headers:** `Authorization: Bearer {token}`
**Response:**
```json
{
  "current_round": 2,
  "status": "in_progress"
}
```

#### `PUT /api/admin/match/{id}/result`
**Headers:** `Authorization: Bearer {token}`
**Request:**
```json
{
  "winner_id": 5
}
```

#### `DELETE /api/admin/match/{id}/force-end`
**Headers:** `Authorization: Bearer {token}`

#### `GET /api/admin/tournaments/history`
**Headers:** `Authorization: Bearer {token}`
**Response:**
```json
{
  "tournaments": [
    {
      "id": 1,
      "name": "Friday Night Draft",
      "status": "completed",
      "players_count": 8,
      "completed_at": "2025-12-01T22:30:00Z"
    }
  ]
}
```

### Player Endpoints

#### `POST /api/players/join`
**Request:**
```json
{
  "tournament_id": 1,
  "name": "Alice"
}
```
**Response:**
```json
{
  "player_id": 1,
  "tournament_id": 1,
  "name": "Alice"
}
```

#### `PUT /api/players/{id}/profile`
**Request (multipart/form-data):**
```
name: "Alice"
colors: ["W", "U"]
avatar: [file] or preset_id: "avatar_1"
```
**Response:**
```json
{
  "player_id": 1,
  "name": "Alice",
  "avatar_url": "/uploads/avatars/player_1.png",
  "colors": ["W", "U"]
}
```

#### `GET /api/players/{id}/profile`
**Response:**
```json
{
  "player_id": 1,
  "name": "Alice",
  "avatar_url": "/uploads/avatars/player_1.png",
  "colors": ["W", "U"],
  "wins": 3,
  "losses": 2
}
```

#### `GET /api/players/{id}/matches`
**Response:**
```json
{
  "current_match": {
    "match_id": 15,
    "round_number": 3,
    "opponent": {
      "name": "Bob",
      "avatar_url": "/uploads/avatars/player_2.png",
      "colors": ["R", "G"]
    },
    "status": "in_progress"
  },
  "upcoming_matches": [
    {
      "round_number": 4,
      "opponent": "Charlie"
    }
  ]
}
```

### Match Endpoints

#### `POST /api/matches/{id}/join`
**Request:**
```json
{
  "player_id": 1
}
```
**Response:**
```json
{
  "match_id": 15,
  "your_health": 20,
  "opponent_name": "Bob",
  "status": "in_progress"
}
```

#### `PUT /api/matches/{id}/health`
**Request:**
```json
{
  "player_id": 1,
  "health_change": -5
}
```
**Response:**
```json
{
  "new_health": 15,
  "opponent_health": null
}
```

#### `POST /api/matches/{id}/defeat`
**Request:**
```json
{
  "player_id": 1
}
```
**Response:**
```json
{
  "match_id": 15,
  "winner_id": 2,
  "status": "completed"
}
```

### Tournament Endpoints

#### `GET /api/tournament/current`
**Response:**
```json
{
  "tournament_id": 1,
  "name": "Friday Night Draft",
  "status": "in_progress",
  "current_round": 3,
  "total_rounds": 7,
  "players_count": 8
}
```

#### `GET /api/tournament/{id}/standings`
**Response:**
```json
{
  "standings": [
    {
      "rank": 1,
      "player_id": 1,
      "name": "Alice",
      "avatar_url": "/uploads/avatars/player_1.png",
      "colors": ["W", "U"],
      "wins": 5,
      "losses": 2,
      "points": 15
    }
  ]
}
```

#### `GET /api/tournament/{id}/schedule`
**Response:**
```json
{
  "rounds": [
    {
      "round_number": 1,
      "status": "completed",
      "matches": [
        {
          "match_id": 1,
          "player1": "Alice",
          "player2": "Bob",
          "winner": "Alice"
        }
      ]
    }
  ]
}
```

#### `GET /api/tournament/{id}/current-round`
**Response:**
```json
{
  "round_number": 3,
  "status": "in_progress",
  "matches": [
    {
      "match_id": 15,
      "player1": {
        "name": "Alice",
        "avatar_url": "/uploads/avatars/player_1.png",
        "colors": ["W", "U"],
        "health": 15
      },
      "player2": {
        "name": "Bob",
        "avatar_url": "/uploads/avatars/player_2.png",
        "colors": ["R", "G"],
        "health": 18
      },
      "status": "in_progress"
    }
  ]
}
```

### WebSocket Endpoints

#### `WS /ws/dashboard`
**Messages Sent to Client:**
```json
{
  "type": "health_update",
  "match_id": 15,
  "player_id": 1,
  "new_health": 15
}
```
```json
{
  "type": "match_complete",
  "match_id": 15,
  "winner_id": 2
}
```
```json
{
  "type": "round_complete",
  "round_number": 3
}
```

#### `WS /ws/match/{match_id}`
**Messages Sent to Client (for players in match):**
```json
{
  "type": "opponent_joined",
  "opponent_name": "Bob"
}
```
```json
{
  "type": "health_update",
  "your_health": 15
}
```
```json
{
  "type": "match_end",
  "winner_id": 2
}
```

---

## Frontend Components

### Admin Panel

#### Pages:
1. **Login Page** (`/admin`)
   - Password input
   - JWT token storage

2. **Tournament Setup** (`/admin/setup`)
   - Form for tournament configuration
   - Player list (with ability to remove players)
   - "Generate Schedule" button
   - "Start Tournament" button

3. **Tournament Control** (`/admin/control`)
   - Current round display
   - Match results table
   - Manual result editing
   - Force end match buttons
   - "Next Round" button (auto-enabled when all matches complete)

4. **Tournament History** (`/admin/history`)
   - List of past tournaments
   - View details/results

### Live Dashboard (Desktop)

#### Pages:
1. **Main Dashboard** (`/dashboard`)
   - Tournament header (name, round X of Y)
   - Current round match grid
     - Each match shows:
       - Player 1: Avatar, Name, Color icons, Health bar
       - VS
       - Player 2: Avatar, Name, Color icons, Health bar
       - Match status indicator
   - Standings table (right sidebar)
     - Rank, Avatar, Name, W-L, Points
   - Schedule overview (collapsible)

### Player Frontend (Mobile)

#### Pages:
1. **Join Tournament** (`/`)
   - Tournament info display
   - Name input
   - "Join" button

2. **Player Profile** (`/profile/{player_id}`)
   - Edit name
   - Upload/select avatar (preset options)
   - Select colors (multi-select with W/U/B/R/G icons)
   - View personal stats (W-L record)

3. **My Matches** (`/matches/{player_id}`)
   - Current match (large card)
     - "Join Match" button
   - Upcoming matches list
   - Standings table

4. **In-Match View** (`/match/{match_id}`)
   - Large health counter display
   - Plus/Minus buttons (+1, -1, +5, -5)
   - Current health number (large, centered)
   - "Confirm Defeat" button (appears when health = 0)
   - Opponent name display (not their health)
   - Exit match button

---

## Round-Robin Scheduling Algorithm

### Implementation
```python
def generate_round_robin_schedule(players: List[Player]) -> List[Round]:
    """
    Generates a round-robin tournament schedule.
    If odd number of players, one player gets a bye each round.
    """
    n = len(players)
    if n % 2 == 1:
        players.append(None)  # Bye placeholder
        n += 1

    rounds = []
    num_rounds = n - 1
    half = n // 2

    for round_num in range(num_rounds):
        round_matches = []
        for i in range(half):
            player1 = players[i]
            player2 = players[n - 1 - i]

            if player1 is not None and player2 is not None:
                round_matches.append((player1, player2))

        rounds.append(round_matches)

        # Rotate players (keep first player fixed)
        players = [players[0]] + [players[-1]] + players[1:-1]

    return rounds
```

### Features:
- Ensures every player plays every other player exactly once
- Handles odd number of players with byes
- No repeat pairings
- Balanced schedule distribution

---

## Real-Time Update Flow

### WebSocket Architecture

1. **Dashboard Connection:**
   - Connects to `/ws/dashboard` on page load
   - Receives all match updates for current round
   - Updates UI elements without page refresh

2. **Match Connection:**
   - Player connects to `/ws/match/{match_id}` when joining match
   - Receives own health updates
   - Receives match end notifications

3. **Backend Broadcasting:**
   - When health changes: broadcast to dashboard + match participants
   - When match completes: broadcast to dashboard, notify both players
   - When round completes: broadcast to all dashboard connections

### Message Flow Example:
```
Player 1 clicks "-5" on health counter
    ↓
POST /api/matches/15/health {"player_id": 1, "health_change": -5}
    ↓
Backend updates database, new health = 15
    ↓
Backend broadcasts via WebSocket:
    → Dashboard: {"type": "health_update", "match_id": 15, "player_id": 1, "new_health": 15}
    → Player 1 match socket: {"type": "health_update", "your_health": 15}
    ↓
All connected clients update UI in real-time
```

---

## UI/UX Design Specifications

### Color Palette
- **Primary:** Magic blue (#0E5A8A)
- **Secondary:** Gold (#FFD700)
- **Background:** Dark gray (#1E1E1E)
- **Card background:** Slightly lighter gray (#2A2A2A)
- **Text:** White (#FFFFFF)
- **Health bar (high):** Green (#28A745)
- **Health bar (medium):** Yellow (#FFC107)
- **Health bar (low):** Red (#DC3545)

### Magic Color Icons
- W (White): Sun symbol, #F0F0F0
- U (Blue): Water droplet, #0E5A8A
- B (Black): Skull, #2B2B2B
- R (Red): Flame, #D32F2F
- G (Green): Tree/leaf, #388E3C

### Preset Avatars
Include 10-15 preset avatar options:
- Planeswalker silhouettes
- Iconic creature types (dragon, angel, demon, etc.)
- Magic card frame templates
- Abstract geometric designs

### Mobile Layout (Player Frontend)
- **Health Counter Screen:**
  - Large centered health number (80px font)
  - Four buttons in 2x2 grid below: [-5] [-1] [+1] [+5]
  - "Confirm Defeat" button at bottom (red, only shows at 0 HP)
  - Opponent name banner at top
  - Back button (top-left)

### Desktop Layout (Dashboard)
- **Match Grid:**
  - 2-3 matches per row (responsive)
  - Each match card: 400px width
  - Avatar size: 80px
  - Health bar: Full width below avatars
  - Color icons: 24px, displayed in row below name

- **Standings Table:**
  - Fixed right sidebar (300px)
  - Sticky position
  - Avatar thumbnails (40px)
  - Sortable columns

---

## Security Considerations

### Admin Access
- Password hashed with bcrypt (min 12 rounds)
- JWT tokens with 24-hour expiration
- Admin endpoints require valid token
- Rate limiting on login endpoint (5 attempts/minute)

### File Uploads
- Validate file types (PNG, JPG, GIF only)
- Max file size: 2MB
- Sanitize filenames
- Store in isolated directory
- Generate unique filenames (UUID)

### Input Validation
- Sanitize all user inputs (names, tournament names)
- Max length limits (name: 50 chars)
- Prevent SQL injection via parameterized queries
- Validate color selections (must be W/U/B/R/G)

### WebSocket Security
- Connection limits per IP
- Message rate limiting
- Validate player/match IDs before broadcasting
- Auto-disconnect idle connections (5 minutes)

---

## Error Handling

### Common Error Responses

#### Tournament Not Found (404)
```json
{
  "error": "Tournament not found",
  "code": "TOURNAMENT_NOT_FOUND"
}
```

#### Player Already Exists (409)
```json
{
  "error": "Player name already taken in this tournament",
  "code": "PLAYER_EXISTS"
}
```

#### Match Not Available (400)
```json
{
  "error": "Match is not in progress",
  "code": "MATCH_NOT_AVAILABLE"
}
```

#### Unauthorized (401)
```json
{
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED"
}
```

### Frontend Error Handling
- Display user-friendly error messages
- Toast notifications for non-critical errors
- Modal dialogs for critical errors
- Auto-retry on WebSocket disconnection
- Fallback to polling if WebSocket unavailable

---

## Testing Strategy

### Backend Tests
1. **Unit Tests:**
   - Tournament creation logic
   - Round-robin algorithm validation
   - Match result calculations
   - Standings computation

2. **Integration Tests:**
   - API endpoint functionality
   - Database operations
   - WebSocket message broadcasting
   - File upload handling

3. **Test Data:**
   - Seed database with sample tournaments
   - Generate test players (4, 8, 16 players)
   - Simulate complete tournament flow

### Frontend Tests
1. **Component Tests:**
   - Health counter increment/decrement
   - Profile form validation
   - Match card rendering

2. **E2E Tests:**
   - Complete player journey (join → match → defeat)
   - Admin tournament setup flow
   - Dashboard real-time updates

### Manual Testing Checklist
- [ ] 4-player tournament (bye handling)
- [ ] 8-player tournament (full round-robin)
- [ ] Concurrent matches in same round
- [ ] WebSocket reconnection
- [ ] Mobile responsive design
- [ ] Avatar upload/selection
- [ ] Admin result editing
- [ ] Tournament completion flow

---

## Deployment Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- SQLite3
- (Optional) Docker & Docker Compose

### Environment Variables
```env
# Backend (.env)
DATABASE_URL=sqlite:///./mtg_tournament.db
ADMIN_PASSWORD_HASH=<bcrypt_hash>
JWT_SECRET=<random_secret_key>
UPLOAD_DIR=./uploads
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8000

# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Installation Steps

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py  # Initialize database
python scripts/create_admin.py  # Set admin password
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Development
npm run build  # Production
```

#### Docker Deployment (Optional)
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    environment:
      - DATABASE_URL=sqlite:///./data/mtg_tournament.db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### Production Checklist
- [ ] Change admin password
- [ ] Generate secure JWT secret
- [ ] Configure CORS origins
- [ ] Enable HTTPS (reverse proxy)
- [ ] Set up backup strategy for SQLite database
- [ ] Configure log rotation
- [ ] Test WebSocket connections through proxy
- [ ] Optimize frontend build (minification, compression)

---

## Future Enhancements (Out of Scope for v1)

1. **Multiple Simultaneous Tournaments**
   - Tournament selection page
   - Separate databases per tournament

2. **Advanced Draft Features**
   - In-app booster draft (pack passing)
   - Deck builder integration
   - Card pool tracking

3. **Enhanced Statistics**
   - Match history per player
   - Color combination win rates
   - Average game length

4. **Social Features**
   - Player chat during matches
   - Post-tournament discussion
   - Share results on social media

5. **Swiss Pairing Options**
   - Alternative tournament formats
   - Tiebreaker systems
   - Opponent history tracking

6. **Notifications**
   - Push notifications for match start
   - Email summaries
   - SMS alerts for round changes

7. **Accessibility**
   - Screen reader support
   - High contrast mode
   - Keyboard navigation

---

## Project File Structure

```
mtgtrack/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tournament.py
│   │   ├── player.py
│   │   ├── match.py
│   │   └── round.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── tournament.py
│   │   ├── player.py
│   │   └── match.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── players.py
│   │   ├── matches.py
│   │   ├── tournament.py
│   │   └── websockets.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tournament_service.py
│   │   ├── match_service.py
│   │   ├── scheduler.py
│   │   └── auth.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── migrations/
│   ├── scripts/
│   │   ├── init_db.py
│   │   └── create_admin.py
│   └── uploads/
│       ├── avatars/
│       └── presets/
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── admin/
│   │   │   │   ├── Login.tsx
│   │   │   │   ├── TournamentSetup.tsx
│   │   │   │   ├── TournamentControl.tsx
│   │   │   │   └── History.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── MatchCard.tsx
│   │   │   │   ├── StandingsTable.tsx
│   │   │   │   └── ScheduleView.tsx
│   │   │   ├── player/
│   │   │   │   ├── JoinTournament.tsx
│   │   │   │   ├── Profile.tsx
│   │   │   │   ├── MatchList.tsx
│   │   │   │   └── MatchView.tsx
│   │   │   └── shared/
│   │   │       ├── Avatar.tsx
│   │   │       ├── ColorIcon.tsx
│   │   │       ├── HealthBar.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useTournament.ts
│   │   │   └── useMatch.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── styles/
│   │       └── index.css
│   └── public/
│       └── presets/
│           ├── avatar_1.png
│           ├── avatar_2.png
│           └── ...
├── docker-compose.yml
├── .gitignore
├── README.md
└── PROJECT_SPECIFICATION.md
```

---

## Implementation Phases

### Phase 1: Backend Core (Week 1)
- [ ] Set up FastAPI project structure
- [ ] Implement database models and migrations
- [ ] Create admin authentication
- [ ] Implement tournament CRUD operations
- [ ] Implement player registration endpoints
- [ ] Build round-robin scheduler
- [ ] Add match management endpoints

### Phase 2: Backend Real-Time (Week 1-2)
- [ ] Implement WebSocket connections
- [ ] Add health update broadcasting
- [ ] Create match event logging
- [ ] Test concurrent connections

### Phase 3: Frontend Core (Week 2)
- [ ] Set up React + Vite + TailwindCSS
- [ ] Create routing structure
- [ ] Build admin login page
- [ ] Build tournament setup page
- [ ] Implement player join flow
- [ ] Create profile editor

### Phase 4: Frontend Match System (Week 2-3)
- [ ] Build match view with health counter
- [ ] Implement WebSocket client
- [ ] Add real-time health updates
- [ ] Create defeat confirmation
- [ ] Build match list view

### Phase 5: Dashboard (Week 3)
- [ ] Build desktop dashboard layout
- [ ] Create match card components
- [ ] Implement standings table
- [ ] Add WebSocket listeners
- [ ] Style with animations

### Phase 6: Admin Control (Week 3)
- [ ] Build tournament control panel
- [ ] Add manual result editing
- [ ] Implement round advancement
- [ ] Create tournament history view

### Phase 7: Polish & Testing (Week 4)
- [ ] Mobile responsive testing
- [ ] Cross-browser testing
- [ ] WebSocket reconnection logic
- [ ] Error handling improvements
- [ ] Performance optimization
- [ ] Documentation

### Phase 8: Deployment (Week 4)
- [ ] Create deployment scripts
- [ ] Set up production environment
- [ ] Database backup strategy
- [ ] Monitor and log configuration
- [ ] Final testing on production server

---

## Key Technical Decisions

### Why FastAPI?
- Native WebSocket support
- Automatic API documentation (Swagger UI)
- Type hints and validation with Pydantic
- High performance (async/await)
- Easy to learn and deploy

### Why React?
- Component reusability
- Large ecosystem for mobile-responsive design
- Excellent WebSocket integration
- TypeScript support for type safety
- Fast development with Vite

### Why SQLite?
- Single-machine deployment requirement
- No separate database server needed
- Easy backup (single file)
- Sufficient performance for 2-20 concurrent users
- Built-in Python support

### Why WebSockets over Polling?
- True real-time updates (no delay)
- Lower server load (no repeated HTTP requests)
- Better user experience for live dashboard
- Bidirectional communication support

---

## Success Metrics

### Technical Metrics
- WebSocket latency < 100ms
- Page load time < 2s
- API response time < 200ms
- Support 20 concurrent players without lag
- 99% uptime during tournament

### User Experience Metrics
- Health updates visible within 500ms
- Mobile-friendly (usable on 4" screens)
- Intuitive UI (no training required)
- Zero data loss on WebSocket reconnect
- Tournament completes without manual intervention

---

## Glossary

- **Round-Robin:** Tournament format where every player plays every other player exactly once
- **Bye:** When a player has no opponent for a round (odd number of players)
- **Best of 1 (Bo1):** Single game determines match winner
- **Best of 3 (Bo3):** First player to win 2 games wins the match
- **Standing:** Current ranking of players based on wins/losses
- **Magic Colors:** W (White), U (Blue), B (Black), R (Red), G (Green)
- **Draft:** Format where players select cards from packs to build decks

---

## Contact & Support

For questions or issues during implementation:
- Review this specification document
- Check FastAPI documentation: https://fastapi.tiangolo.com
- Check React documentation: https://react.dev
- SQLAlchemy ORM: https://docs.sqlalchemy.org

---

---

## Testing Tools & Simulation

### Automated Player Simulator

For testing purposes, a standalone Python script that simulates multiple players playing matches with random health changes.

#### Script: `tests/simulate_tournament.py`

**Features:**
- Create tournament with simulated players
- Simulate N players with random names and colors
- Bots automatically join their assigned matches
- Random health changes (+/- adjustments) at intervals
- Configurable simulation speed
- Real tester can join as a player alongside bots
- Verbose logging of all actions

**Usage:**
```bash
# Simulate 8 players, fast mode (1-3 second intervals)
python tests/simulate_tournament.py --players 8 --speed fast

# Simulate 6 players, allow manual player to join
python tests/simulate_tournament.py --players 6 --manual-player "YourName"

# Simulate specific tournament ID
python tests/simulate_tournament.py --tournament-id 1 --players 4
```

**Configuration Options:**
- `--players N` - Number of simulated players (2-20)
- `--speed [slow|medium|fast]` - Health update frequency
  - slow: 5-10 seconds between actions
  - medium: 3-5 seconds
  - fast: 1-3 seconds
- `--manual-player NAME` - Reserve one slot for human tester
- `--tournament-id ID` - Join existing tournament
- `--round-delay SECONDS` - Pause between rounds (default: 10s)
- `--api-url URL` - Backend API URL (default: http://localhost:8000)
- `--verbose` - Detailed action logging

**Implementation:**

```python
#!/usr/bin/env python3
"""
Tournament simulator for testing MTG Draft Tournament Tracker.
Simulates multiple players with random health changes.
"""

import asyncio
import random
import argparse
import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SimulatedPlayer:
    id: int
    name: str
    colors: List[str]
    current_match_id: Optional[int] = None
    current_health: int = 20

class TournamentSimulator:
    def __init__(
        self,
        api_url: str,
        num_players: int,
        speed: str = "medium",
        manual_player: Optional[str] = None
    ):
        self.api_url = api_url.rstrip('/')
        self.num_players = num_players
        self.speed = speed
        self.manual_player = manual_player
        self.players: List[SimulatedPlayer] = []
        self.tournament_id: Optional[int] = None

        # Speed configurations (seconds)
        self.speed_config = {
            "slow": (5, 10),
            "medium": (3, 5),
            "fast": (1, 3)
        }

        self.running = True

    def log(self, message: str):
        """Print timestamped log message."""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def create_tournament(self) -> int:
        """Create a new tournament."""
        self.log("Creating tournament...")

        response = requests.post(
            f"{self.api_url}/api/admin/tournament",
            json={
                "name": f"Simulated Tournament {int(time.time())}",
                "draft_type": "Simulated Draft",
                "tournament_type": "Round Robin",
                "max_players": self.num_players,
                "match_format": "Best of 1",
                "starting_life": 20
            },
            headers={"Authorization": "Bearer ADMIN_TOKEN"}  # Replace with actual token
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create tournament: {response.text}")

        tournament_id = response.json()["tournament_id"]
        self.log(f"Tournament created: ID {tournament_id}")
        return tournament_id

    def generate_player_name(self, index: int) -> str:
        """Generate random player name."""
        first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank",
                       "Grace", "Henry", "Iris", "Jack", "Kate", "Leo",
                       "Maya", "Noah", "Olivia", "Paul", "Quinn", "Ruby"]
        last_names = ["Smith", "Johnson", "Mage", "Warrior", "Druid",
                      "Ranger", "Cleric", "Rogue", "Paladin", "Monk"]

        if index < len(first_names):
            return f"{first_names[index]} (Bot)"
        return f"Player{index} (Bot)"

    def generate_random_colors(self) -> List[str]:
        """Generate 1-3 random Magic colors."""
        all_colors = ["W", "U", "B", "R", "G"]
        num_colors = random.randint(1, 3)
        return random.sample(all_colors, num_colors)

    def register_players(self):
        """Register all simulated players."""
        self.log(f"Registering {self.num_players} players...")

        for i in range(self.num_players):
            name = self.generate_player_name(i)
            colors = self.generate_random_colors()

            response = requests.post(
                f"{self.api_url}/api/players/join",
                json={
                    "tournament_id": self.tournament_id,
                    "name": name
                }
            )

            if response.status_code != 200:
                self.log(f"Failed to register {name}: {response.text}")
                continue

            player_data = response.json()
            player_id = player_data["player_id"]

            # Update profile with colors
            requests.put(
                f"{self.api_url}/api/players/{player_id}/profile",
                json={"colors": colors}
            )

            player = SimulatedPlayer(
                id=player_id,
                name=name,
                colors=colors
            )
            self.players.append(player)

            self.log(f"Registered: {name} (ID: {player_id}, Colors: {colors})")

    def generate_schedule(self):
        """Generate tournament schedule."""
        self.log("Generating round-robin schedule...")

        response = requests.post(
            f"{self.api_url}/api/admin/tournament/{self.tournament_id}/generate-schedule",
            headers={"Authorization": "Bearer ADMIN_TOKEN"}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to generate schedule: {response.text}")

        data = response.json()
        self.log(f"Schedule generated: {data['rounds_created']} rounds, {data['total_matches']} matches")

    def get_current_round_matches(self) -> List[Dict]:
        """Get matches for current round."""
        response = requests.get(
            f"{self.api_url}/api/tournament/{self.tournament_id}/current-round"
        )

        if response.status_code != 200:
            return []

        return response.json().get("matches", [])

    def join_match(self, player: SimulatedPlayer, match_id: int):
        """Player joins their assigned match."""
        response = requests.post(
            f"{self.api_url}/api/matches/{match_id}/join",
            json={"player_id": player.id}
        )

        if response.status_code == 200:
            player.current_match_id = match_id
            player.current_health = 20
            self.log(f"{player.name} joined match {match_id}")
            return True
        return False

    def update_health(self, player: SimulatedPlayer, change: int):
        """Update player health."""
        if player.current_match_id is None:
            return

        response = requests.put(
            f"{self.api_url}/api/matches/{player.current_match_id}/health",
            json={
                "player_id": player.id,
                "health_change": change
            }
        )

        if response.status_code == 200:
            player.current_health += change
            self.log(f"{player.name}: {change:+d} HP → {player.current_health} HP")

    def confirm_defeat(self, player: SimulatedPlayer):
        """Player confirms defeat."""
        if player.current_match_id is None:
            return

        response = requests.post(
            f"{self.api_url}/api/matches/{player.current_match_id}/defeat",
            json={"player_id": player.id}
        )

        if response.status_code == 200:
            self.log(f"{player.name} confirmed defeat in match {player.current_match_id}")
            player.current_match_id = None
            player.current_health = 20

    async def simulate_player_actions(self, player: SimulatedPlayer):
        """Simulate a single player's actions."""
        while self.running:
            if player.current_match_id is not None:
                # Player is in a match
                if player.current_health > 0:
                    # Random health change
                    change = random.choice([-5, -3, -2, -1, -1, 1, 2])

                    # Don't go negative (API should handle, but check locally)
                    if player.current_health + change < 0:
                        change = -player.current_health

                    self.update_health(player, change)

                    # Check if defeated
                    if player.current_health <= 0:
                        await asyncio.sleep(2)  # Brief pause before confirming
                        self.confirm_defeat(player)
                else:
                    # Already at 0, confirm defeat
                    self.confirm_defeat(player)

            # Wait before next action
            min_delay, max_delay = self.speed_config[self.speed]
            await asyncio.sleep(random.uniform(min_delay, max_delay))

    async def run_round(self):
        """Run one round of matches."""
        matches = self.get_current_round_matches()

        if not matches:
            self.log("No matches found for current round")
            return False

        self.log(f"Starting round with {len(matches)} matches")

        # Assign players to their matches
        for match in matches:
            match_id = match["match_id"]

            # Find players for this match
            p1_name = match["player1"]["name"]
            p2_name = match["player2"]["name"]

            player1 = next((p for p in self.players if p.name == p1_name), None)
            player2 = next((p for p in self.players if p.name == p2_name), None)

            if player1:
                self.join_match(player1, match_id)
            if player2:
                self.join_match(player2, match_id)

        # Start simulating all players concurrently
        tasks = [self.simulate_player_actions(player) for player in self.players]

        # Wait until all matches are complete
        while True:
            matches = self.get_current_round_matches()

            if not matches:
                break

            in_progress = sum(1 for m in matches if m["status"] == "in_progress")
            completed = sum(1 for m in matches if m["status"] == "completed")

            if in_progress == 0:
                self.log(f"Round complete! {completed} matches finished")
                break

            await asyncio.sleep(2)

        # Cancel player simulation tasks
        for task in tasks:
            task.cancel()

        return True

    async def run_tournament(self):
        """Run the entire tournament simulation."""
        try:
            # Create tournament
            self.tournament_id = self.create_tournament()

            # Register players
            self.register_players()

            # Manual player can join now
            if self.manual_player:
                self.log(f"\n{'='*60}")
                self.log(f"MANUAL PLAYER: Join at http://localhost:5173")
                self.log(f"Tournament ID: {self.tournament_id}")
                self.log(f"Your name: {self.manual_player}")
                self.log(f"{'='*60}\n")
                self.log("Waiting 30 seconds for manual player to join...")
                await asyncio.sleep(30)

            # Generate schedule
            self.generate_schedule()

            # Get total rounds
            response = requests.get(f"{self.api_url}/api/tournament/{self.tournament_id}/schedule")
            total_rounds = len(response.json().get("rounds", []))

            self.log(f"Tournament has {total_rounds} rounds")

            # Run each round
            for round_num in range(1, total_rounds + 1):
                self.log(f"\n{'='*60}")
                self.log(f"ROUND {round_num} of {total_rounds}")
                self.log(f"{'='*60}\n")

                success = await self.run_round()

                if not success:
                    break

                if round_num < total_rounds:
                    self.log(f"Pausing before next round...")
                    await asyncio.sleep(10)

            self.log("\n{'='*60}")
            self.log("TOURNAMENT COMPLETE!")
            self.log(f"{'='*60}\n")

            # Display final standings
            response = requests.get(f"{self.api_url}/api/tournament/{self.tournament_id}/standings")
            standings = response.json().get("standings", [])

            self.log("Final Standings:")
            for player in standings:
                self.log(f"  {player['rank']}. {player['name']}: {player['wins']}-{player['losses']}")

        except KeyboardInterrupt:
            self.log("\nSimulation interrupted by user")
            self.running = False
        except Exception as e:
            self.log(f"Error: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(
        description="Simulate MTG Draft Tournament with bot players"
    )
    parser.add_argument(
        "--players",
        type=int,
        default=8,
        help="Number of simulated players (2-20)"
    )
    parser.add_argument(
        "--speed",
        choices=["slow", "medium", "fast"],
        default="medium",
        help="Simulation speed"
    )
    parser.add_argument(
        "--manual-player",
        type=str,
        help="Reserve slot for human player with this name"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Backend API URL"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging"
    )

    args = parser.parse_args()

    # Validate player count
    if args.players < 2 or args.players > 20:
        print("Error: Players must be between 2 and 20")
        return

    # Adjust for manual player
    num_bots = args.players - (1 if args.manual_player else 0)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║      MTG Draft Tournament Simulator                      ║
╚══════════════════════════════════════════════════════════╝

Configuration:
  - Bot Players: {num_bots}
  - Manual Player: {args.manual_player or 'None'}
  - Speed: {args.speed}
  - API: {args.api_url}

Starting simulation...
    """)

    simulator = TournamentSimulator(
        api_url=args.api_url,
        num_players=num_bots,
        speed=args.speed,
        manual_player=args.manual_player
    )

    asyncio.run(simulator.run_tournament())

if __name__ == "__main__":
    main()
```

**Dependencies:**
```txt
# Add to requirements-dev.txt
requests>=2.31.0
asyncio>=3.4.3
```

**Example Test Scenarios:**

```bash
# Scenario 1: Quick 4-player test
python tests/simulate_tournament.py --players 4 --speed fast

# Scenario 2: Join as a real player with 7 bots
python tests/simulate_tournament.py --players 8 --manual-player "TestUser" --speed medium

# Scenario 3: Stress test with 20 players
python tests/simulate_tournament.py --players 20 --speed fast

# Scenario 4: Slow realistic gameplay
python tests/simulate_tournament.py --players 6 --speed slow
```

**What Gets Tested:**
- ✅ Tournament creation
- ✅ Player registration (bulk)
- ✅ Profile updates (colors)
- ✅ Round-robin schedule generation
- ✅ Match joining
- ✅ Real-time health updates via API
- ✅ Defeat confirmation
- ✅ Round completion detection
- ✅ Multi-round tournament flow
- ✅ Final standings calculation
- ✅ Concurrent match simulation
- ✅ WebSocket broadcasting (observed via dashboard)

**Testing Workflow:**

1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. Open dashboard in browser: `http://localhost:5173/dashboard`
4. Run simulator: `python tests/simulate_tournament.py --players 8 --speed medium`
5. Watch live updates on dashboard as bots play
6. (Optional) Join as manual player to play against bots

**Simulator Behavior:**
- Bots make random health changes between -5 and +2
- More negative changes (simulating taking damage)
- When health reaches 0, bot confirms defeat after 2-second delay
- All matches in a round run concurrently
- Automatic progression through all rounds

---

**Document Version:** 1.0
**Last Updated:** 2025-12-02
**Status:** Ready for Implementation
