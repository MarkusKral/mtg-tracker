# Admin Login Troubleshooting Guide

## Current Status
✅ Admin user exists in database
✅ Password verification works correctly
✅ Your admin password is: **`admin`** (not `admin123`)

## How to Login

1. **Start the server** (if not already running):
   ```bash
   ./start.sh
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:8000/admin.html
   ```

3. **Login with**:
   - Password: `admin`

## If Login Still Fails

### Test 1: Check if the server is running
Open a new terminal and run:
```bash
curl http://localhost:8000/health
```

**Expected output:** `{"status":"healthy"}`

If you get "Connection refused", the server isn't running.

### Test 2: Test the login API directly
```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin"}'
```

**Expected output:** Something like:
```json
{
  "token": "eyJ...",
  "expires_at": "2025-12-03T..."
}
```

### Test 3: Check browser console
1. Open browser Developer Tools (F12)
2. Go to the "Console" tab
3. Try to login
4. Look for any error messages in red

Common errors:
- **CORS error**: The API might not be allowing requests from the browser
- **Network error**: Check if the API_URL in admin.html is correct (should be http://localhost:8000)

### Test 4: Verify your password in .env
```bash
cat backend/.env | grep ADMIN_PASSWORD
```

Should show: `ADMIN_PASSWORD=admin`

### Test 5: Reset the admin password
If all else fails, reset the password to "admin123":
```bash
cd backend
source venv/bin/activate
python scripts/reset_admin_password.py
# When prompted, press Enter to use default "admin123"
# Or type a new password and press Enter
```

## Change Password

To change your admin password:

1. Edit `backend/.env`:
   ```bash
   nano backend/.env
   ```

2. Change the line:
   ```
   ADMIN_PASSWORD=your_new_password
   ```

3. Reset the password in the database:
   ```bash
   cd backend
   source venv/bin/activate
   python scripts/reset_admin_password.py
   ```
   Press Enter to use the password from .env, or type a new one.

4. Restart the server

## Quick Reset to Default

To reset everything to use "admin123":

1. Edit `backend/.env` and change to:
   ```
   ADMIN_PASSWORD=admin123
   ```

2. Run:
   ```bash
   cd backend
   source venv/bin/activate
   python scripts/reset_admin_password.py
   ```
   Press Enter when prompted

3. Restart the server with `./start.sh`

4. Login with password: `admin123`

