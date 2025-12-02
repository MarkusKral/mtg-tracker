# Tournament Simulator - Testing Guide

## Overview
The tournament simulator creates bot players that automatically play matches, allowing you to test and demonstrate the tournament system without manual interaction.

## Quick Start

### 1. Start the Server
```bash
./start.sh
```

### 2. Run the Simulator

**Basic simulation (8 players):**
```bash
cd tests
python3 simulate_tournament.py
```

**Or use the convenience script:**
```bash
./tests/run_simulation.sh
```

## Usage Examples

### Different Player Counts
```bash
# 4 players (fewer rounds)
python3 simulate_tournament.py --players 4

# 12 players (more rounds)
python3 simulate_tournament.py --players 12
```

### Simulation Speed
```bash
# Slow speed (5-10 seconds between actions)
python3 simulate_tournament.py --speed slow

# Medium speed (3-5 seconds) - Default
python3 simulate_tournament.py --speed medium

# Fast speed (1-3 seconds)
python3 simulate_tournament.py --speed fast
```

### Play Along with Bots
Reserve a slot for yourself and play against the bots:

```bash
# Reserve slot for "YourName"
python3 simulate_tournament.py --players 8 --manual-player "YourName"
```

Then:
1. Wait for the script to show the join instructions
2. Open `http://localhost:8000/player.html` in your browser
3. Join with the name specified (e.g., "YourName")
4. Play your matches while bots play theirs!

### Custom API URL
If running the server on a different port:
```bash
python3 simulate_tournament.py --api-url http://localhost:3000
```

## Command-Line Options

```
Options:
  --players N           Number of simulated players (2-20, default: 8)
  --speed SPEED         Simulation speed: slow/medium/fast (default: medium)
  --manual-player NAME  Reserve a slot for human player with this name
  --api-url URL         Backend API URL (default: http://localhost:8000)
  -h, --help           Show help message
```

## What the Simulator Does

### Automatic Actions:
1. ✅ **Admin Login** - Authenticates as admin
2. ✅ **Create Tournament** - Sets up a new tournament
3. ✅ **Register Players** - Creates bot players with random names and colors
4. ✅ **Generate Schedule** - Creates round-robin pairings
5. ✅ **Play Matches** - Bots join matches and update health
6. ✅ **Complete Rounds** - Matches finish when health reaches 0
7. ✅ **Advance Rounds** - Automatically moves to next round
8. ✅ **Show Standings** - Displays final rankings

### Bot Behavior:
- Join assigned matches automatically
- Random health changes (-5 to +2)
- More likely to lose health (simulates gameplay)
- Confirm defeat when health reaches 0
- Concurrent match simulation (all matches play simultaneously)

## Example Output

```
[12:34:56] Logging in as admin...
[12:34:56] ✓ Admin login successful
[12:34:56] Creating tournament...
[12:34:56] ✓ Tournament created: ID 1
[12:34:56] Registering 8 bot players...
[12:34:57] ✓ Registered: Alice (Bot) (ID: 1, Colors: ['W', 'U'])
[12:34:57] ✓ Registered: Bob (Bot) (ID: 2, Colors: ['R', 'G'])
...
[12:34:59] Generating round-robin schedule...
[12:34:59] ✓ Schedule generated: 7 rounds, 28 matches

============================================================
ROUND 1 of 7
============================================================

[12:35:00] Starting round with 4 matches...
[12:35:00] ✓ Alice (Bot) joined match 1
[12:35:00] ✓ Bob (Bot) joined match 1
...
[12:35:05]   Alice (Bot): -3 HP → 17 HP
[12:35:08]   Bob (Bot): -5 HP → 15 HP
...
[12:35:30] ✓ Alice (Bot) confirmed defeat in match 1
[12:35:32] ✓ Round complete! 4 matches finished
```

## Watching the Action

While the simulator runs, you can:

### View Live Dashboard
Open `http://localhost:8000/dashboard.html` to see:
- Real-time health updates
- Match progress
- Current standings

### View Admin Panel
Open `http://localhost:8000/admin.html` to:
- Monitor all matches
- See player list
- View standings

### Join as Player (with --manual-player)
Open `http://localhost:8000/player.html` to:
- Play your own matches
- Track your standing
- Compete against bots

## Troubleshooting

### Server Not Running
```
Error: Failed to login as admin
```
**Solution:** Start the server with `./start.sh`

### Admin Password Error
```
Error: Failed to login as admin: Incorrect password
```
**Solution:** Check `backend/.env` for the ADMIN_PASSWORD value. The script tries both "admin" and "admin123".

### Port Already in Use
```
Error: Connection refused
```
**Solution:** Check if server is running on port 8000:
```bash
curl http://localhost:8000/health
```

### Missing Dependencies
```
ModuleNotFoundError: No module named 'requests'
```
**Solution:** Install requirements:
```bash
pip3 install -r tests/requirements-dev.txt
```

## Advanced Usage

### Multiple Simulations
Run multiple tournaments back-to-back:
```bash
for i in {1..3}; do
  echo "=== Tournament $i ==="
  python3 simulate_tournament.py --players 6 --speed fast
  sleep 5
done
```

### Testing Specific Scenarios

**Quick Test (4 players, fast):**
```bash
python3 simulate_tournament.py --players 4 --speed fast
```

**Long Tournament (20 players):**
```bash
python3 simulate_tournament.py --players 20 --speed medium
```

**Realistic Demo (8 players, slow):**
```bash
python3 simulate_tournament.py --players 8 --speed slow
```

## Features Tested

The simulator validates:
- ✅ Tournament creation
- ✅ Player registration  
- ✅ Profile color updates
- ✅ Round-robin scheduling
- ✅ Match joining
- ✅ Health tracking
- ✅ Match completion
- ✅ Round advancement
- ✅ Standings calculation
- ✅ WebSocket updates (visible on dashboard)

## Notes

- Bots don't use WebSockets (they use REST API only)
- Manual players can use full UI features (WebSockets, avatars, etc.)
- Each simulation creates a NEW tournament
- Old tournaments remain in the database (use admin panel to delete)
- Bots have realistic-looking names and random deck colors

## Example Workflows

### Demo for Others
```bash
# Start slow demo
python3 simulate_tournament.py --players 8 --speed slow

# Open dashboard in browser
# http://localhost:8000/dashboard.html
```

### Quick Development Testing
```bash
# Fast test with 4 players
python3 simulate_tournament.py --players 4 --speed fast
```

### Play Against Bots
```bash
# Reserve your slot
python3 simulate_tournament.py --players 8 --manual-player "Your Name"

# Join at: http://localhost:8000/player.html
```

Enjoy testing! 🎮🎴

