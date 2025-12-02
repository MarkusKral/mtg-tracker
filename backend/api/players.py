from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database.database import get_db
from models import Player, Match, Round, Tournament
from schemas.player import PlayerJoin, PlayerResponse, PlayerMatches, CurrentMatch, UpcomingMatch, OpponentInfo
from typing import Optional, List
import json
import os
import uuid
import shutil

router = APIRouter(prefix="/api/players", tags=["players"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
AVATARS_DIR = os.path.join(UPLOAD_DIR, "avatars")


@router.post("/join", response_model=PlayerResponse)
def join_tournament(player_data: PlayerJoin, db: Session = Depends(get_db)):
    """Player joins a tournament."""
    # Check if tournament exists
    tournament = db.query(Tournament).filter(Tournament.id == player_data.tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status != "registration":
        raise HTTPException(status_code=400, detail="Tournament registration is closed")

    # Check if name already taken
    existing = db.query(Player).filter(
        Player.tournament_id == player_data.tournament_id,
        Player.name == player_data.name
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Player name already taken in this tournament")

    # Check max players
    players_count = db.query(Player).filter(Player.tournament_id == player_data.tournament_id).count()
    if players_count >= tournament.max_players:
        raise HTTPException(status_code=400, detail="Tournament is full")

    player = Player(
        tournament_id=player_data.tournament_id,
        name=player_data.name
    )
    db.add(player)
    db.commit()
    db.refresh(player)

    return {
        "player_id": player.id,
        "tournament_id": player.tournament_id,
        "name": player.name,
        "avatar_url": None,
        "colors": None,
        "wins": 0,
        "losses": 0
    }


@router.put("/{player_id}/profile")
async def update_profile(
    player_id: int,
    name: Optional[str] = Form(None),
    colors: Optional[str] = Form(None),
    preset_id: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update player profile."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if name:
        player.name = name

    if colors:
        # Parse colors from JSON string
        try:
            colors_list = json.loads(colors)
            player.colors = json.dumps(colors_list)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid colors format")

    # Handle avatar upload
    if avatar:
        os.makedirs(AVATARS_DIR, exist_ok=True)

        # Generate unique filename
        file_ext = os.path.splitext(avatar.filename)[1]
        unique_filename = f"player_{player_id}_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(AVATARS_DIR, unique_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)

        player.avatar_path = unique_filename

    elif preset_id:
        player.avatar_path = f"preset_{preset_id}"

    db.commit()
    db.refresh(player)

    colors_list = json.loads(player.colors) if player.colors else []

    return {
        "player_id": player.id,
        "name": player.name,
        "avatar_url": f"/uploads/avatars/{player.avatar_path}" if player.avatar_path else None,
        "colors": colors_list
    }


@router.get("/{player_id}/profile", response_model=PlayerResponse)
def get_profile(player_id: int, db: Session = Depends(get_db)):
    """Get player profile."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Count wins and losses
    wins = db.query(Match).filter(Match.winner_id == player_id).count()

    player_matches = db.query(Match).filter(
        ((Match.player1_id == player_id) | (Match.player2_id == player_id)) &
        (Match.status == "completed")
    ).count()

    losses = player_matches - wins

    colors_list = json.loads(player.colors) if player.colors else []

    return {
        "player_id": player.id,
        "tournament_id": player.tournament_id,
        "name": player.name,
        "avatar_url": f"/uploads/avatars/{player.avatar_path}" if player.avatar_path else None,
        "colors": colors_list,
        "wins": wins,
        "losses": losses
    }


@router.get("/{player_id}/matches", response_model=PlayerMatches)
def get_player_matches(player_id: int, db: Session = Depends(get_db)):
    """Get player's current and upcoming matches."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    tournament = player.tournament

    # Get current round
    current_round = db.query(Round).filter(
        Round.tournament_id == tournament.id,
        Round.round_number == tournament.current_round
    ).first()

    current_match = None
    if current_round:
        match = db.query(Match).filter(
            Match.round_id == current_round.id,
            ((Match.player1_id == player_id) | (Match.player2_id == player_id))
        ).first()

        if match:
            opponent_id = match.player2_id if match.player1_id == player_id else match.player1_id
            opponent = db.query(Player).filter(Player.id == opponent_id).first()

            opponent_colors = json.loads(opponent.colors) if opponent.colors else []

            current_match = CurrentMatch(
                match_id=match.id,
                round_number=current_round.round_number,
                opponent=OpponentInfo(
                    name=opponent.name,
                    avatar_url=f"/uploads/avatars/{opponent.avatar_path}" if opponent.avatar_path else None,
                    colors=opponent_colors
                ),
                status=match.status
            )

    # Get upcoming matches
    upcoming_matches = []
    future_rounds = db.query(Round).filter(
        Round.tournament_id == tournament.id,
        Round.round_number > tournament.current_round
    ).all()

    for round_obj in future_rounds:
        match = db.query(Match).filter(
            Match.round_id == round_obj.id,
            ((Match.player1_id == player_id) | (Match.player2_id == player_id))
        ).first()

        if match:
            opponent_id = match.player2_id if match.player1_id == player_id else match.player1_id
            opponent = db.query(Player).filter(Player.id == opponent_id).first()

            upcoming_matches.append(UpcomingMatch(
                round_number=round_obj.round_number,
                opponent=opponent.name
            ))

    return PlayerMatches(
        current_match=current_match,
        upcoming_matches=upcoming_matches
    )
