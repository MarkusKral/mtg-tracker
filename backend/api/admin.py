from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.database import get_db
from models import AdminConfig, Tournament
from schemas.admin import AdminLogin, AdminToken
from schemas.tournament import TournamentCreate, ScheduleGenerated
from schemas.match import WinnerUpdate
from services.auth import verify_password, create_access_token, verify_token
from services.tournament_service import TournamentService
from services.match_service import MatchService
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify admin JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload


@router.post("/login", response_model=AdminToken)
def admin_login(login_data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint."""
    admin_config = db.query(AdminConfig).filter(AdminConfig.id == 1).first()

    if not admin_config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin not configured. Run init_db.py first."
        )

    if not verify_password(login_data.password, admin_config.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": "admin"})
    expires_at = datetime.utcnow() + timedelta(hours=int(os.getenv("JWT_EXPIRATION_HOURS", "24")))

    return {
        "token": access_token,
        "expires_at": expires_at.isoformat() + "Z"
    }


@router.post("/tournament")
def create_tournament(
    tournament_data: TournamentCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    """Create a new tournament."""
    tournament = TournamentService.create_tournament(
        db,
        tournament_data.model_dump()
    )

    return {
        "tournament_id": tournament.id,
        "status": tournament.status
    }


@router.post("/tournament/{tournament_id}/generate-schedule", response_model=ScheduleGenerated)
def generate_schedule(
    tournament_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    """Generate round-robin schedule for tournament."""
    try:
        result = TournamentService.generate_schedule(db, tournament_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tournament/{tournament_id}/next-round")
async def advance_round(
    tournament_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    """Manually advance to next round."""
    try:
        result = TournamentService.advance_to_next_round(db, tournament_id)
        
        # Broadcast round change to dashboard
        from api.websockets import broadcast_round_complete
        await broadcast_round_complete(result["current_round"])
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/match/{match_id}/result")
def update_match_result(
    match_id: int,
    winner_data: WinnerUpdate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    """Manually update match result."""
    try:
        MatchService.update_match_result(db, match_id, winner_data.winner_id)
        return {"message": "Match result updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/match/{match_id}/force-end")
def force_end_match(
    match_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    """Force end a match."""
    try:
        MatchService.force_end_match(db, match_id)
        return {"message": "Match force-ended"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tournaments/history")
def get_tournament_history(
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    """Get tournament history."""
    tournaments = db.query(Tournament).order_by(Tournament.created_at.desc()).all()

    history = []
    for t in tournaments:
        players_count = len(t.players)
        history.append({
            "id": t.id,
            "name": t.name,
            "status": t.status,
            "players_count": players_count,
            "completed_at": t.completed_at.isoformat() + "Z" if t.completed_at else None
        })

    return {"tournaments": history}


@router.delete("/tournament/{tournament_id}")
def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    """Delete a tournament and all associated data (players, rounds, matches)."""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament_name = tournament.name
    
    # SQLAlchemy will cascade delete all related data (players, rounds, matches, events)
    db.delete(tournament)
    db.commit()
    
    return {
        "message": f"Tournament '{tournament_name}' deleted successfully",
        "tournament_id": tournament_id
    }
