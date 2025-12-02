from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False, index=True)
    player1_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player1_health = Column(Integer, nullable=True)
    player2_health = Column(Integer, nullable=True)
    winner_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    status = Column(String, nullable=False, default="pending")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    round = relationship("Round", back_populates="matches")
    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])
    winner = relationship("Player", foreign_keys=[winner_id])
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")


class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    event_type = Column(String, nullable=False)
    old_value = Column(Integer, nullable=True)
    new_value = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="events")
    player = relationship("Player")
