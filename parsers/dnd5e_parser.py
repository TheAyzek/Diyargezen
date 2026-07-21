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

        # Manual parsing of detailed nested equipment and items
        from parsers.base import make_entity
        
        def parse_detailed_eq(eq_data):
            if isinstance(eq_data, dict):
                for cat_name, cat_content in eq_data.items():
                    if isinstance(cat_content, dict):
                        for item_name, item_data in cat_content.items():
                            if isinstance(item_data, dict):
                                item_copy = item_data.copy()
                                if "name" not in item_copy:
                                    item_copy["name"] = item_name
                                if "type" not in item_copy:
                                    if cat_name == "armor":
                                        item_copy["type"] = "armor"
                                    elif cat_name == "weapons":
                                        item_copy["type"] = "weapon"
                                    else:
                                        item_copy["type"] = "equipment"
                                if "category" not in item_copy:
                                    item_copy["category"] = cat_name.replace("_", " ").title()
                                
                                ent = make_entity(item_name, "dnd5e", "equipment", item_copy)
                                if ent:
                                    entities.append(ent)

        parse_detailed_eq(data.get("equipment", {}))
        parse_detailed_eq(data.get("items", {}))

        # abilities bölümü D&D'de yetenek tanımları — ayrı kategori
        abilities = data.get("abilities")
        if isinstance(abilities, dict):
            from parsers.base import parse_section
            entities.extend(parse_section(abilities, "dnd5e", "ability"))
    except Exception as exc:
        logger.error("D&D 5e precompiled parser hatası: %s", exc)

    # 2. Recursive scan of folders in data/
    try:
        from parsers.base import parse_raw_file, make_entity
        base_path = base_dir or Path(__file__).resolve().parent.parent
        dnd_srd_path = base_path / "data" / "dnd-5e-srd-master"
        bg_path = base_path / "data" / "backgrounds"

        # 2a. 5esrd.json — monolithic SRD with non-standard structure
        srd_file = dnd_srd_path / "dnd-5e-srd-master" / "5esrd.json"
        if srd_file.exists():
            try:
                import json as _json
                srd = _json.loads(srd_file.read_text(encoding="utf-8"))

                SRD_CLASS_KEYS = {
                    "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
                    "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
                    "Warlock", "Wizard",
                }
                SRD_FEAT_KEYS  = {"Feats"}
                SRD_EQUIP_KEYS = {"Equipment"}

                # Races
                for race_name, race_data in srd.get("Races", {}).items():
                    if race_name in ("Racial Traits",):
                        continue
                    desc = ""
                    if isinstance(race_data, dict):
                        desc = str(race_data.get("content", race_data.get("description", "")))[:500]
                    ent = make_entity(race_name, "dnd5e", "race", {"name": race_name, "description": desc})
                    if ent:
                        entities.append(ent)

                # Classes (top-level keys)
                for key, val in srd.items():
                    if key in SRD_CLASS_KEYS:
                        desc = ""
                        if isinstance(val, dict):
                            desc = str(val.get("content", val.get("description", "")))[:500]
                        ent = make_entity(key, "dnd5e", "class", {"name": key, "hit_die": 8, "description": desc})
                        if ent:
                            entities.append(ent)

                # Feats
                feats_block = srd.get("Feats", {})
                if isinstance(feats_block, dict):
                    for feat_name, feat_data in feats_block.items():
                        if feat_name in ("content",):
                            continue
                        desc = str(feat_data)[:300] if not isinstance(feat_data, dict) else str(feat_data.get("content", ""))[:300]
                        ent = make_entity(feat_name, "dnd5e", "feat", {"name": feat_name, "description": desc})
                        if ent:
                            entities.append(ent)

                logger.info("D&D 5e SRD monolith parse edildi")
            except Exception as exc:
                logger.error("5esrd.json parse hatası: %s", exc)

        # 2b. Remaining JSON/YAML files in dnd-5e-srd-master and backgrounds
        for sp in [dnd_srd_path, bg_path]:
            if sp.exists():
                for child in sp.rglob("*"):
                    if child.is_file() and child.suffix.lower() in ('.json', '.yaml', '.yml'):
                        if child.name == "5esrd.json":
                            continue  # already handled above
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
