from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TournamentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    draft_type: str = Field(..., min_length=1, max_length=100)
    tournament_type: str = "Round Robin"
    max_players: int = Field(..., ge=2, le=20)
    match_format: str = Field(default="Best of 1")
    starting_life: int = Field(default=20, ge=1, le=100)


class TournamentResponse(BaseModel):
    tournament_id: int
    name: str
    status: str
    current_round: int
    total_rounds: Optional[int] = None
    players_count: int

    class Config:
        from_attributes = True


class TournamentStatus(BaseModel):
    tournament_id: int
    name: str
    status: str
    current_round: int
    total_rounds: int
    players_count: int


class PlayerStanding(BaseModel):
    rank: int
    player_id: int
    name: str
    avatar_url: Optional[str]
    colors: Optional[List[str]]
    wins: int
    losses: int
    points: int


class StandingsResponse(BaseModel):
    standings: List[PlayerStanding]


class MatchSchedule(BaseModel):
    match_id: int
    player1: str
    player2: str
    winner: Optional[str]


class RoundSchedule(BaseModel):
    round_number: int
    status: str
    matches: List[MatchSchedule]


class ScheduleResponse(BaseModel):
    rounds: List[RoundSchedule]


class ScheduleGenerated(BaseModel):
    rounds_created: int
    total_matches: int
    message: str
