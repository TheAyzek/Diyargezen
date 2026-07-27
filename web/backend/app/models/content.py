"""Unified PF1e catalogue: canonical content plus its Foundry/scraper provenance."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True)
    content_type = Column(String, nullable=False, index=True)  # feat, spell, item, trait ...
    slug = Column(String, nullable=False)
    name = Column(String, nullable=False)
    data = Column(Text, nullable=False)  # resolved canonical JSON
    resolution = Column(String, nullable=False, default="foundry")  # foundry, scraper_fallback, merged
    is_active = Column(Boolean, nullable=False, default=True)

    sources = relationship("ContentSource", back_populates="item", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("content_type", "slug", name="uq_pf1e_content_type_slug"),)


class ContentSource(Base):
    __tablename__ = "content_sources"

    id = Column(Integer, primary_key=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False, index=True)
    source_kind = Column(String, nullable=False)  # foundry or scraper
    source_key = Column(String, nullable=False)
    raw_data = Column(Text, nullable=False)
    imported_at = Column(String, nullable=False)

    item = relationship("ContentItem", back_populates="sources")
    __table_args__ = (UniqueConstraint("source_kind", "source_key", name="uq_pf1e_content_source"),)
