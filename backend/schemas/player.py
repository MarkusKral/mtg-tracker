from pydantic import BaseModel, Field
from typing import Optional, List


class PlayerJoin(BaseModel):
    tournament_id: int
    name: str = Field(..., min_length=1, max_length=50)


class PlayerResponse(BaseModel):
    player_id: int
    tournament_id: int
    name: str
    avatar_url: Optional[str] = None
    colors: Optional[List[str]] = None
    wins: Optional[int] = 0
    losses: Optional[int] = 0

    class Config:
        from_attributes = True


class PlayerProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    colors: Optional[List[str]] = None
    preset_id: Optional[str] = None


class OpponentInfo(BaseModel):
    name: str
    avatar_url: Optional[str]
    colors: Optional[List[str]]


class CurrentMatch(BaseModel):
    match_id: int
    round_number: int
    opponent: OpponentInfo
    status: str


class UpcomingMatch(BaseModel):
    round_number: int
    opponent: str


class PlayerMatches(BaseModel):
    current_match: Optional[CurrentMatch]
    upcoming_matches: List[UpcomingMatch]
