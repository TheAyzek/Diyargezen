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
            from utils.source_files import source_files
            for child, metadata in source_files(pf1e_content_path):
                parsed = parse_raw_file(child, "pathfinder1e")
                reference = f'foundry:{child.relative_to(base_path)}:{metadata.st_mtime_ns}'
                for entity in parsed:
                    entity.sistem_verisi['data_source'] = 'foundry'
                    entity.sistem_verisi['_source_ref'] = reference
                entities.extend(parsed)
    except Exception as exc:
        logger.error("PF 1e recursive parser hatası: %s", exc)

    # 2. Parse scraped items (Aonprd/d20pfsrd) for unified DB fallback
    try:
        from parsers.base import parse_raw_file
        scraped_path = base_path / "data" / "pf1e_scraped_items.json"
        if scraped_path.exists():
            scraped_entities = parse_raw_file(scraped_path, "pathfinder1e")
            reference = f'scraper:{scraped_path.name}:{scraped_path.stat().st_mtime_ns}'
            for se in scraped_entities:
                if isinstance(se.sistem_verisi, dict):
                    se.sistem_verisi["data_source"] = "scraper"
                    se.sistem_verisi['_source_ref'] = reference
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
        bundled = parse_sections(data, "pathfinder1e", PF_SECTIONS)
        for entity in bundled:
            entity.sistem_verisi['data_source'] = 'bundled'
        entities.extend(bundled)
    except Exception as exc:
        logger.error("PF 1e precompiled parser hatası: %s", exc)

    from parsers.pf1e_unified import merge_entities
    unique_entities = merge_entities(entities)

    # Enrich class entities with full PF1e Class Details dataset (class_skills, hit_die, etc.)
    try:
        from scraper.seed_pf1e_class_details import PF1E_CLASS_FULL_DETAILS
        for ent in unique_entities:
            if ent.kategori in ("class", "archetype") and isinstance(ent.sistem_verisi, dict):
                for cls_name, info in PF1E_CLASS_FULL_DETAILS.items():
                    if cls_name.lower() == ent.isim.lower().strip():
                        from parsers.pf1e_unified import missing
                        for field in ('hit_die', 'skill_ranks_per_level', 'saving_throws', 'proficiencies', 'class_skills', 'spellcasting', 'spellcasting_type'):
                            if missing(ent.sistem_verisi.get(field)):
                                ent.sistem_verisi[field] = info[field]
                                ent.sistem_verisi['_provenance']['field_sources'][field] = 'curated'
                        break
    except Exception as exc:
        logger.warning("Class details enrichment warning: %s", exc)

    # Enrich race entities with official PF1e Race Ability Score Increase (ASI) dataset
    try:
        from tools.update_race_data import OFFICIAL_PF1E_ASI, format_asi_text
        for ent in unique_entities:
            if ent.kategori == "race" and isinstance(ent.sistem_verisi, dict):
                r_name = ent.isim.lower().strip()
                if r_name in OFFICIAL_PF1E_ASI:
                    asi = OFFICIAL_PF1E_ASI[r_name]
                    if not ent.sistem_verisi.get('ability_score_increase'):
                        ent.sistem_verisi["ability_score_increase"] = asi
                        ent.sistem_verisi["ability_score_increase_text"] = format_asi_text(asi)
                        ent.sistem_verisi['_provenance']['field_sources']['ability_score_increase'] = 'curated'
    except Exception as exc:
        logger.warning("Race ASI enrichment warning: %s", exc)

    logger.info("PF 1e: %d unique entity parse edildi (zengin açıklamalar birleştirildi)", len(unique_entities))
    return unique_entities


