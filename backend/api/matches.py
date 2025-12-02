from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models import Match, Player, Tournament
from schemas.match import MatchJoin, MatchHealthUpdate, MatchDefeat, MatchResponse, MatchResult
from services.match_service import MatchService

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.post("/{match_id}/join", response_model=MatchResponse)
def join_match(
    match_id: int,
    join_data: MatchJoin,
    db: Session = Depends(get_db)
):
    """Player joins their assigned match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if join_data.player_id not in [match.player1_id, match.player2_id]:
        raise HTTPException(status_code=400, detail="Player not assigned to this match")

    # Get tournament starting life
    round_obj = match.round
    tournament = round_obj.tournament
    starting_life = tournament.starting_life

    try:
        updated_match = MatchService.join_match(db, match_id, join_data.player_id, starting_life)

        opponent_id = updated_match.player2_id if updated_match.player1_id == join_data.player_id else updated_match.player1_id
        opponent = db.query(Player).filter(Player.id == opponent_id).first()

        your_health = updated_match.player1_health if updated_match.player1_id == join_data.player_id else updated_match.player2_health

        return {
            "match_id": updated_match.id,
            "your_health": your_health,
            "opponent_name": opponent.name,
            "status": updated_match.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{match_id}/health")
async def update_health(
    match_id: int,
    health_data: MatchHealthUpdate,
    db: Session = Depends(get_db)
):
    """Update player health."""
    try:
        result = MatchService.update_health(
            db,
            match_id,
            health_data.player_id,
            health_data.health_change
        )
        # Broadcast health update to dashboard via WebSocket
        from api.websockets import broadcast_health_update
        await broadcast_health_update(match_id, health_data.player_id, result['new_health'])
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{match_id}/defeat", response_model=MatchResult)
async def confirm_defeat(
    match_id: int,
    defeat_data: MatchDefeat,
    db: Session = Depends(get_db)
):
    """Player confirms defeat."""
    try:
        result = MatchService.confirm_defeat(db, match_id, defeat_data.player_id)
        # Broadcast match completion to all connected clients
        from api.websockets import broadcast_match_complete, broadcast_round_complete
        await broadcast_match_complete(match_id, result['winner_id'])
        
        # If round completed, broadcast that too
        round_info = result.pop('round_info', {})
        if round_info.get('round_completed'):
            await broadcast_round_complete(round_info.get('new_round', 0))
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
