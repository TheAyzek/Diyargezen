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
    """pathfinder_1e_data.json dosyasını parse et."""
    try:
        if data is None:
            data = get_loader(base_dir).load("pathfinder_1e")
        data = safe_dict(data)
        entities = parse_sections(data, "pathfinder1e", PF_SECTIONS)
        logger.info("PF 1e: %d entity parse edildi", len(entities))
        return entities
    except Exception as exc:
        logger.error("PF 1e parser hatası: %s", exc)
        return []
