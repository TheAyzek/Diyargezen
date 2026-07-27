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
    """pf1e-content-main, pf1e_scraped_items.json ve pathfinder_1e_data.json dosyalarını birleşik olarak parse et."""
    entities: List[DiyargezenEntity] = []
    base_path = base_dir or Path(__file__).resolve().parent.parent

    # 1. Recursive scan of Foundry VTT packs in data/pf1e-content-main (Primary rich source)
    try:
        from parsers.base import parse_raw_file
        pf1e_content_path = base_path / "data" / "pf1e-content-main"
        if pf1e_content_path.exists():
            for child in pf1e_content_path.rglob("*"):
                if child.is_file() and child.suffix.lower() in ('.json', '.yaml', '.yml', '.db'):
                    entities.extend(parse_raw_file(child, "pathfinder1e"))
    except Exception as exc:
        logger.error("PF 1e recursive parser hatası: %s", exc)

    # 2. Parse scraped items (Aonprd/d20pfsrd) for unified DB fallback
    try:
        from parsers.base import parse_raw_file
        scraped_path = base_path / "data" / "pf1e_scraped_items.json"
        if scraped_path.exists():
            scraped_entities = parse_raw_file(scraped_path, "pathfinder1e")
            for se in scraped_entities:
                if isinstance(se.sistem_verisi, dict):
                    se.sistem_verisi["data_source"] = "scraper"
            entities.extend(scraped_entities)
    except Exception as exc:
        logger.error("PF 1e scraped items parser hatası: %s", exc)

    # 3. Parse pathfinder_1e_data.json precompiled data (Fallback source)
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

    # Smart De-duplication: Prefer rich/detailed descriptions over dummy placeholders like 'Benefit' or 'Benefit(s)'
    import re
    DUMMY_DESCS = {"benefit", "benefit(s)", "prerequisites", "special", "normal", "description", ""}
    seen_map: Dict[tuple, DiyargezenEntity] = {}

    for ent in entities:
        # Strip category tag suffixes e.g. "Bleeding Critical (Combat)" -> "bleeding critical"
        clean_name = re.sub(r'\s*\((combat|teamwork|metamagic|grit|racial|performance|item creation)\)$', '', ent.isim.strip(), flags=re.I).lower().strip()
        key = (ent.sistem, ent.kategori, clean_name)
        desc_clean = (ent.aciklama or "").strip().lower()

        if key not in seen_map:
            seen_map[key] = ent
        else:
            existing = seen_map[key]
            existing_desc = (existing.aciklama or "").strip().lower()

            # If existing has a dummy/short description and new has a real description, replace
            if existing_desc in DUMMY_DESCS and desc_clean not in DUMMY_DESCS:
                seen_map[key] = ent
            elif len(ent.aciklama or "") > len(existing.aciklama or "") + 30 and desc_clean not in DUMMY_DESCS and existing_desc in DUMMY_DESCS:
                seen_map[key] = ent



    unique_entities = list(seen_map.values())
    logger.info("PF 1e: %d unique entity parse edildi (zengin açıklamalar birleştirildi)", len(unique_entities))
    return unique_entities


