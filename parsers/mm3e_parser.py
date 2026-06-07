"""M&M 3e JSON → DiyargezenEntity parser."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from models.entity import DiyargezenEntity
from parsers.base import parse_sections, safe_dict
from utils.data_loader import get_loader

logger = logging.getLogger(__name__)

MM_SECTIONS = {
    "abilities": "ability",
    "archetypes": "archetype",
    "skills": "skill",
    "advantages": "advantage",
    "powers": "power",
    "complications": "complication",
}


def parse_mm3e(data: Dict[str, Any] | None = None, base_dir: Path | None = None) -> List[DiyargezenEntity]:
    """mm_data.json ve foundrymnm3e-main dosyalarını parse et."""
    entities = []
    try:
        if data is None:
            try:
                data = get_loader(base_dir).load("mm")
            except Exception:
                data = {}
        data = safe_dict(data)
        entities.extend(parse_sections(data, "mm3e", MM_SECTIONS))

        # power_effects / power_levels dict-of-lists — tek tek kayıt
        for extra_key, kategori in (("power_effects", "power_effect"), ("power_levels", "power_level")):
            section = data.get(extra_key)
            if isinstance(section, dict):
                for name, val in section.items():
                    try:
                        if isinstance(val, list):
                            entities.append(
                                DiyargezenEntity(
                                    isim=str(name),
                                    sistem="mm3e",
                                    kategori=kategori,
                                    aciklama="",
                                    sistem_verisi={"name": name, "entries": val},
                                )
                            )
                    except Exception:
                        continue
    except Exception as exc:
        logger.error("M&M 3e precompiled parser hatası: %s", exc)

    # 2. Recursive scan of folders in data/
    try:
        from parsers.base import parse_raw_file
        base_path = base_dir or Path(__file__).resolve().parent.parent
        mm_content_path = base_path / "data" / "foundrymnm3e-main"
        
        if mm_content_path.exists():
            for child in mm_content_path.rglob("*"):
                if child.is_file() and child.suffix.lower() in ('.json', '.yaml', '.yml'):
                    entities.extend(parse_raw_file(child, "mm3e"))
    except Exception as exc:
        logger.error("M&M 3e recursive parser hatası: %s", exc)

    # De-duplicate by system, category, and name (case-insensitive)
    seen = set()
    unique_entities = []
    for ent in entities:
        key = (ent.sistem, ent.kategori, ent.isim.lower())
        if key not in seen:
            seen.add(key)
            unique_entities.append(ent)

    logger.info("M&M 3e: %d unique entity parse edildi", len(unique_entities))
    return unique_entities
