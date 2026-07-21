from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class LevelProgression(Base):
    __tablename__ = "character_progression_history"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    level = Column(Integer, nullable=False)
    class_name = Column(String, nullable=False)
    choices = Column(Text, nullable=False)  # JSON string of choices
    created_at = Column(String, nullable=False)

    character = relationship("Character", back_populates="progressions")

    __table_args__ = (
        UniqueConstraint('character_id', 'level', name='_char_level_uc'),
    )
