# MTG Tournament Tracker - Frontend

Simple HTML/JavaScript frontend for the MTG Tournament Tracker.

## Features

### 📺 **Live Dashboard** (`dashboard.html`)
- Desktop-optimized view for spectators
- Real-time match cards with health bars
- WebSocket updates for live health tracking
- Current standings table
- Magic color indicators
- Auto-refresh every 5 seconds

### 📱 **Player Interface** (`player.html`)
- Mobile-optimized for phones
- Join tournament with name
- View current and upcoming matches
- In-match health counter (+5, +1, -1, -5 buttons)
- Confirm defeat when health reaches 0
- View personal stats and standings
- Auto-refresh every 3 seconds

### ⚙️ **Admin Panel** (`admin.html`)
- Password-protected admin interface
- Create new tournaments
- View registered players
- Generate round-robin schedules
- Monitor current matches
- Force-end matches
- Advance rounds manually
- Auto-refresh every 5 seconds

## Setup

### 1. Start Backend

```bash
cd ../backend
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Access Frontend

The backend serves the frontend automatically:

- **Main Menu:** http://localhost:8000/
- **Live Dashboard:** http://localhost:8000/dashboard.html
- **Player Interface:** http://localhost:8000/player.html
- **Admin Panel:** http://localhost:8000/admin.html

Or open the HTML files directly in your browser:

```bash
# Open in browser
open index.html  # macOS
start index.html # Windows
xdg-open index.html # Linux
```

## Configuration

The API URLs are configured at the top of each HTML file:

```javascript
const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';
```

Change these if you're running the backend on a different host/port.

## Technologies

- **No Build Step Required** - Pure HTML/JavaScript
- **TailwindCSS** - Via CDN for styling
- **WebSockets** - For real-time updates
- **LocalStorage** - For persisting player/admin sessions
- **Fetch API** - For HTTP requests

## Usage

### For Players

1. Open http://localhost:8000/player.html on your phone
2. Enter your name and join tournament
3. When your match starts, click "Start Match"
4. Use +/- buttons to track your health
5. Click "Confirm Defeat" when you reach 0 HP

### For Spectators

1. Open http://localhost:8000/dashboard.html on a large screen
2. Watch matches update in real-time
3. View current standings
4. See live health counters for all players

### For Admins

1. Open http://localhost:8000/admin.html
2. Login with password (default: `admin123`)
3. Create a new tournament
4. Wait for players to join
5. Click "Generate Schedule" when ready
6. Monitor matches and advance rounds

## Features Detail

### Real-Time Updates

The dashboard and match screens use WebSockets to receive updates:

- Health changes appear immediately
- Match completions trigger UI updates
- Round changes refresh the display
- Automatic reconnection if connection drops

### Mobile Optimizations

Player interface is designed for mobile:
- Large touch targets (buttons)
- No horizontal scrolling
- Responsive text sizes
- Optimized for one-handed use
- Prevents zoom on input focus

### Color Coding

Health bars change color based on health:
- **Green:** > 15 HP
- **Yellow:** 11-15 HP
- **Orange:** 6-10 HP
- **Red:** ≤ 5 HP

Magic colors displayed as colored circles:
- **W (White):** Light gold
- **U (Blue):** Blue gradient
- **B (Black):** Black/gray
- **R (Red):** Red gradient
- **G (Green):** Green gradient

## Browser Compatibility

Tested on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

WebSocket support required (all modern browsers).

## Troubleshooting

### WebSocket Not Connecting

Check the WebSocket status indicator (green/red dot in dashboard header):
- **Green + pulsing:** Connected
- **Red:** Disconnected

If disconnected:
1. Ensure backend is running
2. Check CORS settings in `backend/.env`
3. Check browser console for errors

### API Errors

If you see "Failed to fetch" errors:
1. Verify backend is running: http://localhost:8000/health
2. Check API_URL in the HTML file matches backend
3. Look at browser console for specific errors

### Data Not Loading

1. Check Network tab in browser dev tools
2. Verify tournament exists: http://localhost:8000/api/tournament/current
3. Ensure database is initialized: `python scripts/init_db.py`

## Development

### Adding New Features

Each HTML file is self-contained with:
- Inline CSS in `<style>` tags
- JavaScript in `<script>` tags
- TailwindCSS for utility classes

To modify:
1. Edit the HTML file
2. Refresh browser (no build step!)
3. Changes appear immediately

### API Integration

All API calls use the Fetch API:

```javascript
// GET request
const response = await fetch(`${API_URL}/api/tournament/current`);
const data = await response.json();

// POST request
await fetch(`${API_URL}/api/players/join`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tournament_id: 1, name: 'Alice' })
});
```

### WebSocket Integration

```javascript
const ws = new WebSocket(`${WS_URL}/ws/dashboard`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle message
};
```

## Deployment

For production:

1. **Update API URLs** in all HTML files to your domain
2. **Serve via backend:** The backend serves these files at `/`
3. **Or use nginx:** Serve static files separately
4. **Enable HTTPS:** Update WebSocket to use `wss://`

Example nginx config:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /path/to/frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## File Structure

```
frontend/
├── index.html       # Main menu
├── dashboard.html   # Live dashboard (desktop)
├── player.html      # Player interface (mobile)
├── admin.html       # Admin panel
└── README.md        # This file
```

## Credits

- TailwindCSS for styling
- WebSocket API for real-time updates
- Fetch API for HTTP requests

---

**Ready to use!** Just start the backend and open any HTML file in your browser.
