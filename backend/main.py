from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database.database import init_db
from api import admin, players, matches, tournament, websockets
import os

app = FastAPI(
    title="MTG Draft Tournament Tracker",
    description="API for tracking Magic: The Gathering draft tournaments",
    version="1.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router)
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(tournament.router)
app.include_router(websockets.router)

# Serve uploaded files
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "avatars"), exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Serve frontend (if exists)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    from database.database import init_admin_user
    init_db()
    init_admin_user()
    print("Database initialized successfully!")
    print(f"Server running. API docs available at http://localhost:8000/docs")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "MTG Draft Tournament Tracker API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
