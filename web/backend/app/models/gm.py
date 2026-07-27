"""Persistent PF1e Game Master decisions.

Rules are never silently bypassed: every exception and every manual modifier
is attributable, serializable, and belongs to one character.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class GMOverride(Base):
    __tablename__ = "gm_overrides"

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    selection_type = Column(String, nullable=False)  # feat, spell, item, level_up
    selection_key = Column(String, nullable=False)
    violated_rules = Column(Text, nullable=False)  # JSON array
    reason = Column(Text, nullable=False, default="GM izniyle kural esnetildi.")
    is_overridden = Column(Boolean, nullable=False, default=True)
    created_at = Column(String, nullable=False)

    character = relationship("Character", back_populates="gm_overrides")


class CharacterModifier(Base):
    __tablename__ = "character_modifiers"

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    stat = Column(String, nullable=False)  # ac, hp, bab, fortitude, reflex, will, skill:<name>
    value = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    reason = Column(Text, nullable=False, default="")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    character = relationship("Character", back_populates="gm_modifiers")


class LevelUpSession(Base):
    __tablename__ = "level_up_sessions"

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    target_level = Column(Integer, nullable=False)
    state = Column(String, nullable=False, default="started")
    choices = Column(Text, nullable=False, default="{}")
    is_overridden = Column(Boolean, nullable=False, default=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    character = relationship("Character", back_populates="level_up_sessions")
