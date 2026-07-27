"""Parser yardımcıları — eksik key'lerde çökmez."""

from __future__ import annotations

import logging
import json
import re
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import yaml

from models.entity import DiyargezenEntity

logger = logging.getLogger(__name__)


# kategori → creators'ın beklediği dict anahtarı
CATEGORY_TO_SECTION: Dict[str, str] = {
    "race": "races",
    "class": "classes",
    "spell": "spells",
    "feat": "feats",
    "background": "backgrounds",
    "skill": "skills",
    "item": "items",
    "equipment": "equipment",
    "power": "powers",
    "advantage": "advantages",
    "ability": "abilities",
    "archetype": "archetypes",
    "complication": "complications",
    "language": "languages",
}


def safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value).strip()
    except Exception:
        return default


def safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def extract_description(payload: Any) -> str:
    if not payload:
        return ""
    if isinstance(payload, dict):
        for key in ("description", "desc", "benefit", "text", "summary", "details", "value", "entries", "content"):
            if key in payload:
                val = payload[key]
                if isinstance(val, str) and val.strip():
                    txt = val.strip()
                    if txt.lower() in ("benefit", "benefit(s)", "prerequisites", "special", "normal", "description"):
                        continue
                    return txt

                elif isinstance(val, list):
                    parts = []
                    for item in val:
                        if isinstance(item, str) and item.strip():
                            parts.append(item.strip())
                        elif isinstance(item, dict):
                            nested = extract_description(item)
                            if nested:
                                parts.append(nested)
                    if parts:
                        return "\n\n".join(parts)
                elif isinstance(val, dict):
                    nested = extract_description(val)
                    if nested:
                        return nested
        for val in payload.values():
            if isinstance(val, (dict, list)):
                nested = extract_description(val)
                if nested:
                    return nested
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, (dict, list)):
                nested = extract_description(item)
                if nested:
                    return nested
            elif isinstance(item, str) and item.strip():
                return item.strip()
    return ""


