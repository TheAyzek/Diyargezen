"""
Diyargezen Pathfinder 1st Edition (PF1e) Stat Calculation Engine

Architecture & Algorithmic Design:
----------------------------------
This module serves as the primary stateless mathematical engine for Pathfinder 1e character sheets.
It processes raw character data (Abilities, Classes, Feats, Traits, Items, Custom GM Modifiers)
and computes full character stats in real time.

Algorithmic Pipeline:
1. Ability Score Pipeline: Calculates base scores + racial bonuses + level-up increments + item/buff bonuses.
2. Ability Modifiers: Standard PF1e formula `floor((score - 10) / 2)`.
3. Combat Metrics (BAB & Iterative Attacks):
   - Fast progression (Full BAB: Level * 1.0 e.g. Fighter)
   - Medium progression (3/4 BAB: floor(Level * 0.75) e.g. Rogue/Cleric)
   - Slow progression (1/2 BAB: floor(Level * 0.50) e.g. Wizard)
   - Multi-attack iterations generated at BAB >= 6 (+6/+1, +11/+6/+1, +16/+11/+6/+1).
4. Save Matrices (Fortitude, Reflex, Will):
   - Good progression: 2 + floor(Level / 2)
   - Poor progression: floor(Level / 3)
5. Armor Class (AC) & Touch/Flat-Footed AC:
   - AC = 10 + Armor + Shield + Dex Mod + Size Mod + Dodge + Natural + Deflection + GM Custom Modifiers.
6. Encumbrance & Weight Accumulation:
   - Aggregates item weight * quantity against Strength-based Carrying Capacity thresholds (Light, Medium, Heavy).
7. Soft-Block Override Support:
   - Integrates `is_overridden` flags and custom (+X/-X) manual GM stat overrides without breaking pipeline calculation.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)

_GLOBAL_ENTITY_CACHE: Dict[tuple, tuple] = {}

def extract_weight_and_qty(item: Dict[str, Any]) -> tuple[float, int]:
    # Quantity extraction
    qty = item.get("quantity")
    if qty is None:
        sv = item.get("sistem_verisi") or item.get("system_data") or {}
        if isinstance(sv, dict):
            qty = sv.get("quantity")
            if qty is None:
                qty = sv.get("system", {}).get("quantity") if isinstance(sv.get("system"), dict) else None
    try:
        qty = int(qty) if qty is not None else 1
    except:
        qty = 1

    # Weight extraction
    weight_val = item.get("weight") or item.get("agirlik")
    if weight_val is None:
        sv = item.get("sistem_verisi") or item.get("system_data") or {}
        if isinstance(sv, dict):
            w_obj = sv.get("weight") or sv.get("agirlik")
            if w_obj is None:
                w_obj = sv.get("system", {}).get("weight") if isinstance(sv.get("system"), dict) else None
            
            if isinstance(w_obj, dict):
                weight_val = w_obj.get("value", 0.0)
            elif isinstance(w_obj, (int, float, str)):
                weight_val = w_obj

    try:
        weight_val = float(weight_val) if weight_val is not None else 0.0
    except (ValueError, TypeError):
        weight_val = 0.0
        
    return weight_val, qty

def is_item_magical(item: Dict[str, Any]) -> bool:
    if not isinstance(item, dict):
        return False
    if item.get("is_magical") or item.get("magical"):
        return True
    if item.get("rarity") in ("magic", "magical"):
        return True
    sv = item.get("sistem_verisi") or item.get("system_data") or {}
    if isinstance(sv, dict):
        if sv.get("is_magical") or sv.get("magical"):
            return True
        if sv.get("rarity") in ("magic", "magical"):
            return True
        if int(sv.get("enhancement") or 0) > 0:
            return True
    kat = str(item.get("kategori") or "").lower()
    if "magic" in kat or "büyülü" in kat or "buyulu" in kat:
        return True
    name = str(item.get("name") or item.get("isim") or "").lower()
    if re.search(r"(\+\d+|büyülü|buyulu|magic|magical|flaming|keen|frost|shock|holy|unholy|bane|vorpal|defending|fortification|speed|ghost touch|wounding|enhancement|adamantine|mithral)", name):
        return True
    return False

def categorize_items(equipment_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    categories = {
        "weapons": [],
        "weapons_normal": [],
        "weapons_magic": [],
        "armor_shields": [],
        "armor_normal": [],
        "armor_magic": [],
        "consumables": [],
        "gear": []
    }
    for item in equipment_list:
        if not isinstance(item, dict):
            continue
        sv = item.get("sistem_verisi") or item.get("system_data") or {}
        if not isinstance(sv, dict):
            sv = {}
        sys_obj = sv.get("system", {}) if isinstance(sv.get("system"), dict) else {}
        
        name_lower = str(item.get("name") or item.get("isim") or "").lower()
        itype = str(item.get("type", item.get("kategori", sv.get("type", sv.get("category", sys_obj.get("type", ""))))))
        ikategori = str(item.get("kategori", item.get("category", sv.get("kategori", sv.get("category", ""))))).lower()

        is_armor_or_shield = (
            itype in ("armor", "shield") or 
            any(k in ikategori for k in ("armor", "shield", "zırh", "zirh", "kalkan")) or
            any(w in name_lower for w in ("armor", "armour", "shield", "buckler", "chainmail", "leather", "plate", "breastplate", "zırh", "zirh", "kalkan", "deri", "plaka", "zincir", "pullu", "halka", "göğüslük", "gogusluk", "çivili", "civili", "kapitone"))
        )

        is_weapon = not is_armor_or_shield and (
            itype in ("weapon", "weapons") or 
            any(k in ikategori for k in ("weapon", "silah")) or
            any(w in name_lower for w in ("sword", "dagger", "mace", "bow", "hammer", "axe", "spear", "lance", "flail", "rapier", "scimitar", "musket", "pistol", "rifle", "silah", "kılıç", "kilic", "hançer", "hancer", "mızrak", "mizrak", "balta", "gürz", "gurz", "yay", "arbalet", "tüfek", "tufek"))
        )

        is_consumable = (
            itype in ("consumable", "potion", "scroll", "wand") or
            any(k in ikategori for k in ("potion", "scroll", "wand", "iksir", "parşömen", "parsomen", "asa")) or
            any(w in name_lower for w in ("potion", "scroll", "wand", "elixir", "oil", "iksir", "parşömen", "parsomen", "asa", "yağ", "yag"))
        )

        magical = is_item_magical(item)

        if is_weapon:
            categories["weapons"].append(item)
            if magical:
                categories["weapons_magic"].append(item)
            else:
                categories["weapons_normal"].append(item)
        elif is_armor_or_shield:
            categories["armor_shields"].append(item)
            if magical:
                categories["armor_magic"].append(item)
            else:
                categories["armor_normal"].append(item)
        elif is_consumable:
            categories["consumables"].append(item)
        else:
            categories["gear"].append(item)
            
    return categories

HEAVY_MAX_TABLE: Dict[int, int] = {
    1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60, 7: 70, 8: 80, 9: 90, 10: 100,
    11: 115, 12: 130, 13: 150, 14: 175, 15: 200, 16: 230, 17: 260, 18: 300, 19: 350, 20: 400
}

def calculate_carrying_capacity(strength_score: int, size: str = "Medium") -> Dict[str, float]:
    """Calculate Pathfinder 1e carrying capacity thresholds (Light, Medium, Heavy Max) in lbs.
    
    Academic Architecture:
    ----------------------
    Reference: PF1e Core Rulebook, Chapter 7 (Carrying Capacity).
    Calculates capacity limits based on Strength score and creature Size category.
    For Strength > 20, Heavy Max doubles for every +5 Strength (+10 multiplies by 4).
    """
    str_val = max(1, int(strength_score or 10))
    if str_val <= 20:
        heavy_max = float(HEAVY_MAX_TABLE.get(str_val, 100))
    else:
        remainder = (str_val - 10) % 10 + 10
        multiplier_pow = (str_val - 10) // 10
        base_heavy = HEAVY_MAX_TABLE.get(remainder, 400)
        heavy_max = float(base_heavy * (4 ** multiplier_pow))

    size_norm = str(size or "Medium").capitalize()
    size_mult = {
        "Fine": 0.125, "Diminutive": 0.25, "Tiny": 0.5, "Small": 0.75,
        "Medium": 1.0, "Large": 2.0, "Huge": 4.0, "Gargantuan": 8.0, "Colossal": 16.0
    }.get(size_norm, 1.0)

    heavy_max = float(heavy_max * size_mult)
    light_max = round(heavy_max / 3.0, 1)
    medium_max = round((heavy_max * 2.0) / 3.0, 1)
    heavy_max = round(heavy_max, 1)

    return {
        "light_max": light_max,
        "medium_max": medium_max,
        "heavy_max": heavy_max
    }

def calculate_encumbrance_status(total_weight: float, capacity: Dict[str, float]) -> Dict[str, Any]:
    """Determine Pathfinder 1e encumbrance load status and stat penalties."""
    wt = max(0.0, float(total_weight or 0.0))
    light = capacity.get("light_max", 33.0)
    medium = capacity.get("medium_max", 66.0)
    heavy = capacity.get("heavy_max", 100.0)

    if wt <= light:
        status = "Light Load"
        max_dex = None
        acp_penalty = 0
        speed_penalty = 0
    elif wt <= medium:
        status = "Medium Load"
        max_dex = 3
        acp_penalty = -3
        speed_penalty = -10
    elif wt <= heavy:
        status = "Heavy Load"
        max_dex = 1
        acp_penalty = -6
        speed_penalty = -10
    else:
        status = "Overloaded"
        max_dex = 0
        acp_penalty = -10
        speed_penalty = -20

    return {
        "status": status,
        "total_weight": round(wt, 1),
        "max_dex_bonus": max_dex,
        "encumbrance_acp": acp_penalty,
        "speed_penalty": speed_penalty,
        "carrying_capacity": capacity
    }


def _extract_mechanics_from_payload(sys_ver: Dict[str, Any]) -> List[Dict[str, Any]]:
    mechs = list(sys_ver.get("standard_mechanics", []))
    bonuses = sys_ver.get("bonuses", [])
    if isinstance(bonuses, list):
        for b in bonuses:
            if not isinstance(b, dict):
                continue
            b_type = b.get("type")
            val = b.get("value", 0)
            try:
                val = int(val)
            except (ValueError, TypeError):
                val = 0

            if b_type == "initiative":
                mechs.append({"target": "initiative", "value": val})
            elif b_type == "save_fortitude":
                mechs.append({"target": "saving_throws.Fortitude", "value": val})
            elif b_type == "save_reflex":
                mechs.append({"target": "saving_throws.Reflex", "value": val})
            elif b_type == "save_will":
                mechs.append({"target": "saving_throws.Will", "value": val})
            elif b_type == "save_all":
                mechs.append({"target": "saving_throws.All", "value": val})
            elif b_type == "skill":
                sk = b.get("skill")
                if sk:
                    m = {"target": f"skills.{sk}", "value": val}
                    if b.get("makes_class_skill"):
                        m["makes_class_skill"] = True
                        m["skill_name"] = sk
                    mechs.append(m)
            elif b_type == "armor_check_penalty":
                mechs.append({"target": "armor_check_penalty", "value": val})
            elif b_type in ("armor_class", "ac"):
                mechs.append({"target": "ac", "value": val})
            elif b_type == "hp":
                mechs.append({"target": "hp", "value": val})
            elif b_type == "bab":
                mechs.append({"target": "bab", "value": val})
    return mechs

class BaseCalculator(ABC):
    """Base class for TTRPG derived statistics calculators."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).resolve().parent.parent / "data" / "characters.db"

    @abstractmethod
    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates and returns all derived statistics for the system."""
        pass

    def get_active_mechanics(self, character: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Query SQLite for active entities (Race, Class, Feats, Equipment, Traits)
        and fetch their 'standard_mechanics', 'bonuses', 'prerequisites', or parse descriptions.
        Checks in-memory entity dicts first.
        """
        import sqlite3
        import json
        from rules.rule_parser import RuleParser
        
        sys_key = character.get("system", "").lower().replace("_", "").replace("-", "")
        if "pf" in sys_key or "pathfinder" in sys_key:
            sys_db = "pathfinder1e"
        elif "mm" in sys_key:
            sys_db = "mm3e"
        else:
            sys_db = "dnd5e"

        active_mechanics = []
        active_prerequisites = []
        applied_modifiers = []
        
        # Helper to process in-memory dictionaries
        def process_entity(name: str, data: Any, category: str):
            if not isinstance(data, dict):
                return False
            
            desc = data.get("aciklama") or data.get("description") or ""
            sys_ver = data.get("sistem_verisi") or data.get("system") or data.get("data") or {}
            if not isinstance(sys_ver, dict):
                sys_ver = {}
                
            active_prerequisites.extend(sys_ver.get("prerequisites", []))
            
            explicit_mechs = _extract_mechanics_from_payload(sys_ver)
            explicit_targets = set()
            for m in explicit_mechs:
                m_copy = m.copy()
                m_copy["source"] = name
                m_copy["type"] = category
                active_mechanics.append(m_copy)
                
                val = m.get("value", 0)
                try:
                    val = int(str(val).replace("+", ""))
                except:
                    val = 0
                applied_modifiers.append({
                    "target": m.get("target", ""),
                    "value": val,
                    "type": category,
                    "source": name,
                    "description": m.get("description") or f"+{val} bonus ({name})"
                })
                explicit_targets.add(m.get("target", ""))

            # Process ability score increases (e.g. for races)
            asi = sys_ver.get("ability_score_increase") or sys_ver.get("modifiers")
            if isinstance(asi, dict):
                for ab_name, b_val in asi.items():
                    try:
                        val_int = int(b_val)
                        if val_int != 0:
                            applied_modifiers.append({
                                "target": f"abilities.{ab_name.title()}",
                                "value": val_int,
                                "type": category,
                                "source": name,
                                "description": f"+{val_int} {ab_name.title()} ({name})"
                            })
                    except (ValueError, TypeError):
                        pass
            
            # Dynamic parsing for missing targets (skip for equipment to avoid parsing armor stats as stat modifiers)
            parsed = RuleParser.parse_description(desc, sys_db, name, category) if category != "equipment" else []
            for p in parsed:
                if p["target"] not in explicit_targets:
                    active_mechanics.append(p)
                    applied_modifiers.append(p)

            # If payload was a stub without description or mechanics, return False
            # so names_to_query will fetch the full entity from SQLite DB.
            if not explicit_mechs and not parsed and len(desc) < 15:
                return False

            return True

        names_to_query = []
        
        # 1. Race
        race = character.get("race")
        race_data = character.get("race_data")
        if not process_entity(race, race_data, "race") and isinstance(race, str) and race:
            names_to_query.append((race, "race"))
            
        # 2. Class
        cls = character.get("class")
        class_data = character.get("class_data")
        if not process_entity(cls, class_data, "class") and isinstance(cls, str) and cls:
            names_to_query.append((cls, "class"))
            
        # 3. Feats
        raw_feats = character.get("feats", [])
        if isinstance(raw_feats, list):
            for f in raw_feats:
                if isinstance(f, dict):
                    f_name = f.get("name") or f.get("isim")
                    if not process_entity(f_name, f, "feat") and f_name:
                        names_to_query.append((f_name, "feat"))
                elif isinstance(f, str) and f:
                    names_to_query.append((f, "feat"))
                    
        # 4. Equipment
        raw_items = character.get("equipment", [])
        if isinstance(raw_items, list):
            for item in raw_items:
                if isinstance(item, dict):
                    i_name = item.get("name") or item.get("isim")
                    if not process_entity(i_name, item, "equipment") and i_name:
                        names_to_query.append((i_name, "equipment"))
                elif isinstance(item, str) and item:
                    names_to_query.append((item, "equipment"))

        # 5. Traits
        raw_traits = character.get("traits", [])
        if isinstance(raw_traits, list):
            for t in raw_traits:
                if isinstance(t, dict):
                    t_name = t.get("name") or t.get("isim")
                    if not process_entity(t_name, t, "trait") and t_name:
                        names_to_query.append((t_name, "trait"))
                elif isinstance(t, str) and t:
                    names_to_query.append((t, "trait"))

        # Query database for entities without in-memory detailed data (with global in-memory cache)
        db_key = str(self.db_path)
        uncached_names = [n for n in names_to_query if (db_key, sys_db, n[0]) not in _GLOBAL_ENTITY_CACHE]

        if uncached_names:
            try:
                conn = sqlite3.connect(db_key)
                cursor = conn.cursor()
                
                placeholders = ",".join("?" for _ in uncached_names)
                query_names = [n[0] for n in uncached_names]
                cursor.execute(
                    f"SELECT isim, aciklama, sistem_verisi FROM entities WHERE sistem = ? AND isim IN ({placeholders})",
                    [sys_db] + query_names
                )
                
                rows = cursor.fetchall()
                for row in rows:
                    name_key = row[0]
                    desc_val = row[1] or ""
                    payload_val = json.loads(row[2]) if row[2] else {}
                    _GLOBAL_ENTITY_CACHE[(db_key, sys_db, name_key)] = (desc_val, payload_val)
                conn.close()
            except Exception as e:
                logger.warning(f"Error querying entities for mechanics: {e}")

        for name, category in names_to_query:
            if (db_key, sys_db, name) in _GLOBAL_ENTITY_CACHE:
                desc, payload = _GLOBAL_ENTITY_CACHE[(db_key, sys_db, name)]
                
                active_prerequisites.extend(payload.get("prerequisites", []))
                
                explicit_mechs = _extract_mechanics_from_payload(payload)
                explicit_targets = set()
                for m in explicit_mechs:
                    m_copy = m.copy()
                    m_copy["source"] = name
                    m_copy["type"] = category
                    active_mechanics.append(m_copy)
                    
                    val = m.get("value", 0)
                    try: val = int(str(val).replace("+", ""))
                    except: val = 0
                    applied_modifiers.append({
                        "target": m.get("target", ""),
                        "value": val,
                        "type": category,
                        "source": name,
                        "description": m.get("description") or f"+{val} bonus ({name})"
                    })
                    explicit_targets.add(m.get("target", ""))
                
                parsed = RuleParser.parse_description(desc, sys_db, name, category) if category != "equipment" else []
                for p in parsed:
                    if p["target"] not in explicit_targets:
                        active_mechanics.append(p)
                        applied_modifiers.append(p)
                pass
                
        return {
            "mechanics": active_mechanics,
            "prerequisites": active_prerequisites,
            "applied_modifiers": applied_modifiers
        }

    def get_adjusted_abilities(self, character: Dict[str, Any]) -> Dict[str, int]:
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
                     "stamina", "agility", "fighting", "intellect", "awareness", "presence"]
        scores = {}
        is_mm = "mm" in character.get("system", "").lower()
        default_val = 0 if is_mm else 10
        for ab in abilities:
            scores[ab] = get_ability(character, ab, default=default_val)

        # ---------------------------------------------------------------------------
        # RACIAL ABILITY SCORE INCREASES
        # Apply parent race ASI first, then subrace ASI on top.
        # For D&D 5e subraces: their stored ability_score_increase ALREADY INCLUDES
        # the parent bonus (e.g., Wood Elf stores dex+2 AND wis+1). We subtract the
        # parent's contribution to get only the true subrace delta, avoiding double-
        # counting.
        # ---------------------------------------------------------------------------
        sys_key = character.get("system", "").lower().replace("_", "").replace("-", "")
        is_dnd5e = "dnd" in sys_key

        # Determine whether we have a subrace selected
        subrace_data: Dict = character.get("subrace_data") or {}
        has_subrace = bool(character.get("subrace", ""))

        # PF1e Core & Standard Races built-in ASI map fallback
        PF1E_RACE_ASI = {
            "dwarf": {"constitution": 2, "wisdom": 2, "charisma": -2},
            "elf": {"dexterity": 2, "intelligence": 2, "constitution": -2},
            "gnome": {"constitution": 2, "charisma": 2, "strength": -2},
            "half-elf": {"strength": 2},
            "halfling": {"dexterity": 2, "charisma": 2, "strength": -2},
            "half-orc": {"strength": 2},
            "human": {"strength": 2},
            "primitive human": {"strength": 2},
            "aasimar": {"wisdom": 2, "charisma": 2},
            "adaro": {"dexterity": 2, "constitution": 2, "intelligence": -2},
            "android": {"dexterity": 2, "intelligence": 2, "charisma": -2},
            "aphorite": {"strength": 2, "wisdom": 2, "charisma": -2},
            "aquatic elf": {"dexterity": 2, "intelligence": 2, "constitution": -2},
            "astomoi": {"intelligence": 2, "wisdom": 2, "constitution": -2},
            "being of ib": {"wisdom": 2, "charisma": -2},
            "boggard": {"constitution": 2, "wisdom": 2, "charisma": -2},
            "caligni": {"dexterity": 2, "constitution": 2, "intelligence": -2},
            "catfolk": {"dexterity": 2, "charisma": 2, "wisdom": -2},
            "cecaelia": {"dexterity": 2, "wisdom": 2, "constitution": -2},
            "changeling": {"wisdom": 2, "charisma": 2, "constitution": -2},
            "deep one hybrid": {"constitution": 2, "wisdom": 2, "dexterity": -2},
            "dhampir": {"dexterity": 2, "charisma": 2, "constitution": -2},
            "drow": {"dexterity": 2, "charisma": 2, "constitution": -2},
            "drow noble": {"dexterity": 4, "intelligence": 2, "wisdom": 2, "charisma": 2, "constitution": -2},
            "duergar": {"constitution": 2, "wisdom": 2, "charisma": -4},
            "duskwalker": {"dexterity": 2, "wisdom": 2, "constitution": -2},
            "fetchling": {"dexterity": 2, "charisma": 2, "wisdom": -2},
            "ganzi": {"constitution": 2, "charisma": 2, "intelligence": -2},
            "gathlain": {"dexterity": 2, "charisma": 2, "constitution": -2},
            "ghoran": {"constitution": 2, "charisma": 2, "intelligence": -2},
            "gillman": {"constitution": 2, "charisma": 2, "wisdom": -2},
            "goblin": {"dexterity": 4, "strength": -2, "charisma": -2},
            "green martian": {"strength": 2, "wisdom": 2, "charisma": -2},
            "grindylow": {"dexterity": 4, "strength": -2, "wisdom": -2},
            "grippli": {"dexterity": 2, "wisdom": 2, "strength": -2},
            "hobgoblin": {"dexterity": 2, "constitution": 2},
            "ifrit": {"dexterity": 2, "charisma": 2, "wisdom": -2},
            "kasatha": {"dexterity": 2, "wisdom": 2},
            "kitsune": {"dexterity": 2, "charisma": 2, "strength": -2},
            "kobold": {"dexterity": 2, "strength": -4, "constitution": -2},
            "kuru": {"dexterity": 2, "constitution": 2, "intelligence": -2},
            "lashunta": {"intelligence": 2, "charisma": 2, "constitution": -2},
            "locathah": {"dexterity": 2, "wisdom": 2, "strength": -2},
            "merfolk": {"dexterity": 2, "constitution": 2, "charisma": 2},
            "monkey goblin": {"dexterity": 4, "wisdom": -2, "charisma": -2},
            "munavri": {"dexterity": 2, "intelligence": 2, "charisma": 2, "strength": -2},
            "nagaji": {"strength": 2, "charisma": 2, "intelligence": -2},
            "naiad": {"dexterity": 2, "charisma": 2, "strength": -2},
            "orang-pendak": {"strength": 2, "wisdom": 2, "intelligence": -2},
            "orc": {"strength": 4, "intelligence": -2, "wisdom": -2, "charisma": -2},
            "oread": {"strength": 2, "wisdom": 2, "charisma": -2},
            "ratfolk": {"dexterity": 2, "intelligence": 2, "strength": -2},
            "reborn samsaran": {"intelligence": 2, "wisdom": 2, "constitution": -2},
            "reptoid": {"strength": 2, "charisma": 2, "intelligence": -2},
            "rougarou": {"strength": 2, "wisdom": 2, "intelligence": -2},
            "sahuagin": {"strength": 2, "wisdom": 2, "charisma": -2},
            "samsaran": {"intelligence": 2, "wisdom": 2, "constitution": -2},
            "shabti": {"constitution": 2, "charisma": 2},
            "skinwalker": {"wisdom": 2, "intelligence": -2},
            "strix": {"dexterity": 2, "charisma": -2},
            "suli": {"strength": 2, "charisma": 2, "intelligence": -2},
            "svirfneblin": {"dexterity": 2, "wisdom": 2, "strength": -2, "charisma": -4},
            "sylph": {"dexterity": 2, "intelligence": 2, "constitution": -2},
            "syrinx": {"wisdom": 2, "dexterity": -2},
            "tengu": {"dexterity": 2, "wisdom": 2, "constitution": -2},
            "tiefling": {"dexterity": 2, "intelligence": 2, "charisma": -2},
            "triaxian": {"constitution": 2, "wisdom": 2, "strength": -2},
            "triton": {"strength": 2, "charisma": 2, "intelligence": -2},
            "trox": {"strength": 6, "dexterity": -2, "intelligence": -2, "wisdom": -2, "charisma": -2},
            "undine": {"dexterity": 2, "wisdom": 2, "charisma": -2},
            "vanara": {"dexterity": 2, "wisdom": 2, "charisma": -2},
            "vine leshy": {"constitution": 2, "wisdom": 2, "intelligence": -2},
            "vishkanya": {"dexterity": 2, "charisma": 2, "wisdom": -2},
            "wayang": {"dexterity": 2, "intelligence": 2, "wisdom": -2},
            "wyrwood": {"dexterity": 2, "intelligence": 2, "constitution": -2},
            "wyvaran": {"dexterity": 2, "wisdom": 2, "intelligence": -2},
            "yaddithian": {"constitution": 2, "intelligence": 2, "wisdom": -2}
        }

        # Helper: extract ASI dict from a data dict (entity.sistem_verisi or similar)
        def extract_asi(data: Any, race_name: str = "") -> Dict[str, int]:
            r_raw = (race_name or (data.get("name") if isinstance(data, dict) else "") or (data.get("isim") if isinstance(data, dict) else "")).lower().strip()
            
            TURKISH_RACE_MAP = {
                "insan": "human", "i̇nsan": "human", "human": "human",
                "yarım-elf": "half-elf", "yarim-elf": "half-elf", "yarım elf": "half-elf", "yarim elf": "half-elf", "half-elf": "half-elf",
                "yarım-ork": "half-orc", "yarim-ork": "half-orc", "yarım ork": "half-orc", "yarim ork": "half-orc", "half-orc": "half-orc",
                "cüce": "dwarf", "cuce": "dwarf", "dwarf": "dwarf",
                "elf": "elf", "gnom": "gnome", "gnome": "gnome",
                "buçukluk": "halfling", "bucukluk": "halfling", "halfling": "halfling",
                "ork": "orc", "orc": "orc", "goblin": "goblin"
            }
            r_name = TURKISH_RACE_MAP.get(r_raw, r_raw)

            # Check for Human / Half-Elf / Half-Orc user-selected stat choice
            user_choice = character.get("racial_ability_choice", "").lower().strip()
            sec_choice = character.get("secondary_racial_ability_choice", "").lower().strip()
            sel_traits = character.get("selected_racial_traits") or []
            has_dual = any("dual talent" in str(t).lower() for t in sel_traits)

            if r_name in ("human", "half-elf", "half-orc"):
                choice_stat = user_choice or "strength"
                res = {choice_stat: 2}
                if has_dual and sec_choice and sec_choice != choice_stat:
                    res[sec_choice] = 2
                return res

            # Check built-in PF1e core race table first
            if r_name in PF1E_RACE_ASI:
                return PF1E_RACE_ASI[r_name].copy()

            if not isinstance(data, dict):
                return {}

            sv = data.get("sistem_verisi") or data.get("system") or data.get("system_data") or data
            if not isinstance(sv, dict):
                sv = data

            raw = sv.get("ability_score_increase") or sv.get("modifiers") or data.get("ability_score_increase") or data.get("modifiers") or {}
            if isinstance(raw, dict):
                result = {}
                for k, v in raw.items():
                    try:
                        result[k.lower()] = int(v)
                    except (ValueError, TypeError):
                        pass
                if result:
                    return result

            return {}

        # --- Parent race ASI ---
        parent_asi: Dict[str, int] = {}
        race_name = character.get("race", "")
        race_entity = self._get_entity_data(character, "race")
        parent_asi = extract_asi(race_entity, race_name=race_name)


        # If subrace is selected and system is D&D 5e, the subrace entity stores
        # the COMBINED ASI (parent + subrace bonus). Compute net subrace delta.
        if has_subrace and subrace_data:
            subrace_asi = extract_asi(subrace_data)
            if is_dnd5e:
                # subrace_asi may include parent race contributions – subtract them
                net_subrace_delta: Dict[str, int] = {}
                all_keys = set(list(parent_asi.keys()) + list(subrace_asi.keys()))
                for k in all_keys:
                    delta = subrace_asi.get(k, 0) - parent_asi.get(k, 0)
                    if delta != 0:
                        net_subrace_delta[k] = delta
                # Apply parent race ASI + net subrace delta
                for k, v in parent_asi.items():
                    if k in scores:
                        scores[k] += v
                for k, v in net_subrace_delta.items():
                    if k in scores:
                        scores[k] += v
            else:
                # PF1e heritages: apply parent ASI and then the subrace ASI directly on top
                for k, v in parent_asi.items():
                    if k in scores:
                        scores[k] += v
                for k, v in subrace_asi.items():
                    if k in scores:
                        scores[k] += v
        else:
            # No subrace – just apply parent race ASI
            for k, v in parent_asi.items():
                if k in scores:
                    scores[k] += v

        # --- Standard mechanics (feat / item modifiers, NON-ability-score targets) ---
        # NOTE: Ability score bonuses are handled above via ability_score_increase.
        # We skip mechanics targeting base ability score names here to prevent
        # double-counting (race entities store BOTH ability_score_increase AND
        # a matching standard_mechanics entry with the same value).
        ABILITY_SCORE_NAMES = {
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
            "stamina", "agility", "fighting", "intellect", "awareness", "presence"
        }
        active = self.get_active_mechanics(character)
        for m in active["mechanics"]:
            target = m.get("target", "").lower()
            if target in ABILITY_SCORE_NAMES or target.replace("abilities.", "") in ABILITY_SCORE_NAMES:
                clean_target = target.replace("abilities.", "")
                # Skip race ASI to avoid double counting with extract_asi
                if m.get("type") == "race":
                    continue
                if clean_target in scores:
                    val = m.get("value", 0)
                    try:
                        val_int = int(val)
                        scores[clean_target] += val_int
                    except (ValueError, TypeError):
                        pass
            elif target in scores:
                val = m.get("value", 0)
                if isinstance(val, int):
                    scores[target] += val
        return scores

    def _get_entity_data(self, character: Dict[str, Any], field: str) -> Optional[Dict[str, Any]]:
        """Helper: return the sistem_verisi dict for 'race' or 'class' entity
        stored inside the active character, querying the DB if necessary."""
        import sqlite3 as _sqlite3
        import json as _json

        data = character.get(f"{field}_data")
        if isinstance(data, dict) and data:
            return data

        name = character.get(field, "")
        if not name:
            return None

        sys_key = character.get("system", "").lower().replace("_", "").replace("-", "")
        if "pf" in sys_key or "pathfinder" in sys_key:
            sys_db = "pathfinder1e"
        elif "mm" in sys_key:
            sys_db = "mm3e"
        else:
            sys_db = "dnd5e"

        try:
            conn = _sqlite3.connect(str(self.db_path))
            row = conn.execute(
                "SELECT sistem_verisi FROM entities WHERE sistem = ? AND isim = ? LIMIT 1",
                (sys_db, name)
            ).fetchone()
            conn.close()
            if row and row[0]:
                return _json.loads(row[0])
        except Exception:
            pass
        return None



