from sqlalchemy.orm import Session
from models import Tournament, Player, Round, Match
from services.scheduler import generate_round_robin_schedule
from datetime import datetime
from typing import List, Optional
import json


def get_avatar_url(avatar_path: Optional[str]) -> Optional[str]:
    """Get the proper avatar URL - external or local."""
    if not avatar_path:
        return None
    if avatar_path.startswith('http'):
        return avatar_path
    return f"/uploads/avatars/{avatar_path}"


class TournamentService:
    @staticmethod
    def create_tournament(db: Session, tournament_data: dict) -> Tournament:
        """Create a new tournament."""
        tournament = Tournament(**tournament_data, status="registration")
        db.add(tournament)
        db.commit()
        db.refresh(tournament)
        return tournament

    @staticmethod
    def get_tournament(db: Session, tournament_id: int) -> Optional[Tournament]:
        """Get tournament by ID."""
        return db.query(Tournament).filter(Tournament.id == tournament_id).first()

    @staticmethod
    def get_current_tournament(db: Session) -> Optional[Tournament]:
        """Get the current active or most recent tournament."""
        return db.query(Tournament).order_by(Tournament.created_at.desc()).first()

    @staticmethod
    def get_tournament_players(db: Session, tournament_id: int) -> List[Player]:
        """Get all players in a tournament."""
        return db.query(Player).filter(Player.tournament_id == tournament_id).all()

    @staticmethod
    def generate_schedule(db: Session, tournament_id: int) -> dict:
        """Generate round-robin schedule for tournament."""
        tournament = TournamentService.get_tournament(db, tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")

        players = TournamentService.get_tournament_players(db, tournament_id)
        if len(players) < 2:
            raise ValueError("Need at least 2 players to generate schedule")

        # Generate round-robin pairs
        schedule = generate_round_robin_schedule(players)

        total_matches = 0
        # Create rounds and matches
        for round_num, round_matches in enumerate(schedule, start=1):
            round_obj = Round(
                tournament_id=tournament_id,
                round_number=round_num,
                status="pending"
            )
            db.add(round_obj)
            db.flush()

            for player1, player2 in round_matches:
                match = Match(
                    round_id=round_obj.id,
                    player1_id=player1.id,
                    player2_id=player2.id,
                    status="pending"
                )
                db.add(match)
                total_matches += 1

        tournament.status = "in_progress"
        tournament.current_round = 1
        db.commit()

        return {
            "rounds_created": len(schedule),
            "total_matches": total_matches,
            "message": "Schedule generated successfully"
        }

    @staticmethod
    def get_standings(db: Session, tournament_id: int) -> List[dict]:
        """Calculate and return tournament standings."""
        players = TournamentService.get_tournament_players(db, tournament_id)
        standings = []

        for player in players:
            # Count wins
            wins = db.query(Match).filter(
                Match.winner_id == player.id
            ).count()

            # Count losses (matches where player participated but didn't win)
            player_matches = db.query(Match).filter(
                ((Match.player1_id == player.id) | (Match.player2_id == player.id)) &
                (Match.status == "completed")
            ).count()

            losses = player_matches - wins

            # Parse colors
            colors = json.loads(player.colors) if player.colors else []

            standings.append({
                "player_id": player.id,
                "name": player.name,
                "avatar_url": get_avatar_url(player.avatar_path),
                "colors": colors,
                "wins": wins,
                "losses": losses,
                "points": wins * 3  # 3 points per win
            })

        # Sort by points (wins), then by name
        standings.sort(key=lambda x: (-x["points"], x["name"]))

        # Add rank
        for i, standing in enumerate(standings, start=1):
            standing["rank"] = i

        return standings

    @staticmethod
    def advance_to_next_round(db: Session, tournament_id: int) -> dict:
        """Advance tournament to next round."""
        tournament = TournamentService.get_tournament(db, tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")

        current_round = db.query(Round).filter(
            Round.tournament_id == tournament_id,
            Round.round_number == tournament.current_round
        ).first()

        if current_round:
            current_round.status = "completed"
            current_round.completed_at = datetime.utcnow()

        # Check if there are more rounds
        next_round_num = tournament.current_round + 1
        next_round = db.query(Round).filter(
            Round.tournament_id == tournament_id,
            Round.round_number == next_round_num
        ).first()

        if next_round:
            tournament.current_round = next_round_num
            next_round.status = "in_progress"
            next_round.started_at = datetime.utcnow()
        else:
            # Tournament complete
            tournament.status = "completed"
            tournament.completed_at = datetime.utcnow()

        db.commit()

        return {
            "current_round": tournament.current_round,
            "status": tournament.status
        }
