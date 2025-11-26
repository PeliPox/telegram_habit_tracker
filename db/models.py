from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    name = Column(String)
    habits = relationship("User", back_populates="user")

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    periodicity = Column(String(20), default='daily')
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="habits")