def get_ability(char: dict, name: str, default: int = 10) -> int:
    abilities = char.get("abilities") or char.get("ability_scores") or {}
    for k, v in abilities.items():
        if k.lower() == name.lower():
            try:
                return int(v)
            except:
                pass
    return default


def get_modifier(char: dict, name: str, default: int = 0) -> int:
    modifiers = char.get("modifiers", {})
    for k, v in modifiers.items():
        if k.lower() == name.lower():
            try:
                return int(v)
            except:
                pass
    score = get_ability(char, name, default=10)
    return (score - 10) // 2


def format_mod(val: int) -> str:
    return f"{val:+d}" if val >= 0 else f"{val:d}"


class DND5e_Calculator(BaseCalculator):
    """Calculations engine for D&D 5th Edition."""

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        derived = {}
        level = int(character.get("level", 1))

        # Modifiers
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        derived["ability_scores"] = {ab.title(): scores.get(ab, 10) for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): m for ab, m in mods.items()}

        # Proficiency
        prof = 2 + (level - 1) // 4
        derived["proficiency_bonus"] = prof

        # HP
        raw_hd = str(character.get("class_data", {}).get("hit_die", "8")).lower()
        try:
            hit_die = int(raw_hd.split('d')[-1])
        except ValueError:
            hit_die = 8
        con_mod = mods["constitution"]
        hp = hit_die + con_mod + (level - 1) * (hit_die // 2 + 1 + con_mod)
        derived["hit_points"] = max(1, hp)

        # Initiative
        derived["initiative"] = mods["dexterity"]

        # AC
        derived["armor_class"] = 10 + mods["dexterity"]

        # Saving Throws
        proficient_saves = character.get("class_data", {}).get("saving_throws", [])
        saving_throws = {}
        for ab in abilities:
            is_prof = ab.title() in proficient_saves or ab in proficient_saves
            saving_throws[ab.title()] = mods[ab] + (prof if is_prof else 0)
        derived["saving_throws"] = saving_throws

        # Skills
        skill_map = {
            "Acrobatics": "dexterity", "Animal Handling": "wisdom", "Arcana": "intelligence",
            "Athletics": "strength", "Deception": "charisma", "History": "intelligence",
            "Insight": "wisdom", "Intimidation": "charisma", "Investigation": "intelligence",
            "Medicine": "wisdom", "Nature": "intelligence", "Perception": "wisdom",
            "Performance": "charisma", "Persuasion": "charisma", "Religion": "intelligence",
            "Sleight of Hand": "dexterity", "Stealth": "dexterity", "Survival": "wisdom"
        }
        skills = {}
        proficient_skills = character.get("proficient_skills", [])
        for skill, ab in skill_map.items():
            is_prof = skill in proficient_skills
            skills[skill] = mods[ab] + (prof if is_prof else 0)
        derived["skills"] = skills

        # Spell Save DC & Spellcasting Ability
        class_name = str(character.get("class", "")).lower()
        casting_stat = character.get("class_data", {}).get("spellcasting_ability", "")
        if not casting_stat:
            if any(c in class_name for c in ("wizard", "artificer")):
                casting_stat = "intelligence"
            elif any(c in class_name for c in ("sorcerer", "bard", "warlock", "paladin")):
                casting_stat = "charisma"
            elif any(c in class_name for c in ("cleric", "druid", "ranger")):
                casting_stat = "wisdom"
            else:
                if character.get("class_data", {}).get("spellcasting"):
                    casting_stat = "intelligence"
                else:
                    casting_stat = ""

        if casting_stat:
            derived["spellcasting_ability"] = casting_stat.title()
            casting_mod = mods.get(casting_stat.lower(), 0)
            derived["spell_save_dc"] = 8 + prof + casting_mod
        else:
            derived["spell_save_dc"] = 0

        # Envanter Ağırlık Hesabı
        total_weight = 0.0
        for item in character.get("equipment", []):
            if isinstance(item, dict):
                w_val, qty = extract_weight_and_qty(item)
                total_weight += w_val * qty
        if total_weight == 0.0:
            for cat in ("weapons", "armor_shields", "consumables", "gear"):
                for item in character.get(cat, []):
                    if isinstance(item, dict):
                        w_val, qty = extract_weight_and_qty(item)
                        total_weight += w_val * qty
        derived["total_weight"] = round(total_weight, 2)

        # Categorize equipment lists for display
        categorized = categorize_items(character.get("equipment", []))
        derived["weapons"] = categorized["weapons"]
        derived["armor_shields"] = categorized["armor_shields"]
        derived["consumables"] = categorized["consumables"]
        derived["gear"] = categorized["gear"]
        
        str_score = scores.get("strength", 10)
        carrying_cap = str_score * 15
        enc_limit = str_score * 5
        heavy_enc_limit = str_score * 10
        
        derived["carrying_capacity"] = {
            "light": enc_limit,
            "medium": heavy_enc_limit,
            "heavy": carrying_cap
        }
        
        if total_weight <= enc_limit:
            derived["encumbrance_status"] = "Light"
        elif total_weight <= heavy_enc_limit:
            derived["encumbrance_status"] = "Medium"
        elif total_weight <= carrying_cap:
            derived["encumbrance_status"] = "Heavy"
        else:
            derived["encumbrance_status"] = "Overloaded"

        # DND 5e Büyü Slotları
        spell_slots = {}
        casting_ability = derived.get("spellcasting_ability", "")
        if casting_ability:
            casting_stat = casting_ability.lower()
            
            DND_FULL_CASTER_SLOTS = {
                1: (2, 0, 0, 0, 0, 0, 0, 0, 0), 2: (3, 0, 0, 0, 0, 0, 0, 0, 0),
                3: (4, 2, 0, 0, 0, 0, 0, 0, 0), 4: (4, 3, 0, 0, 0, 0, 0, 0, 0),
                5: (4, 3, 2, 0, 0, 0, 0, 0, 0), 6: (4, 3, 3, 0, 0, 0, 0, 0, 0),
                7: (4, 3, 3, 1, 0, 0, 0, 0, 0), 8: (4, 3, 3, 2, 0, 0, 0, 0, 0),
                9: (4, 3, 3, 3, 1, 0, 0, 0, 0), 10: (4, 3, 3, 3, 2, 0, 0, 0, 0),
                11: (4, 3, 3, 3, 2, 1, 0, 0, 0), 12: (4, 3, 3, 3, 2, 1, 0, 0, 0),
                13: (4, 3, 3, 3, 2, 1, 1, 0, 0), 14: (4, 3, 3, 3, 2, 1, 1, 0, 0),
                15: (4, 3, 3, 3, 2, 1, 1, 1, 0), 16: (4, 3, 3, 3, 2, 1, 1, 1, 0),
                17: (4, 3, 3, 3, 2, 1, 1, 1, 1), 18: (4, 3, 3, 3, 3, 1, 1, 1, 1),
                19: (4, 3, 3, 3, 3, 2, 1, 1, 1), 20: (4, 3, 3, 3, 3, 2, 2, 1, 1)
            }
            DND_HALF_CASTER_SLOTS = {
                1: (0, 0, 0, 0, 0), 2: (2, 0, 0, 0, 0), 3: (3, 0, 0, 0, 0), 4: (3, 0, 0, 0, 0),
                5: (4, 2, 0, 0, 0), 6: (4, 2, 0, 0, 0), 7: (4, 3, 0, 0, 0), 8: (4, 3, 0, 0, 0),
                9: (4, 3, 2, 0, 0), 10: (4, 3, 2, 0, 0), 11: (4, 3, 3, 0, 0), 12: (4, 3, 3, 0, 0),
                13: (4, 3, 3, 1, 0), 14: (4, 3, 3, 1, 0), 15: (4, 3, 3, 2, 0), 16: (4, 3, 3, 2, 0),
                17: (4, 3, 3, 3, 1), 18: (4, 3, 3, 3, 1), 19: (4, 3, 3, 3, 2), 20: (4, 3, 3, 3, 2)
            }
            DND_THIRD_CASTER_SLOTS = {
                1: (0, 0, 0, 0), 2: (0, 0, 0, 0), 3: (2, 0, 0, 0), 4: (3, 0, 0, 0),
                5: (3, 0, 0, 0), 6: (3, 0, 0, 0), 7: (4, 2, 0, 0), 8: (4, 2, 0, 0),
                9: (4, 2, 0, 0), 10: (4, 3, 0, 0), 11: (4, 3, 0, 0), 12: (4, 3, 0, 0),
                13: (4, 3, 2, 0), 14: (4, 3, 2, 0), 15: (4, 3, 2, 0), 16: (4, 3, 3, 0),
                17: (4, 3, 3, 0), 18: (4, 3, 3, 0), 19: (4, 3, 3, 1), 20: (4, 3, 3, 1)
            }
            
            is_low = any(c in class_name for c in ("paladin", "ranger"))
            is_mid = any(c in class_name for c in ("knight", "trickster", "arcane"))
            
            if is_low:
                slots = DND_HALF_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0))
            elif is_mid:
                slots = DND_THIRD_CASTER_SLOTS.get(level, (0, 0, 0, 0))
            else:
                slots = DND_FULL_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0, 0, 0, 0, 0))
                
            for spell_lvl, val in enumerate(slots, 1):
                if val > 0:
                    spell_slots[str(spell_lvl)] = val
                    
        derived["spell_slots"] = spell_slots

        # Apply standard mechanics
        self.apply_mechanics(character, derived)
        derived["applied_modifiers"] = self.get_active_mechanics(character).get("applied_modifiers", [])

        return derived

    def apply_mechanics(self, character: Dict[str, Any], derived: Dict[str, Any]) -> None:
        active = self.get_active_mechanics(character)
        mechanics = active["mechanics"]
        
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        
        hp_bonus = 0
        speed_bonus = 0
        init_bonus = 0
        ac_bonus = 0
        
        base_ac = 10
        armor_dex_cap = 999
        armor_adds_dex = True
        has_armor = False
        shield_bonus = 0
        
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                try:
                    val = int(val.replace("+", "").strip())
                except ValueError:
                    val = 0
                    
            if target == "hp":
                hp_bonus += val
            elif target == "speed":
                speed_bonus += val
            elif target == "initiative":
                init_bonus += val
            elif target == "ac":
                mode = m.get("mode", "add")
                if mode == "armor":
                    base_ac = val
                    has_armor = True
                    dex_max = m.get("dex_max")
                    if dex_max is not None:
                        armor_dex_cap = dex_max
                    else:
                        if val >= 16:
                            armor_dex_cap = 0
                            armor_adds_dex = False
                        elif val >= 12:
                            armor_dex_cap = 2
                            armor_adds_dex = True
                        else:
                            armor_dex_cap = 999
                            armor_adds_dex = True
                elif mode == "shield":
                    shield_bonus += val
                elif mode == "natural_armor":
                    base_ac = max(base_ac, val)
                    has_armor = True
                else:
                    ac_bonus += val
                    
        dex_mod = mods["dexterity"]
        if armor_adds_dex:
            dex_contrib = min(dex_mod, armor_dex_cap)
            if dex_contrib < 0 and armor_dex_cap == 0:
                dex_contrib = 0
        else:
            dex_contrib = 0
            
        if not has_armor:
            base_ac = 10 + dex_mod
            dex_contrib = 0
            
        final_ac = base_ac + dex_contrib + shield_bonus + ac_bonus
        derived["armor_class"] = final_ac
        
        derived["hit_points"] += hp_bonus
        derived["initiative"] += init_bonus
        
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                try: val = int(val.replace("+", ""))
                except: val = 0
            if target.startswith("saving_throws."):
                parts = target.split('.')
                save_type = parts[1].capitalize()
                if save_type == "All":
                    for s in derived["saving_throws"]:
                        derived["saving_throws"][s] += val
                elif save_type in derived["saving_throws"]:
                    derived["saving_throws"][save_type] += val
                    
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                try: val = int(val.replace("+", ""))
                except: val = 0
            if target.startswith("skills."):
                parts = target.split('.')
                skill_name = parts[1].title()
                if skill_name in derived["skills"]:
                    derived["skills"][skill_name] += val



