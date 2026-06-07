"""D&D 5e JSON → DiyargezenEntity parser."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from models.entity import DiyargezenEntity
from parsers.base import parse_sections, safe_dict
from utils.data_loader import get_loader

logger = logging.getLogger(__name__)

DND_SECTIONS = {
    "races": "race",
    "classes": "class",
    "spells": "spell",
    "feats": "feat",
    "backgrounds": "background",
    "skills": "skill",
    "items": "item",
    "equipment": "equipment",
    "languages": "language",
}


def parse_dnd5e(data: Dict[str, Any] | None = None, base_dir: Path | None = None) -> List[DiyargezenEntity]:
    """dnd_data.json (+ backgrounds/) dosyalarını parse et."""
    try:
        if data is None:
            data = get_loader(base_dir).load("dnd")
        data = safe_dict(data)
        entities = parse_sections(data, "dnd5e", DND_SECTIONS)

        # abilities bölümü D&D'de yetenek tanımları — ayrı kategori
        abilities = data.get("abilities")
        if isinstance(abilities, dict):
            from parsers.base import parse_section
            entities.extend(parse_section(abilities, "dnd5e", "ability"))

        logger.info("D&D 5e: %d entity parse edildi", len(entities))
        return entities
    except Exception as exc:
        logger.error("D&D 5e parser hatası: %s", exc)
        return []