def extract_standard_mechanics(data: Dict[str, Any], system: str) -> Dict[str, Any]:
    mechanics = []
    prerequisites = []
    
    sys_key = system.lower().replace("_", "").replace("-", "")
    
    if "dnd" in sys_key:
        sys_data = data.get("system") or data.get("data") or {}
        if not isinstance(sys_data, dict):
            sys_data = {}
            
        # 1. Requirements (Prerequisites)
        req = sys_data.get("requirements") or data.get("requirements")
        if req and isinstance(req, str):
            match = re.search(r'\b(Strength|Str|Dexterity|Dex|Constitution|Con|Intelligence|Int|Wisdom|Wis|Charisma|Cha)\s*(\d+)\b', req, re.IGNORECASE)
            if match:
                ability_map = {
                    "str": "strength", "strength": "strength",
                    "dex": "dexterity", "dexterity": "dexterity",
                    "con": "constitution", "constitution": "constitution",
                    "int": "intelligence", "intelligence": "intelligence",
                    "wis": "wisdom", "wisdom": "wisdom",
                    "cha": "charisma", "charisma": "charisma"
                }
                ab = ability_map.get(match.group(1).lower())
                val = int(match.group(2))
                if ab:
                    prerequisites.append({"prerequisite": ab, "value": val})
                    
        # 2. Modifiers
        mods = sys_data.get("modifiers") or data.get("modifiers")
        if isinstance(mods, list):
            for m in mods:
                if isinstance(m, dict):
                    target = m.get("target", "")
                    value = m.get("value", 0)
                    mode = m.get("mode", "add")
                    dex_max = m.get("dex_max")
                    if target:
                        mechanics.append({
                            "target": str(target).lower(),
                            "mode": str(mode).lower(),
                            "value": value,
                            "dex_max": int(dex_max) if dex_max is not None else None
                        })
                        
        # 3. Bonuses
        bonuses = sys_data.get("bonuses") or data.get("bonuses")
        if isinstance(bonuses, dict):
            for k, v in bonuses.items():
                target = k.lower()
                if target == "ac":
                    target = "ac"
                elif "save" in target:
                    target = "saving_throws.all"
                
                try:
                    val = int(str(v).replace("+", "").strip())
                    mechanics.append({
                        "target": target,
                        "mode": "add",
                        "value": val,
                        "dex_max": None
                    })
                except ValueError:
                    pass

        # 4. Ability Score Increase (Racial Stats)
        asi = data.get("ability_score_increase") or sys_data.get("ability_score_increase")
        if isinstance(asi, dict):
            for k, v in asi.items():
                target = k.lower()
                try:
                    mechanics.append({
                        "target": target,
                        "mode": "add",
                        "value": int(v),
                        "dex_max": None
                    })
                except ValueError:
                    pass

        # 5. Armor/Shield AC Mechanics
        item_type = str(data.get("type", "")).lower()
        ac_val = data.get("ac")
        if ac_val is not None:
            try:
                ac_val = int(ac_val)
                armor_type = str(data.get("armor_type", "")).lower()
                if item_type == "shield" or "shield" in str(data.get("name", "")).lower() or armor_type == "shield":
                    mechanics.append({
                        "target": "ac",
                        "mode": "shield",
                        "value": ac_val,
                        "dex_max": None
                    })
                else:
                    # It's armor
                    dex_max = None
                    if armor_type == "medium":
                        dex_max = 2
                    elif armor_type == "heavy":
                        dex_max = 0
                    
                    mechanics.append({
                        "target": "ac",
                        "mode": "armor",
                        "value": ac_val,
                        "dex_max": dex_max
                    })
            except ValueError:
                pass

    elif "pathfinder" in sys_key or "pf" in sys_key:
        sys_data = data.get("system") or data.get("data") or {}
        if not isinstance(sys_data, dict):
            sys_data = {}
            
        # 1. Prerequisites
        prereqs = sys_data.get("prerequisites") or data.get("prerequisites")
        if isinstance(prereqs, list):
            for p in prereqs:
                if isinstance(p, dict):
                    target = p.get("target") or p.get("ability")
                    value = p.get("value") or p.get("level")
                    if target and value:
                        prerequisites.append({
                            "prerequisite": str(target).lower(),
                            "value": int(value)
                        })
        elif isinstance(prereqs, str):
            matches = re.findall(r'\b(Str|Strength|Dex|Dexterity|Con|Constitution|Int|Intelligence|Wis|Wisdom|Cha|Charisma)\s*(\d+)\b', prereqs, re.IGNORECASE)
            ability_map = {
                "str": "strength", "strength": "strength",
                "dex": "dexterity", "dexterity": "dexterity",
                "con": "constitution", "constitution": "constitution",
                "int": "intelligence", "intelligence": "intelligence",
                "wis": "wisdom", "wisdom": "wisdom",
                "cha": "charisma", "charisma": "charisma"
            }
            for ab_name, val in matches:
                ab = ability_map.get(ab_name.lower())
                if ab:
                    prerequisites.append({"prerequisite": ab, "value": int(val)})

        # 2. Changes
        changes = sys_data.get("changes") or data.get("changes")
        if isinstance(changes, list):
            for c in changes:
                if isinstance(c, dict):
                    target = c.get("target") or c.get("subTarget") or ""
                    value = c.get("value") or c.get("formula") or 0
                    operator = c.get("operator") or c.get("mode") or "add"
                    
                    target_str = str(target).lower()
                    mode_str = str(operator).lower()
                    dex_max = c.get("dex_max")
                    
                    if "ability.str" in target_str or target_str == "str":
                        target_norm = "strength"
                    elif "ability.dex" in target_str or target_str == "dex":
                        target_norm = "dexterity"
                    elif "ability.con" in target_str or target_str == "con":
                        target_norm = "constitution"
                    elif "ability.int" in target_str or target_str == "int":
                        target_norm = "intelligence"
                    elif "ability.wis" in target_str or target_str == "wis":
                        target_norm = "wisdom"
                    elif "ability.cha" in target_str or target_str == "cha":
                        target_norm = "charisma"
                    elif "ac" in target_str or target_str == "ac.armor" or target_str == "ac.shield" or target_str == "ac.natural" or target_str == "ac.deflection":
                        target_norm = "ac"
                        if "armor" in target_str:
                            mode_str = "armor"
                        elif "shield" in target_str:
                            mode_str = "shield"
                        elif "natural" in target_str:
                            mode_str = "natural_armor"
                        elif "deflection" in target_str:
                            mode_str = "deflection"
                    elif "saves.fort" in target_str or target_str == "fort":
                        target_norm = "saving_throws.Fortitude"
                    elif "saves.ref" in target_str or target_str == "ref" or target_str == "reflex":
                        target_norm = "saving_throws.Reflex"
                    elif "saves.will" in target_str or target_str == "will":
                        target_norm = "saving_throws.Will"
                    elif "skills" in target_str:
                        parts = target_str.split('.')
                        skill_ab = parts[1] if len(parts) > 1 else ""
                        skill_map = {
                            "acr": "Acrobatics", "app": "Appraise", "blf": "Bluff", "cli": "Climb", "cra": "Craft",
                            "dip": "Diplomacy", "dev": "Disable Device", "dsg": "Disguise", "esc": "Escape Artist",
                            "fly": "Fly", "han": "Handle Animal", "hea": "Heal", "itm": "Intimidate", "lin": "Linguistics",
                            "per": "Perception", "prf": "Perform", "pro": "Profession", "rid": "Ride", "sen": "Sense Motive",
                            "slt": "Sleight of Hand", "spl": "Spellcraft", "ste": "Stealth", "sur": "Survival", "swm": "Swim",
                            "umd": "Use Magic Device"
                        }
                        skill_name = skill_map.get(skill_ab, skill_ab.capitalize())
                        target_norm = f"skills.{skill_name}"
                    elif target_str in ("bab", "cmb", "cmd", "speed", "hp", "initiative"):
                        target_norm = target_str
                    else:
                        target_norm = target_str
                        
                    try:
                        val_resolved = int(float(value))
                    except ValueError:
                        val_resolved = value
                        
                    mechanics.append({
                        "target": target_norm,
                        "mode": mode_str,
                        "value": val_resolved,
                        "dex_max": int(dex_max) if dex_max is not None else None
                    })
                    
        # 3. Active effects
        effects = data.get("effects") or sys_data.get("effects")
        if isinstance(effects, list):
            for eff in effects:
                if isinstance(eff, dict) and eff.get("changes"):
                    for c in eff["changes"]:
                        if isinstance(c, dict):
                            target = c.get("key") or ""
                            value = c.get("value") or 0
                            operator = c.get("mode") or "add"
                            
                            target_str = str(target).lower()
                            try:
                                val_resolved = int(float(value))
                            except ValueError:
                                val_resolved = value
                                
                            mechanics.append({
                                "target": target_str,
                                "mode": "add" if str(operator) == "2" else "set",
                                "value": val_resolved,
                                "dex_max": None
                            })

        # 4. Text-based ability modifier extraction for subraces/traits if changes/mechanics are empty
        if not mechanics:
            desc_val = data.get("description")
            desc = desc_val.get("value", "") if isinstance(desc_val, dict) else (desc_val or "")
            desc_clean = re.sub(r'<[^>]+>', ' ', desc)
            desc_clean = desc_clean.replace("–", "-").replace("—", "-").replace("&ndash;", "-").replace("&mdash;", "-").replace("−", "-").replace("&minus;", "-")
            match = re.search(r'ability\s+modifiers\s*[:\s]*([+-]?\d+\s+[a-zA-Z]+(?:,\s*[+-]?\d+\s+[a-zA-Z]+)*)', desc_clean, re.IGNORECASE)
            if match:
                mods_str = match.group(1)
                ab_matches = re.findall(r'([+-]?\d+)\s+([a-zA-Z]+)', mods_str)
                ability_map = {
                    "str": "strength", "strength": "strength",
                    "dex": "dexterity", "dexterity": "dexterity",
                    "con": "constitution", "constitution": "constitution",
                    "int": "intelligence", "intelligence": "intelligence",
                    "wis": "wisdom", "wisdom": "wisdom",
                    "cha": "charisma", "charisma": "charisma"
                }
                for val_str, ab_name in ab_matches:
                    ab = ability_map.get(ab_name.lower())
                    if ab:
                        try:
                            val = int(val_str)
                            mechanics.append({
                                "target": ab,
                                "mode": "add",
                                "value": val,
                                "dex_max": None
                            })
                        except ValueError:
                            pass

    elif "mm" in sys_key:
        effs = data.get("effects") or data.get("system", {}).get("effects", [])
        if isinstance(effs, list):
            for e in effs:
                if isinstance(e, dict):
                    target = e.get("target") or e.get("defense") or e.get("stat")
                    value = e.get("value") or e.get("ranks") or e.get("mod") or 0
                    if target:
                        try:
                            val_resolved = int(float(value))
                        except ValueError:
                            val_resolved = value
                        mechanics.append({
                            "target": str(target).lower(),
                            "mode": "add",
                            "value": val_resolved,
                            "dex_max": None
                        })
                        
        mods = data.get("modifiers") or data.get("system", {}).get("modifiers", [])
        if isinstance(mods, list):
            for m in mods:
                if isinstance(m, dict):
                    target = m.get("target") or m.get("defense")
                    value = m.get("value") or m.get("ranks") or m.get("mod") or 0
                    if target:
                        try:
                            val_resolved = int(float(value))
                        except ValueError:
                            val_resolved = value
                        mechanics.append({
                            "target": str(target).lower(),
                            "mode": "add",
                            "value": val_resolved,
                            "dex_max": None
                        })
                        
        desc = data.get("description", "") or data.get("aciklama", "")
        name = data.get("name", "") or data.get("isim", "")
        text_to_scan = f"{name} {desc}"
        pattern = r'\+?(-?\d+)\s*(Dodge|Parry|Toughness|Fortitude|Will|Initiative|Speed|Strength|Stamina|Agility|Dexterity|Fighting|Intellect|Awareness|Presence)'
        matches = re.findall(pattern, text_to_scan, re.IGNORECASE)
        for val, stat in matches:
            mechanics.append({
                "target": stat.lower(),
                "mode": "add",
                "value": int(val),
                "dex_max": None
            })
            
    return {
        "standard_mechanics": mechanics,
        "prerequisites": prerequisites
    }


