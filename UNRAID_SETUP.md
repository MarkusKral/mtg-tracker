# Deploying MTG Tournament Tracker on Unraid

## Option 1: Using Docker Compose (Recommended)

### Step 1: Copy files to Unraid
Copy the entire project folder to your Unraid server, e.g., `/mnt/user/appdata/mtg-tournament/`

### Step 2: SSH into Unraid and navigate to the folder
```bash
cd /mnt/user/appdata/mtg-tournament
```

### Step 3: Build and run with Docker Compose
```bash
docker-compose up -d --build
```

### Step 4: Access the app
Open your browser and go to: `http://YOUR_UNRAID_IP:8000`

---

## Option 2: Manual Docker Setup (via Unraid UI)

### Step 1: Build the image on Unraid
SSH into Unraid and run:
```bash
cd /mnt/user/appdata/mtg-tournament
docker build -t mtg-tournament-tracker .
```

### Step 2: Add Container via Unraid Docker UI

1. Go to **Docker** tab in Unraid
2. Click **Add Container**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | mtg-tournament-tracker |
| **Repository** | mtg-tournament-tracker |
| **Network Type** | Bridge |
| **Port Mapping** | Host: `8000` → Container: `8000` |

4. Add **Path Mappings**:

| Container Path | Host Path | Access |
|----------------|-----------|--------|
| `/app/data` | `/mnt/user/appdata/mtg-tournament/data` | Read/Write |
| `/app/backend/uploads` | `/mnt/user/appdata/mtg-tournament/uploads` | Read/Write |

5. Add **Environment Variables**:

| Name | Value |
|------|-------|
| `ADMIN_PASSWORD` | `your-secure-password` |
| `JWT_SECRET` | `your-random-secret-key` |
| `ALLOWED_ORIGINS` | `*` |

6. Click **Apply**

---

## Option 3: Using Portainer (if installed)

1. Open Portainer on your Unraid
2. Go to **Stacks** → **Add Stack**
3. Paste the contents of `docker-compose.yml`
4. Adjust the volume paths to match your Unraid setup
5. Deploy

---

## Accessing the App

Once running, access the app at:
- **Main Page**: `http://YOUR_UNRAID_IP:8000`
- **Admin Panel**: `http://YOUR_UNRAID_IP:8000/admin.html`
- **Dashboard**: `http://YOUR_UNRAID_IP:8000/dashboard.html`
- **Player Page**: `http://YOUR_UNRAID_IP:8000/player.html`

Default admin password: `admin` (change via `ADMIN_PASSWORD` env variable)

---

## Updating the App

```bash
cd /mnt/user/appdata/mtg-tournament
git pull  # if using git
docker-compose down
docker-compose up -d --build
```

---

## Troubleshooting

### Container won't start
Check logs:
```bash
docker logs mtg-tournament-tracker
```

### Database issues
The SQLite database is stored in `/app/data/mtg_tournament.db`. Make sure the volume is properly mapped.

### Reset everything
```bash
docker-compose down
rm -rf data/mtg_tournament.db
docker-compose up -d
```

---

## Reverse Proxy (Optional)

If you want to access via a domain name with HTTPS, use Nginx Proxy Manager or Traefik:

**Nginx Proxy Manager example:**
- Domain: `mtg.yourdomain.com`
- Forward to: `YOUR_UNRAID_IP:8000`
- Enable WebSocket support ✓

