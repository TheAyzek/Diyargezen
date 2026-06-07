"""Pathfinder 1e JSON → DiyargezenEntity parser."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from models.entity import DiyargezenEntity
from parsers.base import parse_sections, safe_dict
from utils.data_loader import get_loader

logger = logging.getLogger(__name__)

PF_SECTIONS = {
    "races": "race",
    "classes": "class",
    "spells": "spell",
    "feats": "feat",
    "skills": "skill",
    "items": "item",
}


def parse_pf1e(data: Dict[str, Any] | None = None, base_dir: Path | None = None) -> List[DiyargezenEntity]:
    """pathfinder_1e_data.json ve pf1e-content-main dosyalarını parse et."""
    entities = []
    try:
        if data is None:
            try:
                data = get_loader(base_dir).load("pathfinder_1e")
            except Exception:
                data = {}
        data = safe_dict(data)
        entities.extend(parse_sections(data, "pathfinder1e", PF_SECTIONS))
    except Exception as exc:
        logger.error("PF 1e precompiled parser hatası: %s", exc)

    # 2. Recursive scan of folders in data/
    try:
        from parsers.base import parse_raw_file
        base_path = base_dir or Path(__file__).resolve().parent.parent
        pf1e_content_path = base_path / "data" / "pf1e-content-main"
        
        if pf1e_content_path.exists():
            for child in pf1e_content_path.rglob("*"):
                if child.is_file() and child.suffix.lower() in ('.json', '.yaml', '.yml', '.db'):
                    entities.extend(parse_raw_file(child, "pathfinder1e"))
    except Exception as exc:
        logger.error("PF 1e recursive parser hatası: %s", exc)

    # De-duplicate by system, category, and name (case-insensitive)
    seen = set()
    unique_entities = []
    for ent in entities:
        key = (ent.sistem, ent.kategori, ent.isim.lower())
        if key not in seen:
            seen.add(key)
            unique_entities.append(ent)

    logger.info("PF 1e: %d unique entity parse edildi", len(unique_entities))
    return unique_entities
