from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.sql import func
from database.database import Base


class AdminConfig(Base):
    __tablename__ = "admin_config"

    id = Column(Integer, primary_key=True, default=1)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('id = 1', name='single_row_check'),
    )
