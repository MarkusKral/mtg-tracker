from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base


class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="pending")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    tournament = relationship("Tournament", back_populates="rounds")
    matches = relationship("Match", back_populates="round", cascade="all, delete-orphan")
