from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models import Tournament, Round, Match, Player
from schemas.tournament import TournamentStatus, StandingsResponse, ScheduleResponse, RoundSchedule, MatchSchedule
from schemas.match import CurrentRoundResponse, MatchDetails, MatchPlayerInfo
from services.tournament_service import TournamentService
import json

router = APIRouter(prefix="/api/tournament", tags=["tournament"])


@router.get("/current", response_model=TournamentStatus)
def get_current_tournament(db: Session = Depends(get_db)):
    """Get current tournament status."""
    tournament = TournamentService.get_current_tournament(db)
    if not tournament:
        raise HTTPException(status_code=404, detail="No tournament found")

    players_count = len(tournament.players)

    # Count total rounds
    total_rounds = db.query(Round).filter(Round.tournament_id == tournament.id).count()

    return {
        "tournament_id": tournament.id,
        "name": tournament.name,
        "status": tournament.status,
        "current_round": tournament.current_round,
        "total_rounds": total_rounds,
        "players_count": players_count
    }


@router.get("/{tournament_id}/standings", response_model=StandingsResponse)
def get_standings(tournament_id: int, db: Session = Depends(get_db)):
    """Get tournament standings."""
    tournament = TournamentService.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    standings = TournamentService.get_standings(db, tournament_id)
    return {"standings": standings}


@router.get("/{tournament_id}/schedule", response_model=ScheduleResponse)
def get_schedule(tournament_id: int, db: Session = Depends(get_db)):
    """Get full tournament schedule."""
    tournament = TournamentService.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    rounds = db.query(Round).filter(Round.tournament_id == tournament_id).order_by(Round.round_number).all()

    schedule = []
    for round_obj in rounds:
        matches = db.query(Match).filter(Match.round_id == round_obj.id).all()

        match_schedules = []
        for match in matches:
            player1 = db.query(Player).filter(Player.id == match.player1_id).first()
            player2 = db.query(Player).filter(Player.id == match.player2_id).first()
            winner = db.query(Player).filter(Player.id == match.winner_id).first() if match.winner_id else None

            match_schedules.append(MatchSchedule(
                match_id=match.id,
                player1=player1.name,
                player2=player2.name,
                winner=winner.name if winner else None
            ))

        schedule.append(RoundSchedule(
            round_number=round_obj.round_number,
            status=round_obj.status,
            matches=match_schedules
        ))

    return {"rounds": schedule}


@router.get("/{tournament_id}/current-round", response_model=CurrentRoundResponse)
def get_current_round(tournament_id: int, db: Session = Depends(get_db)):
    """Get current round with live match data."""
    tournament = TournamentService.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.current_round == 0:
        raise HTTPException(status_code=400, detail="Tournament has not started")

    round_obj = db.query(Round).filter(
        Round.tournament_id == tournament_id,
        Round.round_number == tournament.current_round
    ).first()

    if not round_obj:
        raise HTTPException(status_code=404, detail="Current round not found")

    matches = db.query(Match).filter(Match.round_id == round_obj.id).all()

    match_details = []
    for match in matches:
        player1 = db.query(Player).filter(Player.id == match.player1_id).first()
        player2 = db.query(Player).filter(Player.id == match.player2_id).first()

        player1_colors = json.loads(player1.colors) if player1.colors else []
        player2_colors = json.loads(player2.colors) if player2.colors else []

        match_details.append(MatchDetails(
            match_id=match.id,
            player1=MatchPlayerInfo(
                player_id=player1.id,
                name=player1.name,
                avatar_url=f"/uploads/avatars/{player1.avatar_path}" if player1.avatar_path else None,
                colors=player1_colors,
                health=match.player1_health
            ),
            player2=MatchPlayerInfo(
                player_id=player2.id,
                name=player2.name,
                avatar_url=f"/uploads/avatars/{player2.avatar_path}" if player2.avatar_path else None,
                colors=player2_colors,
                health=match.player2_health
            ),
            status=match.status,
            winner_id=match.winner_id
        ))

    return {
        "round_number": round_obj.round_number,
        "status": round_obj.status,
        "matches": match_details
    }
