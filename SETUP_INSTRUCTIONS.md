# Setup Instructions

## Quick Setup (Tested on macOS with Python 3.9+)

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you encounter issues with Python 3.13, the requirements have been updated to use compatible versions.

### 2. Initialize Database

```bash
python scripts/init_db.py
```

You should see:
```
✓ Database tables created
✓ Admin user created with password: admin123
```

### 3. Start Server

```bash
uvicorn main:app --reload
```

Server will start at: **http://localhost:8000**

### 4. Verify Installation

Open your browser and visit:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

You should see the interactive API documentation (Swagger UI).

## Testing the Application

### Option 1: Use the Simulator

In a new terminal:

```bash
cd tests
pip install requests
python simulate_tournament.py --players 8 --speed medium
```

### Option 2: Manual API Testing

#### Login as Admin

```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin123"}'
```

Save the token from the response.

#### Create Tournament

```bash
curl -X POST http://localhost:8000/api/admin/tournament \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tournament",
    "draft_type": "Booster Draft",
    "max_players": 8,
    "starting_life": 20
  }'
```

## Troubleshooting

### Python 3.13 Compatibility

If you're using Python 3.13 and encounter build errors with `pydantic-core`, the requirements.txt has been updated with compatible versions. Simply reinstall:

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### bcrypt Warnings

You may see warnings about bcrypt version detection. These are harmless and don't affect functionality. The application has been tested with bcrypt==4.1.2 which works correctly.

### Port Already in Use

If port 8000 is already in use:

```bash
uvicorn main:app --port 8001
```

Then update API URLs accordingly.

### Database Reset

To reset the database:

```bash
rm mtg_tournament.db
python scripts/init_db.py
```

## What's Working

✅ **All Backend Features:**
- Admin authentication (JWT)
- Tournament creation and management
- Player registration with profiles
- Match tracking with health updates
- Real-time WebSocket updates
- Round-robin scheduling
- Standings calculation
- Admin controls (force-end, edit results)

✅ **Testing Tools:**
- Tournament simulator with bot players
- Interactive API documentation at `/docs`
- Health check endpoint

## Next Steps

1. **Change Admin Password:** Edit `backend/.env` and set `ADMIN_PASSWORD`
2. **Explore API:** Visit http://localhost:8000/docs
3. **Run Simulator:** Test with `python tests/simulate_tournament.py`
4. **Build Frontend:** (Pending implementation)

## Need Help?

- **Full Documentation:** See `README.md`
- **Quick Start:** See `QUICKSTART.md`
- **Technical Details:** See `PROJECT_SPECIFICATION.md`
- **API Reference:** http://localhost:8000/docs (when server is running)

---

**Everything is working!** The backend is 100% functional and ready to use. 🚀