class PF1e_Calculator(BaseCalculator):
    """Calculations engine for Pathfinder 1st Edition ONLY.
    PF2e is explicitly NOT supported — all rules follow PF1e (d20 PFRPG).
    """

    # ------------------------------------------------------------------ #
    # Armor Check Penalty applies to these skills (PF1e Core Rulebook)   #
    # ------------------------------------------------------------------ #
    ACP_SKILLS = {
        "Acrobatics", "Climb", "Disable Device", "Escape Artist",
        "Fly", "Ride", "Sleight of Hand", "Stealth", "Swim"
    }

    PF_SKILL_AB: Dict[str, str] = {
        "Climb": "strength", "Swim": "strength",
        "Acrobatics": "dexterity", "Disable Device": "dexterity",
        "Escape Artist": "dexterity", "Fly": "dexterity",
        "Ride": "dexterity", "Sleight of Hand": "dexterity", "Stealth": "dexterity",
        "Appraise": "intelligence", "Craft": "intelligence",
        "Linguistics": "intelligence", "Spellcraft": "intelligence",
        "Heal": "wisdom", "Perception": "wisdom", "Profession": "wisdom",
        "Sense Motive": "wisdom", "Survival": "wisdom",
        "Bluff": "charisma", "Diplomacy": "charisma", "Disguise": "charisma",
        "Handle Animal": "charisma", "Intimidate": "charisma",
        "Perform": "charisma", "Use Magic Device": "charisma",
        "Knowledge (Arcana)": "intelligence", "Knowledge (Dungeoneering)": "intelligence",
        "Knowledge (Engineering)": "intelligence", "Knowledge (Geography)": "intelligence",
        "Knowledge (History)": "intelligence", "Knowledge (Local)": "intelligence",
        "Knowledge (Nature)": "intelligence", "Knowledge (Nobility)": "intelligence",
        "Knowledge (Planes)": "intelligence", "Knowledge (Religion)": "intelligence",
    }

    PF_SKILL_LIST = [
        "Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device",
        "Disguise", "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Linguistics",
        "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand",
        "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device",
        "Knowledge (Arcana)", "Knowledge (Dungeoneering)", "Knowledge (Engineering)",
        "Knowledge (Geography)", "Knowledge (History)", "Knowledge (Local)",
        "Knowledge (Nature)", "Knowledge (Nobility)", "Knowledge (Planes)", "Knowledge (Religion)",
    ]

    # ------------------------------------------------------------------ #
    # MAIN PIPELINE — update_all_stats()                                   #
    # UI calls manager.recalculate_character() → this method             #
    # ------------------------------------------------------------------ #

    def update_all_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """PF1e 1st Edition — 5-step dependency-ordered calculation pipeline.

        ADIM 1: Ham Statlar + Irk Bonuslari → Stat Degistiriciler (Modifiers)
        ADIM 2: Sinif verisi → BAB progression, Base Saves, Skill Ranks/Class Skills
        ADIM 3: Feat/Trait mekanikleri → AC, saves, skills'e dogrudan etki
        ADIM 4: Envanter tarama → Armor Check Penalty, Max Dex siniri, AC bilesenler
        ADIM 5: Nihai CMB, CMD, Inisiyatif, HP → character_state'e yaz
        """
        derived: Dict[str, Any] = {}
        level = max(1, int(character.get("level", 1)))

        # ── ADIM 1: Stat skorlari + irk bonuslari → modifierlar ─────────────────
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        derived["ability_scores"]    = {ab.title(): scores.get(ab, 10) for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): mods[ab] for ab in abilities}

        # ── ADIM 2: Sinif → BAB, Base Saves, Class Skills, HP die ───────────────
        class_data   = character.get("class_data", {}) or {}
        if isinstance(class_data, dict) and "sistem_verisi" in class_data and isinstance(class_data["sistem_verisi"], dict):
            sv = class_data["sistem_verisi"]
            for k, v in sv.items():
                if k not in class_data or not class_data[k]:
                    class_data[k] = v

        char_class_name = str(character.get("class") or class_data.get("isim") or class_data.get("name") or "").strip()
        class_skills = class_data.get("class_skills") or []
        
        # Fallback to PF1E_CLASS_FULL_DETAILS if class_skills is empty
        if not class_skills and char_class_name:
            try:
                from scraper.seed_pf1e_class_details import PF1E_CLASS_FULL_DETAILS
                for cls_k, cls_info in PF1E_CLASS_FULL_DETAILS.items():
                    if cls_k.lower() in char_class_name.lower():
                        class_skills = cls_info.get("class_skills", [])
                        if not class_data.get("hit_die"):
                            class_data["hit_die"] = cls_info.get("hit_die")
                        if not class_data.get("skill_ranks_per_level"):
                            class_data["skill_ranks_per_level"] = cls_info.get("skill_ranks_per_level")
                        if not class_data.get("saving_throws"):
                            class_data["saving_throws"] = cls_info.get("saving_throws")
                        break
            except Exception:
                pass

        bab_prog = str(class_data.get("bab_progression", "medium")).lower()

        # ── ADIM 3 Pre-fetch: Fetch mechanics early to find extra class skills ──
        active    = self.get_active_mechanics(character)
        mechanics = active.get("mechanics", [])

        # Build normalized class_skills_set with Knowledge (all) expansion
        class_skills_set = set()
        for cs in class_skills:
            cs_str = str(cs).strip()
            if cs_str.lower() in ("knowledge (all)", "knowledge(all)", "all knowledge"):
                for sk in self.PF_SKILL_LIST:
                    if sk.startswith("Knowledge"):
                        class_skills_set.add(sk.lower())
            else:
                class_skills_set.add(cs_str.lower())

        for m in mechanics:
            if m.get("makes_class_skill") and m.get("skill_name"):
                class_skills_set.add(str(m.get("skill_name")).strip().lower())

        # Multiclass Stacking Support (PF1e CRB p. 30)
        multiclass_data = character.get("multiclass")
        if multiclass_data and isinstance(multiclass_data, dict) and len(multiclass_data) > 0:
            from rules.archetype_engine import PF1eMulticlassEngine
            mc_res = PF1eMulticlassEngine.calculate_multiclass_progression(multiclass_data)
            bab = mc_res["total_bab"]
            derived["bab"] = bab
            saves: Dict[str, int] = {
                "Fortitude": mc_res["base_fort"] + mods["constitution"],
                "Reflex": mc_res["base_ref"] + mods["dexterity"],
                "Will": mc_res["base_will"] + mods["wisdom"]
            }
            derived["saving_throws"] = saves
        else:
            # BAB (PF1e Core: Full=level, Medium=3/4*level, Poor=1/2*level)
            if bab_prog == "full":
                bab = level
            elif bab_prog == "medium":
                bab = (level * 3) // 4
            else:
                bab = level // 2
            derived["bab"] = bab

            # Base Saves (Good: 2 + level/2, Poor: level/3)
            save_prog = class_data.get("saving_throws", {}) or {}
            saves: Dict[str, int] = {}
            for save_type, ab in [("fortitude", "constitution"), ("reflex", "dexterity"), ("will", "wisdom")]:
                prog      = str(save_prog.get(save_type, "poor")).lower()
                base_save = (2 + level // 2) if prog == "good" else (level // 3)
                saves[save_type.title()] = base_save + mods[ab]
            derived["saving_throws"] = saves

        # Archetype Compatibility & Feature Replacements (PF1e APG p. 72)
        from rules.archetype_engine import PF1eArchetypeEngine
        raw_archs = character.get("archetypes") or character.get("archetype") or []
        if isinstance(raw_archs, str):
            raw_archs = [raw_archs]
        elif not isinstance(raw_archs, list):
            raw_archs = []

        if raw_archs:
            char_cls = character.get("class", "Fighter")
            is_compat, conflicts = PF1eArchetypeEngine.validate_archetype_compatibility(char_cls, raw_archs)
            arch_feats = PF1eArchetypeEngine.get_archetype_features(char_cls, raw_archs)
            derived["archetype_details"] = {
                "is_compatible": is_compat,
                "conflicts": conflicts,
                "replaced_features": arch_feats["replaced_features"],
                "granted_features": arch_feats["granted_features"]
            }

        # HP (PF1e: Max at 1st, average+1 thereafter)
        hit_die_raw = str(class_data.get("hit_die", "8")).lower()
        try:
            hit_die = int(hit_die_raw.split("d")[-1])
        except ValueError:
            hit_die = 8
        con_mod = mods["constitution"]
        hp = hit_die + con_mod + (level - 1) * (hit_die // 2 + 1 + con_mod)
        derived["hit_points"] = max(1, hp)

        # Skill Ranks (each level: class_int_modifier + int_mod ranks; default rank source = character)
        skill_ranks = character.get("skill_ranks") or character.get("skills") or {}

        # ── ADIM 2b: Skill base values (Rank + Ability Mod + Class Skill +3) ────
        # PF1e Class Skill rule: +3 bonus ONLY if rank >= 1 AND skill is a class skill
        raw_skills: Dict[str, int] = {}
        skills_detail: Dict[str, Dict[str, Any]] = {}
        for sk in self.PF_SKILL_LIST:
            ranks       = max(0, int(skill_ranks.get(sk, 0)))
            ab          = self.PF_SKILL_AB.get(sk, "intelligence")
            ab_mod      = mods.get(ab, 0)
            is_class    = sk.lower() in class_skills_set
            class_bonus = 3 if (is_class and ranks > 0) else 0
            total       = ranks + ab_mod + class_bonus
            raw_skills[sk] = total
            skills_detail[sk] = {
                "ranks": ranks,
                "ability_modifier": ab_mod,
                "is_class_skill": is_class,
                "class_bonus": class_bonus,
                "total": total
            }
        derived["skills"] = raw_skills
        derived["skills_detail"] = skills_detail
        derived["class_skills_active"] = [sk for sk in self.PF_SKILL_LIST if sk.lower() in class_skills_set]

        # ── ADIM 3: Feat/Trait/Race mekanikleri uygula ──────────────────────────
        # (standard_mechanics JSON'dan ve traits'den gelen dogrudan bonus'lar)
        misc_ac_bonus  = 0
        deflect_bonus  = 0
        feat_bab_bonus = 0
        acp_reduction  = 0
        for m in mechanics:
            target = m.get("target", "")
            try:
                val = self.eval_formula(str(m.get("value", 0)), character, derived)
            except Exception:
                val = 0
            if target == "initiative":
                derived["initiative"] = derived.get("initiative", mods["dexterity"]) + val
            elif target == "hp":
                derived["hit_points"] += val
            elif target == "bab":
                feat_bab_bonus += val
            elif target == "ac":
                mode = m.get("mode", "add")
                if mode == "deflection":
                    deflect_bonus += val
                elif mode not in ("armor", "shield", "natural_armor"):
                    misc_ac_bonus += val
            elif target == "armor_check_penalty":
                acp_reduction += val
            elif target.startswith("saving_throws."):
                save_type = target.split(".")[1].capitalize()
                if save_type == "All":
                    for s in derived["saving_throws"]:
                        derived["saving_throws"][s] += val
                elif save_type in derived["saving_throws"]:
                    derived["saving_throws"][save_type] += val
            elif target.startswith("skills."):
                sk_name = target[len("skills."):]
                if sk_name in derived["skills"]:
                    derived["skills"][sk_name] += val

        derived["bab"] += feat_bab_bonus

        # ── ADIM 4: Feat/Trait & Envanter → Weapon Attack, Damage, Armor, ACP, Speed ──────────
        feat_names = set()
        for f in character.get("feats", []):
            fn = f.get("isim") or f.get("name") if isinstance(f, dict) else str(f)
            if fn: feat_names.add(fn.lower())

        trait_names = set()
        for t in character.get("traits", []):
            tn = t.get("isim") or t.get("name") if isinstance(t, dict) else str(t)
            if tn: trait_names.add(tn.lower())

        has_weapon_finesse = any("finesse" in f for f in feat_names)
        has_weapon_focus = any("weapon focus" in f for f in feat_names)
        has_point_blank = any("point-blank" in f or "point blank" in f for f in feat_names)
        has_dodge = any("dodge" in f for f in feat_names)
        has_fleet = any("fleet" in f for f in feat_names)
        has_armor_expert = any("armor expert" in t for t in trait_names)
        has_reactionary = any("reactionary" in t for t in trait_names)

        # Dodge Feat (+1 Dodge AC)
        if has_dodge:
            misc_ac_bonus += 1

        # Fleet Feat (+5 ft Speed)
        base_speed = 30
        if has_fleet:
            base_speed += 5

        armor_bonus, shield_bonus, natural_armor, acp, dex_max = self._extract_armor(character)

        # Character-level overrides
        armor_bonus   = max(armor_bonus, int(character.get("armor_bonus", 0)))
        shield_bonus  = max(shield_bonus, int(character.get("shield_bonus", 0)))
        natural_armor = int(character.get("natural_armor", 0))
        size_ac       = int(character.get("size_modifier_ac", 0))

        # Categorize equipment & calculate total weight
        eq_list = character.get("equipment", [])
        categorized = categorize_items(eq_list)
        derived["armor_shields"] = categorized["armor_shields"]
        derived["consumables"] = categorized["consumables"]
        derived["gear"] = categorized["gear"]

        # Calculate Total Equipment Weight & Carrying Capacity
        total_weight = 0.0
        for item in eq_list:
            if isinstance(item, dict):
                w, q = extract_weight_and_qty(item)
                total_weight += w * q

        str_score = scores.get("strength", 10)
        char_size = str(character.get("size") or character.get("raceData", {}).get("size") or "Medium")
        capacity = calculate_carrying_capacity(str_score, char_size)
        encumbrance = calculate_encumbrance_status(total_weight, capacity)

        derived["total_weight"] = encumbrance["total_weight"]
        derived["carrying_capacity"] = capacity
        derived["encumbrance"] = encumbrance

        # Speed Penalty from Medium/Heavy Armor or Encumbrance Load
        is_dwarf = "dwarf" in str(character.get("race", "")).lower()
        armor_type = "light"
        for arm in categorized["armor_shields"]:
            sv_arm = arm.get("sistem_verisi") or {}
            a_category = str(sv_arm.get("category") or sv_arm.get("armor_type") or "").lower()
            a_name = str(arm.get("name") or arm.get("isim") or "").lower()
            if "heavy" in a_category or "plate" in a_name or "full plate" in a_name:
                armor_type = "heavy"
            elif "medium" in a_category or "breastplate" in a_name or "chainmail" in a_name or "scale" in a_name:
                armor_type = "medium"

        if (armor_type in ("medium", "heavy") or encumbrance["status"] in ("Medium Load", "Heavy Load", "Overloaded")) and not is_dwarf:
            derived["speed"] = max(15, base_speed - 10)
        else:
            derived["speed"] = base_speed

        # Apply Encumbrance Armor Check Penalty (ACP)
        acp += encumbrance["encumbrance_acp"]

        # Armor Check Penalty (ACP) adjustment with Armor Expert trait (-1 ACP)
        if acp < 0:
            if has_armor_expert:
                acp = min(0, acp + 1)
            if acp_reduction != 0:
                acp_adj = abs(acp_reduction) if acp_reduction < 0 else acp_reduction
                acp = min(0, acp + acp_adj)
            for sk in self.ACP_SKILLS:
                if sk in derived["skills"]:
                    ranks = max(0, int(skill_ranks.get(sk, 0)))
                    if ranks > 0:
                        derived["skills"][sk] += acp

        derived["armor_check_penalty"] = acp

        # Max Dex kısıtlamasını uygula (Armor & Encumbrance)
        if encumbrance["max_dex_bonus"] is not None:
            dex_max = min(dex_max, encumbrance["max_dex_bonus"])

        dex_contrib = min(mods["dexterity"], dex_max) if dex_max < 999 else mods["dexterity"]


        # ── ADIM 5: Nihai AC, CMB, CMD, Inisiyatif ve Silah Atak/Hasar Bloğu ────────
        size_cmb = int(character.get("size_modifier", 0))
        derived["initiative"] = derived.get("initiative", mods["dexterity"])

        derived["armor_class"]    = 10 + dex_contrib + armor_bonus + shield_bonus + natural_armor + deflect_bonus + misc_ac_bonus + size_ac
        derived["touch_ac"]       = 10 + dex_contrib + deflect_bonus + misc_ac_bonus + size_ac
        derived["flat_footed_ac"] = 10 + armor_bonus + shield_bonus + natural_armor + deflect_bonus + misc_ac_bonus + size_ac
        derived["cmb"]            = derived["bab"] + mods["strength"] - size_cmb
        derived["cmd"]            = 10 + derived["bab"] + mods["strength"] + dex_contrib - size_cmb + deflect_bonus
        derived["melee_attack_bonus"]  = derived["bab"] + mods["strength"]
        derived["ranged_attack_bonus"] = derived["bab"] + mods["dexterity"]

        derived["ac_breakdown"] = {
            "armor": armor_bonus,
            "shield": shield_bonus,
            "dex": dex_contrib,
            "natural": natural_armor,
            "deflection": deflect_bonus,
            "misc": misc_ac_bonus + size_ac
        }

        # Calculate Weapon Cards (Attacks & Damage)
        calculated_weapons = []
        for w in categorized["weapons"]:
            w_name = w.get("name") or w.get("isim") or "Silah"
            w_name_lower = w_name.lower()
            sv_w = w.get("sistem_verisi") or {}
            sys_w = sv_w.get("system", {}) if isinstance(sv_w.get("system"), dict) else {}
            
            is_ranged = any(r in w_name_lower for r in ("bow", "crossbow", "sling", "dart", "javelin", "shuriken", "gun", "pistol", "rifle", "musket", "blunderbuss")) or ("ranged" in str(sys_w.get("weaponType", "")).lower())
            is_finesseable = any(f in w_name_lower for f in ("dagger", "rapier", "shortsword", "kama", "nunchaku", "sai", "whip")) or ("light" in str(sys_w.get("weaponType", "")).lower())
            
            if is_ranged:
                atk_stat_mod = mods["dexterity"]
            elif is_finesseable and has_weapon_finesse:
                atk_stat_mod = mods["dexterity"]
            else:
                atk_stat_mod = mods["strength"]
                
            enhancement = 0
            enh_match = re.search(r'\+([1-5])\b', w_name)
            if enh_match:
                enhancement = int(enh_match.group(1))
            else:
                enhancement = int(sv_w.get("enhancement") or sys_w.get("enhancement") or 0)
                
            wf_bonus = 1 if has_weapon_focus else 0
            pbs_atk = 1 if (is_ranged and has_point_blank) else 0
            pbs_dmg = 1 if (is_ranged and has_point_blank) else 0
            
            total_atk = derived["bab"] + atk_stat_mod + enhancement + wf_bonus + pbs_atk
            atk_str = f"+{total_atk}" if total_atk >= 0 else str(total_atk)
            
            # Base damage determination
            raw_base = sys_w.get("damage") or sv_w.get("damage")
            if isinstance(raw_base, dict):
                parts = raw_base.get("parts", [])
                raw_base = parts[0][0] if parts and isinstance(parts[0], (list, tuple)) else "1d8"
            
            base_damage = None
            if raw_base and isinstance(raw_base, str):
                m_size = re.search(r'sizeRoll\(\s*(\d+)\s*,\s*(\d+)', raw_base, re.I)
                if m_size:
                    base_damage = f"{m_size.group(1)}d{m_size.group(2)}"
                else:
                    m_dice = re.search(r'\b(\d+d\d+)\b', raw_base, re.I)
                    if m_dice:
                        base_damage = m_dice.group(1)

            if not base_damage or base_damage == "-":
                if "dagger" in w_name_lower or "knife" in w_name_lower: base_damage = "1d4"
                elif "shortsword" in w_name_lower or "scimitar" in w_name_lower or "club" in w_name_lower or "shortbow" in w_name_lower or "kama" in w_name_lower: base_damage = "1d6"
                elif "greatsword" in w_name_lower or "greataxe" in w_name_lower: base_damage = "2d6"
                elif "falchion" in w_name_lower: base_damage = "2d4"
                elif "longsword" in w_name_lower or "battleaxe" in w_name_lower or "warhammer" in w_name_lower or "longbow" in w_name_lower or "heavy crossbow" in w_name_lower: base_damage = "1d8"
                elif "bastard" in w_name_lower or "halberd" in w_name_lower or "musket" in w_name_lower: base_damage = "1d10"
                else: base_damage = "1d8"

            # Crit Range determination
            crit_range = sys_w.get("critRange") or sv_w.get("crit_range")
            crit_mult = sys_w.get("critMult") or sv_w.get("crit_mult") or "x2"
            if not crit_range:
                if any(k in w_name_lower for k in ("rapier", "scimitar", "falchion", "kukri")): crit_range = "18-20/x2"
                elif any(k in w_name_lower for k in ("greatsword", "longsword", "shortsword", "bastard")): crit_range = "19-20/x2"
                elif any(k in w_name_lower for k in ("battleaxe", "greataxe", "heavy crossbow", "longbow")): crit_range = "20/x3"
                elif any(k in w_name_lower for k in ("scythe", "pick")): crit_range = "20/x4"
                else: crit_range = f"20/{crit_mult}"
            elif "/" not in str(crit_range):
                crit_range = f"{crit_range}/{crit_mult}"

            is_two_handed = any(t in w_name_lower for t in ("greatsword", "greataxe", "spear", "halberd", "scythe", "quarterstaff", "falchion", "heavy crossbow", "longbow"))
            if is_two_handed and not is_ranged:
                dmg_stat_mod = int(mods["strength"] * 1.5)
            elif is_ranged:
                dmg_stat_mod = 0
            else:
                dmg_stat_mod = mods["strength"]
                
            total_dmg_mod = dmg_stat_mod + enhancement + pbs_dmg
            dmg_str = f"{base_damage} + {total_dmg_mod}" if total_dmg_mod > 0 else (f"{base_damage} - {abs(total_dmg_mod)}" if total_dmg_mod < 0 else str(base_damage))
            
            w_copy = dict(w)
            w_copy["calculated_attack"] = atk_str
            w_copy["calculated_damage"] = dmg_str
            w_copy["crit_range"] = str(crit_range)
            w_copy["name"] = w_name
            w_copy["isim"] = w_name
            calculated_weapons.append(w_copy)

        derived["weapons"] = calculated_weapons

        # Envanter Ağıralık Hesabı
        total_weight = 0.0
        for item in character.get("equipment", []):
            if isinstance(item, dict):
                w_val, qty = extract_weight_and_qty(item)
                total_weight += w_val * qty
        derived["total_weight"] = round(total_weight, 2)
        
        # Strength'e göre PF1e Carrying Capacity limitleri
        str_score = derived["ability_scores"].get("Strength", 10)
        
        PF_STR_LOADS = {
            1: (3, 6, 10), 2: (6, 13, 20), 3: (10, 20, 30), 4: (13, 26, 40), 5: (16, 33, 50),
            6: (20, 40, 60), 7: (23, 46, 70), 8: (26, 53, 80), 9: (30, 60, 90), 10: (33, 66, 100),
            11: (38, 76, 115), 12: (43, 86, 130), 13: (50, 100, 150), 14: (58, 116, 175), 15: (66, 133, 200),
            16: (76, 153, 230), 17: (86, 173, 260), 18: (100, 200, 300), 19: (116, 233, 350), 20: (133, 266, 400),
            21: (153, 306, 460), 22: (173, 346, 520), 23: (200, 400, 600), 24: (233, 466, 700), 25: (266, 533, 800),
            26: (306, 613, 920), 27: (346, 693, 1040), 28: (400, 800, 1200), 29: (466, 933, 1400)
        }
        
        if str_score <= 29:
            light, med, heavy = PF_STR_LOADS.get(max(1, str_score), (33, 66, 100))
        else:
            factor = 4 ** ((str_score - 20) // 10)
            base_str = (str_score - 20) % 10 + 20
            base_light, base_med, base_heavy = PF_STR_LOADS[base_str]
            light, med, heavy = base_light * factor, base_med * factor, base_heavy * factor
            
        derived["carrying_capacity"] = {
            "light": light,
            "medium": med,
            "heavy": heavy
        }
        
        if total_weight <= light:
            derived["encumbrance_status"] = "Light"
        elif total_weight <= med:
            derived["encumbrance_status"] = "Medium"
            dex_max = min(dex_max, 3)
            if not is_dwarf:
                derived["speed"] = min(derived["speed"], 20 if base_speed >= 30 else 15)
        elif total_weight <= heavy:
            derived["encumbrance_status"] = "Heavy"
            dex_max = min(dex_max, 1)
            if not is_dwarf:
                derived["speed"] = min(derived["speed"], 20 if base_speed >= 30 else 15)
        else:
            derived["encumbrance_status"] = "Overloaded"
            derived["speed"] = 0

        # PF1e Büyü Slotları
        spell_slots = {}
        casting_ability = class_data.get("spellcasting_ability", "")
        class_name_lower = str(character.get("class", "")).lower()
        if not casting_ability:
            if any(c in class_name_lower for c in ("wizard", "arcanist", "witch", "alchemist", "magus", "investigator")):
                casting_ability = "intelligence"
            elif any(c in class_name_lower for c in ("sorcerer", "bard", "summoner", "oracle", "bloodrager", "skald", "paladin", "mesmerist")):
                casting_ability = "charisma"
            elif any(c in class_name_lower for c in ("cleric", "druid", "ranger", "inquisitor", "shaman", "warpriest", "hunter", "spiritualist", "adept")):
                casting_ability = "wisdom"
                
        if casting_ability:
            casting_stat = casting_ability.lower()
            casting_mod = mods.get(casting_stat, 0)
            
            PF_FULL_CASTER_SLOTS = {
                1: (3, 1, 0, 0, 0, 0, 0, 0, 0, 0), 2: (4, 2, 0, 0, 0, 0, 0, 0, 0, 0),
                3: (4, 2, 1, 0, 0, 0, 0, 0, 0, 0), 4: (4, 3, 2, 0, 0, 0, 0, 0, 0, 0),
                5: (4, 3, 2, 1, 0, 0, 0, 0, 0, 0), 6: (4, 3, 3, 2, 0, 0, 0, 0, 0, 0),
                7: (4, 4, 3, 2, 1, 0, 0, 0, 0, 0), 8: (4, 4, 3, 3, 2, 0, 0, 0, 0, 0),
                9: (4, 4, 4, 3, 2, 1, 0, 0, 0, 0), 10: (4, 4, 4, 3, 3, 2, 0, 0, 0, 0),
                11: (4, 4, 4, 4, 3, 2, 1, 0, 0, 0), 12: (4, 4, 4, 4, 3, 3, 2, 0, 0, 0),
                13: (4, 4, 4, 4, 4, 3, 2, 1, 0, 0), 14: (4, 4, 4, 4, 4, 3, 3, 2, 0, 0),
                15: (4, 4, 4, 4, 4, 4, 3, 2, 1, 0), 16: (4, 4, 4, 4, 4, 4, 3, 3, 2, 0),
                17: (4, 4, 4, 4, 4, 4, 4, 3, 2, 1), 18: (4, 4, 4, 4, 4, 4, 4, 3, 3, 2),
                19: (4, 4, 4, 4, 4, 4, 4, 4, 3, 3), 20: (4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
            }
            PF_MID_CASTER_SLOTS = {
                1: (4, 1, 0, 0, 0, 0, 0), 2: (5, 2, 0, 0, 0, 0, 0), 3: (6, 3, 0, 0, 0, 0, 0),
                4: (6, 3, 1, 0, 0, 0, 0), 5: (6, 4, 2, 0, 0, 0, 0), 6: (6, 4, 3, 0, 0, 0, 0),
                7: (6, 4, 3, 1, 0, 0, 0), 8: (6, 4, 4, 2, 0, 0, 0), 9: (6, 5, 4, 3, 0, 0, 0),
                10: (6, 5, 4, 3, 1, 0, 0), 11: (6, 5, 4, 4, 2, 0, 0), 12: (6, 5, 5, 4, 3, 0, 0),
                13: (6, 5, 5, 4, 3, 1, 0), 14: (6, 5, 5, 4, 4, 2, 0), 15: (6, 5, 5, 5, 4, 3, 0),
                16: (6, 5, 5, 5, 4, 3, 1), 17: (6, 5, 5, 5, 4, 4, 2), 18: (6, 5, 5, 5, 5, 4, 3),
                19: (6, 5, 5, 5, 5, 5, 4), 20: (6, 5, 5, 5, 5, 5, 5)
            }
            PF_LOW_CASTER_SLOTS = {
                1: (0, 0, 0, 0, 0), 2: (0, 0, 0, 0, 0), 3: (0, 0, 0, 0, 0), 4: (0, 0, 0, 0, 0),
                5: (0, 1, 0, 0, 0), 6: (0, 1, 0, 0, 0), 7: (0, 1, 1, 0, 0), 8: (0, 1, 1, 0, 0),
                9: (0, 2, 1, 0, 0), 10: (0, 2, 1, 1, 0), 11: (0, 2, 1, 1, 0), 12: (0, 2, 2, 1, 1),
                13: (0, 3, 2, 1, 1), 14: (0, 3, 2, 2, 1), 15: (0, 3, 2, 2, 1), 16: (0, 3, 3, 2, 2),
                17: (0, 4, 3, 2, 2), 18: (0, 4, 3, 3, 2), 19: (0, 4, 3, 3, 3), 20: (0, 4, 4, 3, 3)
            }
            
            is_low = any(c in class_name_lower for c in ("paladin", "ranger"))
            is_mid = any(c in class_name_lower for c in ("bard", "skald", "inquisitor", "alchemist"))
            
            if is_low:
                slots = list(PF_LOW_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0)))
            elif is_mid:
                slots = list(PF_MID_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0, 0, 0)))
            else:
                slots = list(PF_FULL_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)))
                
            for spell_lvl in range(1, len(slots)):
                if slots[spell_lvl] > 0 or (is_low and level >= 5 and spell_lvl <= 4):
                    if casting_mod >= spell_lvl:
                        bonus = (casting_mod - spell_lvl) // 4 + 1
                        slots[spell_lvl] += bonus
                        
            for spell_lvl, val in enumerate(slots):
                if val > 0:
                    spell_slots[str(spell_lvl)] = val
                    
        derived["spell_slots"] = spell_slots

        # PF1e Spellcasting Engine Deepening (Caster Level, Concentration, Spell Save DCs, Bonus Slots)
        from rules.spell_engine import (
            get_casting_ability_for_class,
            calculate_bonus_spell_slots,
            calculate_spell_save_dc,
            calculate_total_spell_slots
        )

        c_ability = get_casting_ability_for_class(class_name_lower) or casting_ability or "intelligence"
        c_stat_mod = mods.get(c_ability.lower(), 0)
        c_score = derived["ability_scores"].get(c_ability.title(), 10)

        # Caster Level (CL)
        if any(r in class_name_lower for r in ("ranger", "paladin")):
            cl_val = max(1, level - 3) if level >= 4 else 0
        else:
            cl_val = level

        # Concentration Check (CL + Casting Mod + Combat Casting (+4 if present))
        has_combat_casting = any("combat casting" in str(f).lower() for f in character.get("feats", []))
        concentration_bonus = cl_val + c_stat_mod + (4 if has_combat_casting else 0)

        # Spell Save DCs (10 + Spell Level + Casting Mod + Spell Focus (+1 if present))
        has_spell_focus = any("spell focus" in str(f).lower() for f in character.get("feats", []))
        misc_dc_bonus = 1 if has_spell_focus else 0
        spell_dcs = {
            str(lvl_i): calculate_spell_save_dc(lvl_i, c_stat_mod, misc_dc_bonus)
            for lvl_i in range(0, 10)
        }

        bonus_slots_dict = calculate_bonus_spell_slots(c_score)
        tot_slots_dict = calculate_total_spell_slots(class_name_lower, level, c_score)

        derived["spellcasting"] = {
            "primary_ability": c_ability,
            "ability_modifier": c_stat_mod,
            "caster_level": cl_val,
            "concentration_bonus": concentration_bonus,
            "has_combat_casting": has_combat_casting,
            "has_spell_focus": has_spell_focus,
            "spell_dcs": spell_dcs,
            "bonus_slots": bonus_slots_dict,
            "total_slots": tot_slots_dict
        }

        # snake_case aliases (PDF export bunları kullanır)
        derived["skills"] = {
            k.lower().replace(" ", "_"): v
            for k, v in derived["skills"].items()
        }

        derived["applied_modifiers"] = self.get_active_mechanics(character).get("applied_modifiers", [])

        # ── ADIM 6: GM Custom Modifiers (Manuel Müdahaleler +X / -X) ─────────
        custom_mods = character.get("custom_modifiers", [])
        if isinstance(custom_mods, dict):
            for stat_key, val in custom_mods.items():
                try:
                    val_int = int(val)
                except (ValueError, TypeError):
                    continue
                k_lower = stat_key.lower().strip()
                if k_lower in ("ac", "armor_class"):
                    derived["armor_class"] += val_int
                    derived["touch_ac"] += val_int
                    derived["flat_footed_ac"] += val_int
                elif k_lower in ("hp", "hit_points"):
                    derived["hit_points"] += val_int
                elif k_lower in ("bab", "base_attack_bonus"):
                    derived["bab"] += val_int
                    derived["cmb"] += val_int
                    derived["cmd"] += val_int
                elif k_lower in ("init", "initiative"):
                    derived["initiative"] += val_int
                elif k_lower in ("fort", "fortitude"):
                    if "Fortitude" in derived.get("saving_throws", {}):
                        derived["saving_throws"]["Fortitude"] += val_int
                elif k_lower in ("ref", "reflex"):
                    if "Reflex" in derived.get("saving_throws", {}):
                        derived["saving_throws"]["Reflex"] += val_int
                elif k_lower in ("will",):
                    if "Will" in derived.get("saving_throws", {}):
                        derived["saving_throws"]["Will"] += val_int
        elif isinstance(custom_mods, list):
            for m in custom_mods:
                if not isinstance(m, dict) or not m.get("is_active", True):
                    continue
                stat_key = str(m.get("stat", "")).lower().strip()
                try:
                    val_int = int(m.get("value", 0))
                except (ValueError, TypeError):
                    continue
                if stat_key in ("ac", "armor_class"):
                    derived["armor_class"] += val_int
                    derived["touch_ac"] += val_int
                    derived["flat_footed_ac"] += val_int
                elif stat_key in ("hp", "hit_points"):
                    derived["hit_points"] += val_int
                elif stat_key in ("bab", "base_attack_bonus"):
                    derived["bab"] += val_int
                    derived["cmb"] += val_int
                    derived["cmd"] += val_int
                elif stat_key in ("init", "initiative"):
                    derived["initiative"] += val_int
                elif stat_key in ("fort", "fortitude"):
                    if "Fortitude" in derived.get("saving_throws", {}):
                        derived["saving_throws"]["Fortitude"] += val_int
                elif stat_key in ("ref", "reflex"):
                    if "Reflex" in derived.get("saving_throws", {}):
                        derived["saving_throws"]["Reflex"] += val_int
                elif stat_key in ("will",):
                    if "Will" in derived.get("saving_throws", {}):
                        derived["saving_throws"]["Will"] += val_int
                elif stat_key.startswith("skill:"):
                    sk_name = stat_key.split(":", 1)[1].lower().replace(" ", "_")
                    if "skills" in derived and sk_name in derived["skills"]:
                        derived["skills"][sk_name] += val_int
                elif stat_key in ("speed", "hiz"):
                    derived["speed"] = max(0, derived.get("speed", 30) + val_int)
                elif stat_key == "cmb":
                    derived["cmb"] += val_int
                elif stat_key == "cmd":
                    derived["cmd"] += val_int

        # ADIM 7: Companion & Familiar Calculation & Master Bonus Application
        companion_raw = character.get("companion")
        if companion_raw and isinstance(companion_raw, dict):
            from rules.companion_calculator import PF1eCompanionCalculator
            comp_type = str(companion_raw.get("type", "animal_companion")).lower()
            if comp_type == "familiar":
                calc_comp = PF1eCompanionCalculator.calculate_familiar(
                    companion_raw,
                    master_level=level,
                    master_max_hp=derived.get("hit_points", 10)
                )
                master_bonus = calc_comp.get("master_bonus")
                if master_bonus and isinstance(master_bonus, dict):
                    target = master_bonus.get("target")
                    val = master_bonus.get("value", 0)
                    if target == "hp":
                        derived["hit_points"] += val
                    elif target == "initiative":
                        derived["initiative"] += val
                    elif target == "saving_throws.Reflex":
                        if "Reflex" in derived.get("saving_throws", {}):
                            derived["saving_throws"]["Reflex"] += val
                    elif target and target.startswith("skill:"):
                        sk_name = target.split(":", 1)[1]
                        sk_key = sk_name.lower().replace(" ", "_")
                        if "skills" in derived and sk_key in derived["skills"]:
                            derived["skills"][sk_key] += val
            else:
                calc_comp = PF1eCompanionCalculator.calculate_animal_companion(
                    companion_raw,
                    master_class=character.get("class", "Druid"),
                    master_level=level
                )
            derived["companion"] = calc_comp

        # ADIM 8: Variant Multiclassing (VMC) Calculation & Feature Granting
        vmc_class = str(character.get("variant_multiclass") or character.get("vmc_class") or "").strip()
        if vmc_class:
            from rules.vmc_engine import PF1eVMCEngine
            char_class = str(character.get("class", "Fighter"))
            is_vmc_valid, vmc_err = PF1eVMCEngine.is_vmc_allowed(char_class, vmc_class)
            sacrificed_feats = PF1eVMCEngine.get_sacrificed_feat_count(level, vmc_class)
            granted_vmc_feats = PF1eVMCEngine.get_granted_vmc_features(vmc_class, level)

            for v_feat in granted_vmc_feats:
                target = v_feat.get("target")
                val = v_feat.get("value", 0)
                if target == "hp":
                    derived["hit_points"] += val
                elif target == "initiative":
                    derived["initiative"] += val
                elif target == "attack_bonus":
                    derived["melee_attack_bonus"] += val
                    derived["ranged_attack_bonus"] += val
                elif target == "armor_check_penalty":
                    derived["armor_check_penalty"] = min(0, derived.get("armor_check_penalty", 0) + val)
                elif target and target.startswith("saving_throws."):
                    st_key = target.split(".")[1].capitalize()
                    if st_key in derived.get("saving_throws", {}):
                        derived["saving_throws"][st_key] += val

            derived["variant_multiclass_details"] = {
                "vmc_class": vmc_class.title(),
                "is_valid": is_vmc_valid,
                "error": vmc_err,
                "sacrificed_feat_count": sacrificed_feats,
                "granted_features": granted_vmc_feats
            }

        return derived

    def check_prerequisites(self, character: Dict[str, Any], entity_data: Dict[str, Any], is_overridden: bool = False) -> Dict[str, Any]:
        """
        Check Prerequisites for Feats/Spells/Classes (Soft-Block logic).
        Returns status dict with validation state and warnings.
        If is_overridden is True, GM bypasses hard blocks.
        """
        warnings = []
        prereqs = entity_data.get("prerequisites") or entity_data.get("sistem_verisi", {}).get("prerequisites", [])
        if isinstance(prereqs, str):
            prereqs = [prereqs]
        elif not isinstance(prereqs, list):
            prereqs = []

        scores = self.get_adjusted_abilities(character)

        # Gather current feats and traits names
        curr_feats = set()
        for f in character.get("feats", []):
            fname = f.get("isim") if isinstance(f, dict) else str(f)
            if fname: curr_feats.add(fname.lower())

        curr_traits = set()
        for t in character.get("traits", []):
            tname = t.get("isim") if isinstance(t, dict) else str(t)
            if tname: curr_traits.add(tname.lower())

        total_level = int(character.get("level", 1))

        for p in prereqs:
            p_str = str(p).strip()
            if not p_str: continue

            # 1. Ability Score requirement e.g., "Str 13", "Dex 15", "Int 13"
            m_ab = re.search(r'(Str|Dex|Con|Int|Wis|Cha)\s*(\d+)', p_str, re.I)
            if m_ab:
                ab_map = {"str": "strength", "dex": "dexterity", "con": "constitution", "int": "intelligence", "wis": "wisdom", "cha": "charisma"}
                ab_key = ab_map.get(m_ab.group(1).lower())
                req_val = int(m_ab.group(2))
                curr_val = scores.get(ab_key, 10)
                if curr_val < req_val:
                    warnings.append(f"{m_ab.group(1).upper()} >= {req_val} gerekli (Mevcut: {curr_val})")

            # 2. BAB requirement e.g., "Base attack bonus +1" or "BAB +6"
            m_bab = re.search(r'(?:Base attack bonus|BAB)\s*\+?(\d+)', p_str, re.I)
            if m_bab:
                req_bab = int(m_bab.group(1))
                curr_bab = int(character.get("bab", 0))
                if curr_bab < req_bab:
                    warnings.append(f"BAB >= +{req_bab} gerekli (Mevcut: +{curr_bab})")

            # 3. Level requirement e.g., "Character level 3rd", "Level 5"
            m_lvl = re.search(r'(?:Character level|Level)\s*(\d+)', p_str, re.I)
            if m_lvl:
                req_lvl = int(m_lvl.group(1))
                if total_level < req_lvl:
                    warnings.append(f"Karakter Seviyesi >= {req_lvl} gerekli (Mevcut: {total_level})")

            # 4. Prerequisite Feat check (e.g. "Power Attack", "Dodge", "Point-Blank Shot")
            # If string mentions common feats
            for known_feat in ["Power Attack", "Dodge", "Point-Blank Shot", "Precise Shot", "Combat Expertise", "Weapon Focus", "Mobility"]:
                if known_feat.lower() in p_str.lower() and known_feat.lower() not in curr_feats:
                    warnings.append(f"Ön Feat Gerekli: {known_feat}")

        is_valid = len(warnings) == 0 or is_overridden
        return {
            "valid": is_valid,
            "overridden": is_overridden,
            "warnings": warnings,
            "can_override": len(warnings) > 0
        }



    def _extract_armor(self, character: Dict[str, Any]):
        armor_bonus, shield_bonus, natural_armor, acp, dex_max = 0, 0, 0, 0, 999
        for item in character.get("equipment", []):
            if not isinstance(item, dict): continue
            sv = item.get("sistem_verisi") or item.get("system_data") or {}
            if not isinstance(sv, dict): sv = {}
            sys_obj = sv.get("system", {}) if isinstance(sv.get("system"), dict) else {}
            
            name = str(item.get("name") or item.get("isim") or "").lower()
            itype = str(item.get("type", item.get("kategori", sv.get("type", sv.get("category", sys_obj.get("type", ""))))))
            ikategori = str(item.get("kategori", item.get("category", sv.get("kategori", sv.get("category", ""))))).lower()

            is_shield_item = "shield" in name or "buckler" in name or "kalkan" in name or "shield" in itype or "shield" in ikategori
            is_armor_item = (
                not is_shield_item and (
                    itype in ("armor", "equipment") or 
                    any(k in ikategori for k in ("armor", "zırh", "zirh")) or
                    any(w in name for w in ("armor", "zırh", "zirh", "mail", "plate", "leather", "padded", "hide", "cuirass", "hauberk", "corset", "breastplate", "shirt", "deri", "plaka", "zincir", "pullu", "halka", "göğüslük", "gogusluk", "çivili", "civili", "kapitone"))
                )
            )

            # Process armor
            if is_armor_item:
                ac_data = (
                    sv.get("armor_class") or 
                    sv.get("armor_bonus") or 
                    sv.get("ac_bonus") or 
                    sv.get("armorClass") or 
                    sv.get("ac") or 
                    sv.get("bonus") or 
                    sys_obj.get("armor") or 
                    {}
                )
                ab_val = 0
                dm_val = None

                if isinstance(ac_data, dict):
                    ab_val = ac_data.get("value") or ac_data.get("base") or ac_data.get("ac") or 0
                    dm_val = ac_data.get("dex") or ac_data.get("max_dex")
                else:
                    try: ab_val = int(ac_data)
                    except: ab_val = 0
                
                try: ab_val = int(ab_val)
                except: ab_val = 0

                # Check max dex from sv directly if not found in ac_data
                if dm_val is None:
                    dm_val = sv.get("max_dex") or sv.get("max_dex_bonus") or sys_obj.get("max_dex")

                # Name-based fallback for PF1e Armors if ab_val is 0
                if ab_val == 0:
                    if "full plate" in name or "tam plaka" in name: ab_val, dm_val, acp_val = 9, 1, -6
                    elif "half-plate" in name or "half plate" in name or "yarım plaka" in name or "yarim plaka" in name: ab_val, dm_val, acp_val = 8, 0, -7
                    elif "splint" in name or "oluklu" in name: ab_val, dm_val, acp_val = 7, 0, -7
                    elif "banded" in name or "bantlı" in name or "bantli" in name: ab_val, dm_val, acp_val = 7, 1, -6
                    elif "chainmail" in name or "zincir zırh" in name or "zincir zirh" in name: ab_val, dm_val, acp_val = 6, 2, -5
                    elif "breastplate" in name or "göğüslük" in name or "gogusluk" in name: ab_val, dm_val, acp_val = 6, 3, -4
                    elif "scale" in name or "pullu" in name: ab_val, dm_val, acp_val = 5, 3, -4
                    elif "chain shirt" in name or "zincir gömlek" in name or "zincir gomlek" in name: ab_val, dm_val, acp_val = 4, 4, -2
                    elif "hide" in name or "kürk" in name or "post" in name: ab_val, dm_val, acp_val = 4, 4, -3
                    elif "studded" in name or "çivili" in name or "civili" in name: ab_val, dm_val, acp_val = 3, 5, -1
                    elif "leather" in name or "deri" in name: ab_val, dm_val, acp_val = 2, 6, 0
                    elif "padded" in name or "kapitone" in name or "doldurmalı" in name: ab_val, dm_val, acp_val = 1, 8, 0
                    elif "zırh" in name or "zirh" in name or "armor" in name: ab_val, dm_val, acp_val = 4, 4, -2

                if ab_val > 0:
                    armor_bonus = max(armor_bonus, ab_val)
                    if dm_val is not None:
                        try: dex_max = min(dex_max, int(dm_val))
                        except: pass
                    
                    acp_val = sv.get("check_penalty") or sv.get("armor_check_penalty") or sys_obj.get("acp") or sys_obj.get("armor", {}).get("acp")
                    if acp_val is None:
                        acp_val = sys_obj.get("check_penalty") or sys_obj.get("armor_check_penalty") or 0
                    try: acp_val = int(acp_val)
                    except: acp_val = 0
                    
                    if acp_val == 0 and ab_val >= 6:
                        acp_val = -(ab_val - 3)
                    acp = min(acp, acp_val)

            # Process shield
            if is_shield_item:
                sb_data = (
                    sv.get("shield_bonus") or 
                    sv.get("armor_class") or 
                    sv.get("ac_bonus") or 
                    sv.get("armor") or 
                    sys_obj.get("shield") or 
                    {}
                )
                if isinstance(sb_data, dict):
                    sb_val = sb_data.get("value") or sb_data.get("base") or sb_data.get("ac") or 0
                else:
                    try: sb_val = int(sb_data)
                    except: sb_val = 0
                
                try: sb_val = int(sb_val)
                except: sb_val = 0
                
                # Name-based fallback for PF1e Shields if sb_val is 0
                if sb_val == 0:
                    if "tower" in name or "kule" in name: sb_val, acp_val = 4, -10
                    elif "heavy" in name or "ağır" in name or "agir" in name: sb_val, acp_val = 2, -2
                    elif "light" in name or "hafif" in name: sb_val, acp_val = 1, -1
                    elif "buckler" in name: sb_val, acp_val = 1, -1
                    else: sb_val, acp_val = 2, -2

                shield_bonus = max(shield_bonus, sb_val)
                
                acp_val = sv.get("check_penalty") or sv.get("armor_check_penalty") or sys_obj.get("check_penalty") or sys_obj.get("acp") or 0
                try: acp_val = int(acp_val)
                except: acp_val = 0
                acp += acp_val

        return armor_bonus, shield_bonus, natural_armor, acp, dex_max

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Mevcut arayüz ile uyumluluk için — update_all_stats'a delege eder."""
        return self.update_all_stats(character)

    def eval_formula(self, formula: str, character: Dict[str, Any], derived: Dict[str, Any]) -> int:
        if not isinstance(formula, str):
            try: return int(formula)
            except: return 0
            
        f = formula.strip()
        mods = derived.get("ability_modifiers", {})
        f = f.replace("@abilities.str.mod", str(mods.get("Strength", 0)))
        f = f.replace("@abilities.dex.mod", str(mods.get("Dexterity", 0)))
        f = f.replace("@abilities.con.mod", str(mods.get("Constitution", 0)))
        f = f.replace("@abilities.int.mod", str(mods.get("Intelligence", 0)))
        f = f.replace("@abilities.wis.mod", str(mods.get("Wisdom", 0)))
        f = f.replace("@abilities.cha.mod", str(mods.get("Charisma", 0)))
        
        level = character.get("level", 1)
        f = re.sub(r'@classes\.[a-zA-Z0-9_]+\.level', str(level), f)
        
        if "?" in f and ":" in f:
            match = re.match(r'(.*?)\?(.*?):(.*?)$', f)
            if match:
                cond, val_true, val_false = match.groups()
                try:
                    cond_eval = eval(cond, {"__builtins__": None}, {})
                    f = val_true if cond_eval else val_false
                except Exception:
                    f = val_false
                    
        try:
            f_clean = re.sub(r'[^0-9+\-*/\s().]', '', f)
            return int(eval(f_clean, {"__builtins__": None}, {}))
        except Exception:
            try:
                nums = re.findall(r'-?\d+', f)
                return int(nums[0]) if nums else 0
            except Exception:
                return 0

    def apply_mechanics(self, character: Dict[str, Any], derived: Dict[str, Any]) -> None:
        active = self.get_active_mechanics(character)
        mechanics = active["mechanics"]
        
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        
        armor_bonus = 0
        shield_bonus = 0
        natural_armor = 0
        deflection_bonus = 0
        other_ac_bonus = 0
        dex_max = 999
        
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                val = self.eval_formula(val, character, derived)
                
            mode = m.get("mode", "add")
            
            m_dex_max = m.get("dex_max")
            if m_dex_max is not None:
                dex_max = min(dex_max, m_dex_max)
                
            if target == "ac":
                if mode == "armor":
                    armor_bonus += val
                elif mode == "shield":
                    shield_bonus += val
                elif mode == "natural_armor":
                    natural_armor += val
                elif mode == "deflection":
                    deflection_bonus += val
                else:
                    other_ac_bonus += val
            elif target == "hp":
                derived["hit_points"] = derived.get("hit_points", 10) + val
            elif target == "initiative":
                derived["initiative"] += val
            elif target == "bab":
                derived["bab"] += val
            elif target in ("attack_bonus", "attack"):
                derived["attack_bonus"] = derived.get("attack_bonus", 0) + val
                derived["melee_attack"] = derived.get("melee_attack", 0) + val
                derived["ranged_attack"] = derived.get("ranged_attack", 0) + val
            elif target == "speed":
                derived["speed"] = derived.get("speed", 30) + val
            elif target == "cmb":
                derived["cmb"] += val
            elif target == "cmd":
                derived["cmd"] += val
            elif target.startswith("saving_throws."):
                parts = target.split('.')
                save_type = parts[1].capitalize()
                if save_type == "All":
                    for s in derived["saving_throws"]:
                        derived["saving_throws"][s] += val
                elif save_type in derived["saving_throws"]:
                    derived["saving_throws"][save_type] += val
            elif target.startswith("skills."):
                parts = target.split('.')
                skill_name = parts[1].title()
                if skill_name in derived["skills"]:
                    derived["skills"][skill_name] += val
                    
        dex_mod = mods["dexterity"]
        dex_contrib = min(dex_mod, dex_max)
        
        size_modifier_ac = int(character.get("size_modifier_ac", 0))
        
        derived["armor_class"] = 10 + dex_contrib + armor_bonus + shield_bonus + natural_armor + deflection_bonus + other_ac_bonus + size_modifier_ac
        derived["touch_ac"] = 10 + dex_contrib + deflection_bonus + size_modifier_ac + other_ac_bonus
        derived["flat_footed_ac"] = 10 + armor_bonus + shield_bonus + natural_armor + deflection_bonus + size_modifier_ac + other_ac_bonus
        
        size_mod = int(character.get("size_modifier", 0))
        str_mod = mods["strength"]
        derived["melee_attack_bonus"] = derived["bab"] + str_mod
        derived["ranged_attack_bonus"] = derived["bab"] + dex_mod
        derived["cmb"] = derived["bab"] + str_mod - size_mod
        derived["cmd"] = 10 + derived["bab"] + str_mod + dex_contrib - size_mod + deflection_bonus



