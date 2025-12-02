from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    avatar_path = Column(String, nullable=True)
    colors = Column(Text, nullable=True)  # JSON array: ["W", "U", "B", "R", "G"]
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    tournament = relationship("Tournament", back_populates="players")
