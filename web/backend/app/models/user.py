from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

    characters = relationship("Character", back_populates="owner", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    server_id = Column(String, unique=True, index=True, nullable=True)
    system = Column(String, nullable=False)
    name = Column(String, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)

    owner = relationship("User", back_populates="characters")
    progressions = relationship("LevelProgression", back_populates="character", cascade="all, delete-orphan")
