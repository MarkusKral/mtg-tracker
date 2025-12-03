from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    max_players = Column(Integer, nullable=False)
    starting_life = Column(Integer, nullable=False, default=20)
    status = Column(String, nullable=False, default="registration")
    current_round = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    players = relationship("Player", back_populates="tournament", cascade="all, delete-orphan")
    rounds = relationship("Round", back_populates="tournament", cascade="all, delete-orphan")
