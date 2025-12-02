from sqlalchemy.orm import Session
from models import Match, MatchEvent, Round, Tournament
from datetime import datetime
from typing import Optional


class MatchService:
    @staticmethod
    def get_match(db: Session, match_id: int) -> Optional[Match]:
        """Get match by ID."""
        return db.query(Match).filter(Match.id == match_id).first()

    @staticmethod
    def join_match(db: Session, match_id: int, player_id: int, starting_life: int) -> Match:
        """Player joins a match."""
        match = MatchService.get_match(db, match_id)
        if not match:
            raise ValueError("Match not found")

        # Initialize health if not set
        if match.player1_id == player_id and match.player1_health is None:
            match.player1_health = starting_life
        elif match.player2_id == player_id and match.player2_health is None:
            match.player2_health = starting_life

        # Only change to "in_progress" when BOTH players have joined (both health values set)
        if match.status == "pending" and match.player1_health is not None and match.player2_health is not None:
            match.status = "in_progress"
            match.started_at = datetime.utcnow()

        # Log match start event
        event = MatchEvent(
            match_id=match_id,
            player_id=player_id,
            event_type="match_start",
            new_value=starting_life
        )
        db.add(event)

        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def update_health(db: Session, match_id: int, player_id: int, health_change: int) -> dict:
        """Update player health in match."""
        match = MatchService.get_match(db, match_id)
        if not match:
            raise ValueError("Match not found")

        if match.status != "in_progress":
            raise ValueError("Match is not in progress")

        old_health = None
        new_health = None

        if match.player1_id == player_id:
            old_health = match.player1_health
            new_health = max(0, match.player1_health + health_change)
            match.player1_health = new_health
        elif match.player2_id == player_id:
            old_health = match.player2_health
            new_health = max(0, match.player2_health + health_change)
            match.player2_health = new_health
        else:
            raise ValueError("Player not in this match")

        # Log health change event
        event = MatchEvent(
            match_id=match_id,
            player_id=player_id,
            event_type="health_change",
            old_value=old_health,
            new_value=new_health
        )
        db.add(event)

        db.commit()

        return {
            "new_health": new_health,
            "opponent_health": None  # Players don't see opponent health
        }

    @staticmethod
    def confirm_defeat(db: Session, match_id: int, loser_id: int) -> dict:
        """Player confirms defeat (health reached 0)."""
        match = MatchService.get_match(db, match_id)
        if not match:
            raise ValueError("Match not found")

        if match.status != "in_progress":
            raise ValueError("Match is not in progress")

        # Determine winner
        if match.player1_id == loser_id:
            match.winner_id = match.player2_id
        elif match.player2_id == loser_id:
            match.winner_id = match.player1_id
        else:
            raise ValueError("Player not in this match")

        match.status = "completed"
        match.completed_at = datetime.utcnow()

        # Log match end event
        event = MatchEvent(
            match_id=match_id,
            player_id=loser_id,
            event_type="match_end",
            new_value=0
        )
        db.add(event)

        db.commit()

        # Check if all matches in round are complete
        round_info = MatchService.check_round_completion(db, match.round_id)

        return {
            "match_id": match_id,
            "winner_id": match.winner_id,
            "status": "completed",
            "round_info": round_info
        }

    @staticmethod
    def check_round_completion(db: Session, round_id: int) -> dict:
        """Check if all matches in a round are complete and auto-advance if needed.
        Returns info about round advancement for broadcasting."""
        round_obj = db.query(Round).filter(Round.id == round_id).first()
        if not round_obj:
            return {"round_completed": False}

        # Count incomplete matches
        incomplete_matches = db.query(Match).filter(
            Match.round_id == round_id,
            Match.status != "completed"
        ).count()

        if incomplete_matches == 0:
            # All matches complete, advance to next round
            from services.tournament_service import TournamentService
            result = TournamentService.advance_to_next_round(db, round_obj.tournament_id)
            return {
                "round_completed": True,
                "new_round": result["current_round"],
                "tournament_status": result["status"]
            }
        
        return {"round_completed": False}

    @staticmethod
    def force_end_match(db: Session, match_id: int):
        """Admin force-ends a match."""
        match = MatchService.get_match(db, match_id)
        if not match:
            raise ValueError("Match not found")

        match.status = "completed"
        match.completed_at = datetime.utcnow()
        db.commit()

        MatchService.check_round_completion(db, match.round_id)

    @staticmethod
    def update_match_result(db: Session, match_id: int, winner_id: int):
        """Admin manually updates match result."""
        match = MatchService.get_match(db, match_id)
        if not match:
            raise ValueError("Match not found")

        if winner_id not in [match.player1_id, match.player2_id]:
            raise ValueError("Winner must be one of the match players")

        match.winner_id = winner_id
        match.status = "completed"
        match.completed_at = datetime.utcnow()

        db.commit()