def load_any_file(path: Path) -> List[Dict[str, Any]]:
    entities = []
    suffix = path.suffix.lower()
    
    if suffix == '.db':
        try:
            with path.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            entities.append(obj)
                    except Exception:
                        pass
            if entities:
                return entities
        except Exception:
            pass

    if suffix in ('.json', '.db'):
        try:
            with path.open('r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith('{') or content.startswith('['):
                    raw = json.loads(content)
                    if isinstance(raw, list):
                        return raw
                    elif isinstance(raw, dict):
                        return [raw]
        except Exception:
            try:
                with path.open('r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            if isinstance(obj, dict):
                                entities.append(obj)
                        except Exception:
                            pass
                if entities:
                    return entities
            except Exception:
                pass

    if suffix in ('.yaml', '.yml'):
        try:
            with path.open('r', encoding='utf-8') as f:
                raw = yaml.safe_load(f)
                if isinstance(raw, list):
                    return raw
                elif isinstance(raw, dict):
                    return [raw]
        except Exception:
            pass
            
    return entities


def should_skip_path(path: Path) -> bool:
    path_str = str(path.resolve()).lower()
    
    # 1. Filter out pure text files (journal/rules without system mechanics)
    suffix = path.suffix.lower()
    if suffix in ('.json', '.yaml', '.yml'):
        try:
            with path.open('r', encoding='utf-8') as f:
                chunk = f.read(8000)
                if '"content"' in chunk and not any(x in chunk for x in ['"system"', '"changes"', '"ability_score_increase"', '"modifiers"']):
                    return True
        except Exception:
            pass

    # 2. Blacklist directories only (excluding the filename to avoid skipping valid feats/traits)
    blacklist = {
        "tables", "scenes", "kingdom", "encounter", "buffs", 
        "merchant", "maladi", "trap", "reference", "legal", "combat", 
        "running", "npc", "creature", "monster", "plane", "deities", 
        "harrow", "deck", "mechanic", "rules"
    }
    
    for part in path.parent.parts:
        part_lower = part.lower()
        if ":" in part_lower:
            continue
        for word in blacklist:
            if word in part_lower:
                return True
    return False


def parse_raw_file(path: Path, system: str) -> List[DiyargezenEntity]:
    if should_skip_path(path):
        return []
        
    entities = []
    suffix = path.suffix.lower()
    if suffix not in ('.json', '.yaml', '.yml', '.db'):
        return []

    try:
        if suffix in ('.json', '.yaml', '.yml'):
            with path.open('r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    if suffix == '.json':
                        raw = json.loads(content)
                    else:
                        raw = yaml.safe_load(content)
                    
                    if isinstance(raw, dict):
                        sect_keys = {"races", "classes", "spells", "feats", "backgrounds", "skills", "items", "equipment", "powers", "advantages", "abilities", "archetypes", "complications", "languages"}
                        found_sections = sect_keys.intersection(raw.keys())
                        if found_sections:
                            mapping = {val: key for key, val in CATEGORY_TO_SECTION.items() if val in raw}
                            return parse_sections(raw, system, mapping)
    except Exception:
        pass

    raw_list = load_any_file(path)
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        
        name = safe_str(item.get("name") or item.get("id") or item.get("key"))
        if not name:
            continue
            
        kategori = None
        item_type = safe_str(item.get("type")).lower()

        # STRICT TYPE RESOLUTION — FoundryVTT inner 'type' field is the
        # ground truth.  CRITICAL: 'race_trait', 'racial', 'feat' are NOT races.
        TYPE_MAP = {
            "race":       "race",
            "feat":       "feat",
            "race_trait": "feat",   # PF1e racial trait stored as type=feat
            "racial":     "feat",   # generic racial ability, NOT a race
            "trait":      "trait",  # character trait — distinct from feat
            "spell":      "spell",
            "class":      "class",
            "advantage":  "advantage",
            "power":      "power",
            "weapon":     "equipment",
            "armor":      "equipment",
            "shield":     "equipment",
            "equipment":  "equipment",
            "loot":       "equipment",
            "consumable": "equipment",
            "container":  "equipment",
            "backpack":   "equipment",
            "item":       "equipment",
            "buff":       "buff",
            "character":  "npc",
            "npc":        "npc",
            "attack":     "feat",
        }
        if item_type:
            kategori = TYPE_MAP.get(item_type)

            
        if not kategori:
            name_and_parent = (path.parent.name + "_" + path.name).lower()

            # 'racial-traits', 'pf-racial-traits' etc. are FEATS not races
            if "racial-trait" in name_and_parent or "pf-racial" in name_and_parent:
                kategori = "feat"
            elif "race" in name_and_parent or "racial" in name_and_parent:
                kategori = "race"
            elif "class" in name_and_parent or "archetype" in name_and_parent:
                kategori = "class"
            elif "feat" in name_and_parent:
                kategori = "feat"
            elif "spell" in name_and_parent or "magic" in name_and_parent:
                kategori = "spell"
            elif "item" in name_and_parent or "equipment" in name_and_parent or "wondrous" in name_and_parent or "goods" in name_and_parent or "technology" in name_and_parent or "artifact" in name_and_parent:
                kategori = "equipment"
            elif "power" in name_and_parent:
                kategori = "power"
            elif "advantage" in name_and_parent:
                kategori = "advantage"
            elif "skill" in name_and_parent:
                kategori = "skill"
            elif "rule" in name_and_parent or "reference" in name_and_parent or "table" in name_and_parent or "kingdom" in name_and_parent or "harrow" in name_and_parent or "trap" in name_and_parent or "malad" in name_and_parent or "deit" in name_and_parent or "ritual" in name_and_parent:
                kategori = "rule"
            elif "special" in name_and_parent or "monster" in name_and_parent or "companion" in name_and_parent or "eidolon" in name_and_parent:
                kategori = "feat"
            else:
                # Default rule fallback for raw content entries (like pf-rules.db)
                if "content" in item or "description" in item:
                    kategori = "rule"
                else:
                    kategori = None

        if not kategori:
            continue

        ent = make_entity(name, system, kategori, item)
        if ent:
            entities.append(ent)

    return entities


def detect_parent_race(name: str, system: str) -> Optional[str]:
    name_clean = name.strip()
    sys_key = system.lower().replace("_", "").replace("-", "")
    
    if "dnd" in sys_key:
        main_races = {"Dwarf", "Elf", "Halfling", "Human", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling", "Aasimar", "Genasi", "Goliath", "Tabaxi", "Triton", "Firbolg", "Kenku", "Lizardfolk"}
        if name_clean in main_races:
            return None
            
        for p in main_races:
            if f"{p} (" in name_clean or name_clean.endswith(f" {p}"):
                return p
                
        # Fallback keyword checks
        name_lower = name_clean.lower()
        if "dwarf" in name_lower: return "Dwarf"
        if "elf" in name_lower and "half-elf" not in name_lower: return "Elf"
        if "gnome" in name_lower: return "Gnome"
        if "halfling" in name_lower: return "Halfling"
        if "aasimar" in name_lower: return "Aasimar"
        if "genasi" in name_lower: return "Genasi"
        if "goliath" in name_lower: return "Goliath"
        if "tabaxi" in name_lower: return "Tabaxi"
        if "triton" in name_lower: return "Triton"
        if "firbolg" in name_lower: return "Firbolg"
        if "kenku" in name_lower: return "Kenku"
        if "lizardfolk" in name_lower: return "Lizardfolk"
        
    elif "pf" in sys_key or "pathfinder" in sys_key:
        main_races = {
            "Aasimar", "Tiefling", "Elf", "Dwarf", "Halfling", "Gnome", 
            "Human", "Half-Elf", "Half-Orc", "Changeling", "Dhampir",
            "Ganzi", "Goblin", "Ifrit", "Merfolk", "Oread", "Skinwalker",
            "Sylph", "Undine", "Gillman"
        }
        if name_clean in main_races:
            return None
            
        name_lower = name_clean.lower()
        
        # Aasimar heritages
        aasimar_heritages = ["idyllkin", "angelkin", "lawbringers", "musetouched", "plumekith", "emberkin", "agathion-blooded", "angel-blooded", "archon-blooded", "azata-blooded", "garuda-blooded", "peri-blooded"]
        if any(h in name_lower for h in aasimar_heritages):
            return "Aasimar"
            
        # Tiefling heritages
        tiefling_heritages = ["hellspawn", "grimspawn", "pitborn", "faultspawn", "spitespawn", "shackleborn", "beastbrood", "hungerseed", "motherless", "plagueborn", "daemon-spawn", "demon-spawn", "devil-spawn", "div-spawn", "kyton-spawn", "oni-spawn", "rakshasa-spawn", "qlippoth-spawn"]
        if any(h in name_lower for h in tiefling_heritages):
            return "Tiefling"
            
        for p in main_races:
            if p.lower() in name_lower:
                if p == "Elf" and "half-elf" in name_lower:
                    return "Half-Elf"
                if p == "Orc" and "half-orc" in name_lower:
                    return "Half-Orc"
                return p
                
    return None


def make_entity(
    isim: str,
    sistem: str,
    kategori: str,
    payload: Any,
) -> Optional[DiyargezenEntity]:
    """Tek bir kaydı güvenli şekilde DiyargezenEntity'ye dönüştür.

    Kategori çözümleme önceliği (azalan sırayla):
    1. FoundryVTT dosyasındaki 'type' alanı  (parse_raw_file tarafından zaten
       type_map'e göre çözülüp buraya verilir)
    2. detect_parent_race — sadece parent_race METADATA ekler;
       kategori değiştirmez (feat bir feat kalır!)
    3. Gerçek 'type=="race"' ise zaten 'race' olarak gelmiştir.
    """
    try:
        name = safe_str(isim)
        if not name:
            return None
        data = safe_dict(payload)
        if not data.get("name"):
            data = {**data, "name": name}

        # ----------------------------------------------------------------
        # STRICT TYPE CHECK — if the raw data explicitly declares a type
        # that contradicts the folder-inferred category, honour the raw type.
        # ----------------------------------------------------------------
        inner_type = safe_str(data.get("type")).lower()
        if inner_type:
            strict_type_map = {
                "race":       "race",
                "feat":       "feat",
                "race_trait": "feat",
                "racial":     "feat",
                "trait":      "trait",   # <-- proper trait category
                "spell":      "spell",
                "class":      "class",
                "weapon":     "equipment",
                "armor":      "equipment",
                "shield":     "equipment",
                "equipment":  "equipment",
                "loot":       "equipment",
                "consumable": "equipment",
                "container":  "equipment",
                "backpack":   "equipment",
                "item":       "equipment",
            }
            resolved = strict_type_map.get(inner_type)
            if resolved:
                kategori = resolved   # inner type always wins

        # ----------------------------------------------------------------
        # PF1e featType sub-classification:
        # FoundryVTT PF1e stores feats with type='feat' AND a 'featType'
        # sub-field that distinguishes actual feats from character traits.
        # Values like 'trait', 'social', 'combat', 'regional', 'religion',
        # 'magic', 'racial' in featType → store as kategori='trait'.
        # ----------------------------------------------------------------
        sys_key = safe_str(data.get("system", {}).get("featType") if isinstance(data.get("system"), dict) else "").lower()
        if not sys_key:
            # Also check top-level featType
            sys_key = safe_str(data.get("featType", "")).lower()
        if sys_key:
            TRAIT_FEAT_TYPES = {
                "trait", "social", "regional", "religion",
                "combat", "magic", "racial", "drawback",
            }
            if sys_key in TRAIT_FEAT_TYPES and kategori == "feat":
                kategori = "trait"

        mechanics = extract_standard_mechanics(data, sistem)
        data["standard_mechanics"] = mechanics.get("standard_mechanics", [])
        data["prerequisites"] = mechanics.get("prerequisites", [])

        # Detect parent race and attach as metadata.
        # IMPORTANT: this does NOT change the category — a racial feat/trait
        # stays a 'feat'/'trait'.  Only genuine race entities (type='race') are 'race'.
        parent = detect_parent_race(name, sistem)
        if parent:
            data["parent_race"] = parent
            # Do NOT override kategori here; feats/traits stay feats/traits.

        # ADIM 1: Büyü verilerini izole 'spells' tablosuna yaz
        if kategori == "spell":
            try:
                parser = SpellParser()
                parser.store_single_spell(sistem, data)
            except Exception as exc:
                logger.warning("SpellParser entegrasyon hatası (%s): %s", name, exc)

        return DiyargezenEntity(
            isim=name,
            sistem=sistem,
            kategori=kategori,
            aciklama=extract_description(data),
            sistem_verisi=data,
        )
    except Exception as exc:
        logger.debug("Entity atlandı (%s/%s): %s", kategori, isim, exc)
        return None


def parse_section(
    raw: Any,
    sistem: str,
    kategori: str,
) -> List[DiyargezenEntity]:
    """Dict veya list formatındaki bir bölümü entity listesine çevir."""
    entities: List[DiyargezenEntity] = []

    if isinstance(raw, dict):
        for key, val in raw.items():
            ent = make_entity(safe_str(key), sistem, kategori, val)
            if ent:
                entities.append(ent)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                ent = make_entity(item, sistem, kategori, {"name": item})
            elif isinstance(item, dict):
                name = safe_str(item.get("name") or item.get("id") or item.get("key"))
                ent = make_entity(name, sistem, kategori, item)
            else:
                continue
            if ent:
                entities.append(ent)

    return entities


def parse_sections(
    data: Dict[str, Any],
    sistem: str,
    mapping: Dict[str, str],
) -> List[DiyargezenEntity]:
    """Birden fazla JSON bölümünü tek seferde parse et."""
    out: List[DiyargezenEntity] = []
    for json_key, kategori in mapping.items():
        try:
            section = data.get(json_key)
            if section:
                out.extend(parse_section(section, sistem, kategori))
        except Exception as exc:
            logger.warning("%s → %s parse hatası: %s", sistem, json_key, exc)
    return out


class SpellParser:
    """Spells parser that creates and manages the isolated 'spells' table in the database."""
    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(__file__).resolve().parent.parent / "data" / "characters.db"
        self.init_table()

    def init_table(self) -> None:
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS spells (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                isim          TEXT    NOT NULL,
                sistem        TEXT    NOT NULL,
                seviye        INTEGER NOT NULL DEFAULT 0,
                siniflar      TEXT    NOT NULL, -- comma-separated list of playable classes
                aciklama      TEXT    DEFAULT '',
                UNIQUE(sistem, isim)
            )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_spells_system_name ON spells(sistem, isim)")
            conn.commit()
        except Exception as e:
            logger.warning("Spells tablosu oluşturma hatası: %s", e)
        finally:
            conn.close()

    def _load_dnd_spell_lists(self) -> Dict[str, List[str]]:
        if hasattr(self, "_dnd_spell_lists"):
            return self._dnd_spell_lists
            
        mapping = {}
        try:
            path = Path(__file__).resolve().parent.parent / "data" / "dnd-5e-srd-master" / "dnd-5e-srd-master" / "json" / "08 spellcasting.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                lists = data.get("Spellcasting", {}).get("Spell Lists", {})
                for class_spell_key, levels_dict in lists.items():
                    class_name = class_spell_key.replace(" Spells", "").strip().title()
                    if isinstance(levels_dict, dict):
                        for lvl_key, spells_list in levels_dict.items():
                            if isinstance(spells_list, list):
                                for spell_name in spells_list:
                                    name_clean = str(spell_name).strip()
                                    mapping.setdefault(name_clean.lower(), []).append(class_name)
        except Exception as e:
            logger.debug("D&D spell lists loading error: %s", e)
            
        self._dnd_spell_lists = mapping
        return mapping

    def store_single_spell(self, system: str, raw_data: Dict[str, Any]) -> None:
        import sqlite3
        
        name = raw_data.get("name") or raw_data.get("isim")
        if not name:
            return
            
        system_normalized = system.lower().replace("_", "").replace("-", "")
        level = self.get_spell_level(raw_data)
        classes_str = ",".join(self.get_spell_classes(raw_data, name))
        description = extract_description(raw_data)
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
            INSERT OR REPLACE INTO spells (isim, sistem, seviye, siniflar, aciklama)
            VALUES (?, ?, ?, ?, ?)
            """, (name, system_normalized, level, classes_str, description))
            conn.commit()
        except Exception as e:
            logger.warning("Büyü veritabanına yazılırken hata oluştu (%s): %s", name, e)
        finally:
            conn.close()

    def get_spell_level(self, raw: dict) -> int:
        for parent_key in (None, "system", "data", "sistem_verisi"):
            if parent_key is None:
                target = raw
            else:
                target = raw.get(parent_key)
            if isinstance(target, dict):
                level = target.get("level")
                if level is not None:
                    try:
                        return int(level)
                    except (ValueError, TypeError):
                        pass
                content = target.get("content")
                if isinstance(content, list) and content:
                    import re
                    first_line = str(content[0])
                    match_lvl = re.search(r'(\d+)(?:st|nd|rd|th)-level', first_line, re.IGNORECASE)
                    if match_lvl:
                        return int(match_lvl.group(1))
                    elif "cantrip" in first_line.lower():
                        return 0
        return 0

    def get_spell_classes(self, raw: dict, name: str) -> List[str]:
        CLASS_MAP = {
            "wiz": "Wizard",
            "clr": "Cleric",
            "dru": "Druid",
            "sor": "Sorcerer",
            "pal": "Paladin",
            "brd": "Bard",
            "rng": "Ranger",
            "alc": "Alchemist",
            "bar": "Barbarian",
            "rog": "Rogue",
            "ftr": "Fighter",
            "mon": "Monk",
            "oracle": "Oracle",
            "witch": "Witch",
            "inquisitor": "Inquisitor",
            "summoner": "Summoner",
            "magus": "Magus"
        }
        
        classes = []
        # Check DND 5e pre-built spell lists mapping
        dnd_lists = self._load_dnd_spell_lists()
        if name.lower() in dnd_lists:
            classes.extend(dnd_lists[name.lower()])

        for parent_key in (None, "system", "data", "sistem_verisi"):
            if parent_key is None:
                target = raw
            else:
                target = raw.get(parent_key)
            if isinstance(target, dict):
                levels_by_class = target.get("levels_by_class")
                if isinstance(levels_by_class, dict):
                    for k in levels_by_class.keys():
                        name_norm = k.strip().lower()
                        mapped = CLASS_MAP.get(name_norm, name_norm.title())
                        classes.append(mapped)

                for key in ("classes", "spellClasses", "spell_class", "levels"):
                    val = target.get(key)
                    if isinstance(val, list):
                        for item in val:
                            if isinstance(item, str) and item.strip():
                                name_norm = item.strip().lower()
                                mapped = CLASS_MAP.get(name_norm, name_norm.title())
                                classes.append(mapped)
                            elif isinstance(item, dict):
                                n = item.get("name") or item.get("isim")
                                if n:
                                    name_norm = str(n).strip().lower()
                                    mapped = CLASS_MAP.get(name_norm, name_norm.title())
                                    classes.append(mapped)
                    elif isinstance(val, dict):
                        for k, v in val.items():
                            if v:
                                name_norm = k.strip().lower()
                                mapped = CLASS_MAP.get(name_norm, name_norm.title())
                                classes.append(mapped)
                    elif isinstance(val, str):
                        for item in val.split(","):
                            if item.strip():
                                name_norm = item.strip().lower()
                                mapped = CLASS_MAP.get(name_norm, name_norm.title())
                                classes.append(mapped)
        return sorted(list(set(classes)))

