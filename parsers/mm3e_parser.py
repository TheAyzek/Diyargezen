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
    """mm_data.json dosyasını parse et."""
    try:
        if data is None:
            data = get_loader(base_dir).load("mm")
        data = safe_dict(data)
        entities = parse_sections(data, "mm3e", MM_SECTIONS)

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

        logger.info("M&M 3e: %d entity parse edildi", len(entities))
        return entities
    except Exception as exc:
        logger.error("M&M 3e parser hatası: %s", exc)
        return []