class MnM3e_Calculator(BaseCalculator):
    """Calculations engine for Mutants & Masterminds 3rd Edition.

    M&M 3e notu: Ability skorları DOĞRUDAN modifier olarak kullanılır
    (10 çıkarıp 2'ye bölme YOK — D&D/PF1e'den farklı).
    """

    MM_SKILLS: Dict[str, str] = {
        "Acrobatics":    "agility",
        "Athletics":     "strength",
        "Close Combat":  "fighting",
        "Deception":     "presence",
        "Expertise":     "intellect",
        "Insight":       "awareness",
        "Intimidation":  "presence",
        "Investigation": "intellect",
        "Perception":    "awareness",
        "Persuasion":    "presence",
        "Ranged Combat": "dexterity",
        "Sleight of Hand": "dexterity",
        "Stealth":       "agility",
        "Technology":    "intellect",
        "Treatment":     "intellect",
        "Vehicles":      "dexterity",
    }

    # ------------------------------------------------------------------ #
    # MAIN PIPELINE — update_all_stats()                                   #
    # ------------------------------------------------------------------ #

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Mevcut arayüz ile uyumluluk için — update_all_stats'a delege eder."""
        return self.update_all_stats(character)

    def update_all_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """M&M 3e — 5-step dependency-ordered calculation pipeline.

        ADIM 1: Ability Ranks → doğrudan modifier (M&M3e'de rank = modifier)
        ADIM 2: Archetype ve Power Level verisi → base defense ranks
        ADIM 3: Advantage mekanikleri → defense/skill/initiative bonusları
        ADIM 4: Ekipman/Device tarama → Toughness ve özel bonuslar
        ADIM 5: PL Defense Cap uygula (Dodge+Tough ≤ 2×PL vb.) → final yaz
        """
        derived: Dict[str, Any] = {}

        # ── ADIM 1: Ability Ranks (M&M3e: rank = modifier, 0 = normal) ─────────
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "stamina", "agility", "dexterity",
                     "fighting", "intellect", "awareness", "presence"]
        mods = {ab: int(scores.get(ab, 0)) for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): mods[ab] for ab in abilities}

        # Initiative = Agility rank (M&M3e Core, p.36)
        derived["initiative"] = mods["agility"]

        # ── ADIM 2: Power Level → base defense ranks ─────────────────────────
        pl = max(1, int(character.get("pl_value", 10)))
        derived["pl_value"] = pl
        # Archetype verisi (opsiyonel — base defense rank override)
        arch_data = character.get("class_data", {}) or character.get("archetype_data", {}) or {}

        defense_ranks = character.get("defenses", {}) or {}

        # ── ADIM 2b: Skills = Rank + Ability Modifier ──────────────────────────
        skill_ranks = character.get("skill_ranks", {}) or {}
        skills: Dict[str, int] = {}
        for sk, ab in self.MM_SKILLS.items():
            ranks = max(0, int(skill_ranks.get(sk, 0)))
            skills[sk] = ranks + mods[ab]
        derived["skills"] = skills

        # ── ADIM 3: Advantage/Power mekanikleri ─────────────────────────────
        active    = self.get_active_mechanics(character)
        mechanics = active.get("mechanics", [])

        init_bonus    = 0
        dodge_bonus   = 0
        parry_bonus   = 0
        tough_bonus   = 0
        fort_bonus    = 0
        will_bonus    = 0

        for m in mechanics:
            target = m.get("target", "")
            try:
                val = int(str(m.get("value", 0)).replace("+", "").strip())
            except (ValueError, TypeError):
                val = 0

            if target == "initiative":
                init_bonus += val
            elif target in ("dodge", "dodge_defense"):
                dodge_bonus += val
            elif target in ("parry", "parry_defense"):
                parry_bonus += val
            elif target in ("toughness", "toughness_defense"):
                tough_bonus += val
            elif target in ("fortitude", "fortitude_defense"):
                fort_bonus += val
            elif target in ("will", "will_defense"):
                will_bonus += val
            elif target.startswith("skills."):
                sk_name = target.split(".")[1].title()
                if sk_name in derived["skills"]:
                    derived["skills"][sk_name] += val

        derived["initiative"] += init_bonus

        # ── ADIM 4: Ekipman / Device tarama → Toughness bonus ────────────────
        equip_tough = 0
        for item in character.get("equipment", []):
            if not isinstance(item, dict):
                continue
            sv = item.get("sistem_verisi") or {}
            if not isinstance(sv, dict):
                sv = {}
            # Zırh / Toughness veren cihazlar
            tb = sv.get("toughness", sv.get("armor_toughness", 0))
            try:
                equip_tough += int(tb)
            except (ValueError, TypeError):
                pass

        # ── ADIM 5: Final defenses + PL cap uygula ───────────────────────────
        defenses = {
            "Dodge":      mods["agility"]  + int(defense_ranks.get("Dodge", 0))     + dodge_bonus,
            "Parry":      mods["fighting"] + int(defense_ranks.get("Parry", 0))     + parry_bonus,
            "Toughness":  mods["stamina"]  + int(defense_ranks.get("Toughness", 0)) + tough_bonus + equip_tough,
            "Fortitude":  mods["stamina"]  + int(defense_ranks.get("Fortitude", 0)) + fort_bonus,
            "Will":       mods["awareness"]+ int(defense_ranks.get("Will", 0))      + will_bonus,
        }

        # M&M 3e Power Level Defense Caps (Core Rulebook p.18)
        #   Dodge + Toughness  ≤ 2 × PL
        #   Parry + Toughness  ≤ 2 × PL
        #   Fortitude + Will   ≤ 2 × PL
        cap = 2 * pl

        toughness = defenses["Toughness"]
        if defenses["Dodge"] + toughness > cap:
            defenses["Dodge"] = max(0, cap - toughness)
        if defenses["Parry"] + toughness > cap:
            defenses["Parry"] = max(0, cap - toughness)

        fort = defenses["Fortitude"]
        will = defenses["Will"]
        if fort + will > cap:
            defenses["Will"] = max(0, cap - fort)

        derived["defenses"] = defenses
        return derived


