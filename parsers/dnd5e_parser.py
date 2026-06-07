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
    """dnd_data.json (+ backgrounds/) ve dnd-5e-srd-master dosyalarını parse et."""
    entities = []
    try:
        if data is None:
            try:
                data = get_loader(base_dir).load("dnd")
            except Exception:
                data = {}
        data = safe_dict(data)
        entities.extend(parse_sections(data, "dnd5e", DND_SECTIONS))

        # abilities bölümü D&D'de yetenek tanımları — ayrı kategori
        abilities = data.get("abilities")
        if isinstance(abilities, dict):
            from parsers.base import parse_section
            entities.extend(parse_section(abilities, "dnd5e", "ability"))
    except Exception as exc:
        logger.error("D&D 5e precompiled parser hatası: %s", exc)

    # 2. Recursive scan of folders in data/
    try:
        from parsers.base import parse_raw_file
        base_path = base_dir or Path(__file__).resolve().parent.parent
        dnd_srd_path = base_path / "data" / "dnd-5e-srd-master"
        bg_path = base_path / "data" / "backgrounds"
        
        for sp in [dnd_srd_path, bg_path]:
            if sp.exists():
                for child in sp.rglob("*"):
                    if child.is_file() and child.suffix.lower() in ('.json', '.yaml', '.yml'):
                        entities.extend(parse_raw_file(child, "dnd5e"))
    except Exception as exc:
        logger.error("D&D 5e recursive parser hatası: %s", exc)

    # De-duplicate by system, category, and name (case-insensitive)
    seen = set()
    unique_entities = []
    for ent in entities:
        key = (ent.sistem, ent.kategori, ent.isim.lower())
        if key not in seen:
            seen.add(key)
            unique_entities.append(ent)

    logger.info("D&D 5e: %d unique entity parse edildi", len(unique_entities))
    return unique_entities
