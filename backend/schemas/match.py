from pydantic import BaseModel
from typing import Optional, List


class MatchJoin(BaseModel):
    player_id: int


class MatchHealthUpdate(BaseModel):
    player_id: int
    health_change: int


class MatchDefeat(BaseModel):
    player_id: int


class MatchResponse(BaseModel):
    match_id: int
    your_health: Optional[int]
    opponent_name: str
    status: str


class MatchResult(BaseModel):
    match_id: int
    winner_id: int
    status: str


class MatchPlayerInfo(BaseModel):
    player_id: int
    name: str
    avatar_url: Optional[str]
    colors: Optional[List[str]]
    health: Optional[int]


class MatchDetails(BaseModel):
    match_id: int
    player1: MatchPlayerInfo
    player2: MatchPlayerInfo
    status: str


class CurrentRoundResponse(BaseModel):
    round_number: int
    status: str
    matches: List[MatchDetails]


class WinnerUpdate(BaseModel):
    winner_id: int