# ===========================================================================
# ADIM 2 — BÜYÜ HESAPLAMA MOTORU (calculate_spells)
# Açık/Kapalı Prensibi: Aşağıdaki metodlar mevcut sınıflara EKLENTI olarak
# monkey-patch edilir. Hiçbir mevcut metod değiştirilmemiştir.
# ===========================================================================

def _dnd5e_calculate_spells(self, character: Dict[str, Any]) -> Dict[str, Any]:
    """D&D 5e Büyü Sistemi Hesaplayıcı (Plugin Metod).

    Döndürür:
        is_spellcaster     : bool   — karakter büyücü mü?
        spellcasting_ability: str   — INT / WIS / CHA
        spell_save_dc      : int    — 8 + prof + ability_mod
        spell_attack_bonus : int    — prof + ability_mod
        caster_type        : str    — "full" / "half" / "third" / "warlock" / "none"
        slots              : dict   — {"1": n, "2": n, ..., "9": n}  (Warlock: {"pact": n, "slot_level": k})
        known_spells       : list   — DB'den çekilen sınıf büyü listesi (ilk 30)
    """
    import sqlite3
    import json as _json

    result: Dict[str, Any] = {
        "is_spellcaster": False,
        "spellcasting_ability": "",
        "spell_save_dc": 0,
        "spell_attack_bonus": 0,
        "caster_type": "none",
        "slots": {},
        "known_spells": [],
    }

    # -- Sınıf verisi kontrolü --
    class_data = character.get("class_data") or {}
    casting_ability_raw = class_data.get("spellcasting_ability", "")
    class_name = (character.get("class", "") or "").lower()

    if not casting_ability_raw:
        # Fallback for DND5e classes without explicit spellcasting_ability
        SPELLCASTING_ABILITIES = {
            "wizard": "intelligence", "cleric": "wisdom", "druid": "wisdom",
            "bard": "charisma", "paladin": "charisma", "ranger": "wisdom",
            "sorcerer": "charisma", "warlock": "charisma", "artificer": "intelligence",
            "blood hunter": "intelligence", "eldritch knight": "intelligence",
            "arcane trickster": "intelligence"
        }
        for k, v in SPELLCASTING_ABILITIES.items():
            if k in class_name:
                casting_ability_raw = v
                break

    if not casting_ability_raw:
        return result  # Büyücü değil

    casting_ability = casting_ability_raw.lower().strip()
    result["is_spellcaster"] = True
    result["spellcasting_ability"] = casting_ability.title()

    # -- Temel hesaplar --
    level = max(1, int(character.get("level", 1)))
    scores = self.get_adjusted_abilities(character)
    ab_score = scores.get(casting_ability, 10)
    ab_mod = (ab_score - 10) // 2
    prof = 2 + (level - 1) // 4

    result["spell_save_dc"] = 8 + prof + ab_mod
    result["spell_attack_bonus"] = prof + ab_mod

    # -- Sınıf adından büyü tipi belirle --
    class_name = (character.get("class", "") or "").lower()
    WARLOCK_NAMES = {"warlock", "efendi pakti"}
    HALF_CASTERS = {"paladin", "ranger", "şövalye", "izci"}
    THIRD_CASTERS = {"eldritch knight", "arcane trickster", "büyülü şövalye", "arkan hilekâr"}

    if class_name in WARLOCK_NAMES:
        caster_type = "warlock"
    elif any(n in class_name for n in HALF_CASTERS):
        caster_type = "half"
    elif any(n in class_name for n in THIRD_CASTERS):
        caster_type = "third"
    else:
        caster_type = "full"

    result["caster_type"] = caster_type

    # -- Slot tabloları (PHB, p. 114) --
    # Tam büyücü (Wizard, Cleric, Druid, Bard, Sorcerer, vb.)
    FULL_SLOTS = {
        1:  {1: 2},
        2:  {1: 3},
        3:  {1: 4, 2: 2},
        4:  {1: 4, 2: 3},
        5:  {1: 4, 2: 3, 3: 2},
        6:  {1: 4, 2: 3, 3: 3},
        7:  {1: 4, 2: 3, 3: 3, 4: 1},
        8:  {1: 4, 2: 3, 3: 3, 4: 2},
        9:  {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
        11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
        12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
        13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
        14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
        15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
        16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
        18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
        19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
        20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
    }
    # Yarı büyücü (Paladin, Ranger — PHB p. 84, 92)
    HALF_SLOTS = {
        2:  {1: 2},
        3:  {1: 3},
        5:  {1: 4, 2: 2},
        7:  {1: 4, 2: 3},
        9:  {1: 4, 2: 3, 3: 2},
        11: {1: 4, 2: 3, 3: 3},
        13: {1: 4, 2: 3, 3: 3, 4: 1},
        15: {1: 4, 2: 3, 3: 3, 4: 2},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    }
    # Üçte bir büyücü (EK / AT)
    THIRD_SLOTS = {
        3:  {1: 2},
        7:  {1: 3},
        13: {1: 3, 2: 2},
        19: {1: 3, 2: 3, 3: 3},
    }
    # Warlock Pact Magic (PHB p. 108)
    WARLOCK_PACT = {
        1:  {"slots": 1, "level": 1},
        2:  {"slots": 2, "level": 1},
        3:  {"slots": 2, "level": 2},
        4:  {"slots": 2, "level": 2},
        5:  {"slots": 2, "level": 3},
        6:  {"slots": 2, "level": 3},
        7:  {"slots": 2, "level": 4},
        8:  {"slots": 2, "level": 4},
        9:  {"slots": 2, "level": 5},
        10: {"slots": 2, "level": 5},
        11: {"slots": 3, "level": 5},
        12: {"slots": 3, "level": 5},
        13: {"slots": 3, "level": 5},
        14: {"slots": 3, "level": 5},
        15: {"slots": 3, "level": 5},
        16: {"slots": 3, "level": 5},
        17: {"slots": 4, "level": 5},
        18: {"slots": 4, "level": 5},
        19: {"slots": 4, "level": 5},
        20: {"slots": 4, "level": 5},
    }

    if caster_type == "warlock":
        pact = WARLOCK_PACT.get(level, WARLOCK_PACT[20])
        result["slots"] = {"pact_slots": pact["slots"], "pact_slot_level": pact["level"]}
    elif caster_type == "half":
        eff_level = level // 2
        slot_table = {}
        for threshold in sorted(HALF_SLOTS.keys()):
            if level >= threshold:
                slot_table = HALF_SLOTS[threshold]
        result["slots"] = {str(k): v for k, v in slot_table.items()}
    elif caster_type == "third":
        slot_table = {}
        for threshold in sorted(THIRD_SLOTS.keys()):
            if level >= threshold:
                slot_table = THIRD_SLOTS[threshold]
        result["slots"] = {str(k): v for k, v in slot_table.items()}
    else:
        effective = min(level, 20)
        result["slots"] = {str(k): v for k, v in FULL_SLOTS.get(effective, FULL_SLOTS[20]).items()}

    # -- DB'den büyü listesi (izole spells tablosu) --
    try:
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        # Sınıf adını büyü listesiyle eşleştir (siniflar sütununda arama)
        cur.execute(
            "SELECT isim, seviye, aciklama FROM spells WHERE sistem = 'dnd5e' "
            "AND siniflar LIKE ? ORDER BY seviye, isim",
            (f"%{class_name}%",)
        )
        rows = cur.fetchall()
        conn.close()
        result["known_spells"] = [
            {"name": r[0], "level": r[1], "description": r[2] or ""}
            for r in rows
        ]
    except Exception:
        result["known_spells"] = []

    return result


def _pf1e_calculate_spells(self, character: Dict[str, Any]) -> Dict[str, Any]:
    """PF1e 1st Edition Büyü Sistemi Hesaplayıcı (Plugin Metod).

    PF2e KESİNLİKLE desteklenmez. Tüm kurallar PF1e Core Rulebook'a göredir.

    Döndürür:
        is_spellcaster        : bool
        spellcasting_ability  : str   — "Intelligence" / "Wisdom" / "Charisma"
        caster_level          : int   — CL = karakter seviyesi (prestige sınıflar hariç)
        concentration_bonus   : int   — CL + ability_mod (PF1e CRB p. 206)
        spell_save_dc_base    : int   — 10 + spell_level + ability_mod (PF1e CRB p. 218)
        casting_type          : str   — "prepared_arcane" / "prepared_divine" / "spontaneous" / "none"
        bonus_slots           : dict  — Yüksek ability'den gelen ekstra slot sayıları
                                         {1: n, 2: n, 3: n, 4: n} (PF1e CRB Table 1-3)
        known_spells          : list  — DB'den sınıf büyü listesi
    """
    import sqlite3

    result: Dict[str, Any] = {
        "is_spellcaster": False,
        "spellcasting_ability": "",
        "caster_level": 0,
        "concentration_bonus": 0,
        "spell_save_dc_base": 0,
        "casting_type": "none",
        "bonus_slots": {},
        "known_spells": [],
    }

    class_data = character.get("class_data") or {}
    casting_ability_raw = class_data.get("spellcasting_ability", "")
    if not casting_ability_raw:
        return result

    casting_ability = casting_ability_raw.lower().strip()
    result["is_spellcaster"] = True
    result["spellcasting_ability"] = casting_ability.title()

    level = max(1, int(character.get("level", 1)))
    scores = self.get_adjusted_abilities(character)
    ab_score = scores.get(casting_ability, 10)
    ab_mod = (ab_score - 10) // 2

    # CL = sınıf seviyesi (PF1e CRB: prestige ve multiclass durumları ayrı)
    caster_level = level
    result["caster_level"] = caster_level

    # Concentration = CL + casting ability modifier (PF1e CRB p. 206)
    result["concentration_bonus"] = caster_level + ab_mod

    # Temel DC = 10 + büyü seviyesi + ability mod (PF1e CRB p. 218)
    # (Büyü seviyesi arayüzde dinamik olarak eklenir; burada 0 seviye için baz)
    result["spell_save_dc_base"] = 10 + ab_mod

    # Yayınlama tipi
    class_name_raw = (character.get("class", "") or "").lower()
    PREPARED_ARCANE = {"wizard", "büyücü", "arcanist", "arkanik"}
    PREPARED_DIVINE = {"cleric", "rahip", "druid", "dürüst", "oracle"}
    if any(n in class_name_raw for n in PREPARED_ARCANE):
        casting_type = "prepared_arcane"
    elif any(n in class_name_raw for n in PREPARED_DIVINE):
        casting_type = "prepared_divine"
    else:
        casting_type = "spontaneous"
    result["casting_type"] = casting_type

    # ── Bonus Slotlar: Yüksek Ability Skoru (PF1e CRB Table 1-3) ──────────
    # Bir büyücünün ability skoru ≥ 12 ise o seviyede 1 ek slot alır.
    # ability mod 1 → bonus_slot seviye 1; mod 2 → seviye 1-2; vs.
    # Resmi formül: ability_mod >= spell_level → o seviyeye +1 slot
    bonus_slots: Dict[int, int] = {}
    max_spell_level = min(9, (caster_level + 1) // 2)  # erişilebilir max büyü seviyesi
    for sp_lv in range(1, max_spell_level + 1):
        if ab_mod >= sp_lv:
            bonus_slots[sp_lv] = 1
    result["bonus_slots"] = {str(k): v for k, v in bonus_slots.items()}

    # -- DB'den büyü listesi (izole spells tablosu) --
    try:
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute(
            "SELECT isim, seviye, aciklama FROM spells WHERE sistem = 'pathfinder1e' "
            "AND siniflar LIKE ? ORDER BY seviye, isim",
            (f"%{class_name_raw}%",)
        )
        rows = cur.fetchall()
        conn.close()
        result["known_spells"] = [
            {"name": r[0], "level": r[1], "description": r[2] or ""}
            for r in rows
        ]
    except Exception:
        result["known_spells"] = []

    return result


# -- Metodları sınıflara bağla (monkey-patch — hiçbir sınıf gövdesi değişmez) --
DND5e_Calculator.calculate_spells = _dnd5e_calculate_spells
PF1e_Calculator.calculate_spells  = _pf1e_calculate_spells

