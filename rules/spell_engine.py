"""
Pathfinder 1st Edition (PF1e) Spellcasting Engine
===================================================
PF1e büyü mekanikleri, bonus slotlar, DC hesaplamaları ve sınıf büyü yönetimi.
"""

import math
from typing import Dict, Any, List, Optional

# Primary casting ability for PF1e classes
CLASS_CASTING_ABILITIES: Dict[str, str] = {
    "wizard": "intelligence",
    "sorcerer": "charisma",
    "cleric": "wisdom",
    "druid": "wisdom",
    "bard": "charisma",
    "paladin": "charisma",
    "ranger": "wisdom",
    "magus": "intelligence",
    "alchemist": "intelligence",
    "witch": "intelligence",
    "oracle": "charisma",
    "inquisitor": "wisdom",
    "summoner": "charisma",
    "arcanist": "intelligence",
    "bloodrager": "charisma",
    "shaman": "wisdom",
}

# Base spell slot progression per class type
# 9-level casters (Wizard, Cleric, Druid, Sorcerer, Witch, Oracle, Arcanist)
FULL_CASTER_SLOTS: Dict[int, Dict[int, int]] = {
    1: {0: 3, 1: 1},
    2: {0: 4, 1: 2},
    3: {0: 4, 1: 2, 2: 1},
    4: {0: 4, 1: 3, 2: 2},
    5: {0: 4, 1: 3, 2: 2, 3: 1},
    6: {0: 4, 1: 3, 2: 3, 3: 2},
    7: {0: 4, 1: 4, 2: 3, 3: 2, 4: 1},
    8: {0: 4, 1: 4, 2: 3, 3: 3, 4: 2},
    9: {0: 4, 1: 4, 2: 4, 3: 3, 4: 2, 5: 1},
    10: {0: 4, 1: 4, 2: 4, 3: 3, 4: 3, 5: 2},
    11: {0: 4, 1: 4, 2: 4, 3: 4, 4: 3, 5: 2, 6: 1},
    12: {0: 4, 1: 4, 2: 4, 3: 4, 4: 3, 5: 3, 6: 2},
    13: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 3, 6: 2, 7: 1},
    14: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 3, 6: 3, 7: 2},
    15: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3, 7: 2, 8: 1},
    16: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3, 7: 3, 8: 2},
    17: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 2, 9: 1},
    18: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 3, 9: 2},
    19: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 3, 9: 3},
    20: {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4},
}

# 6-level casters (Bard, Magus, Alchemist, Inquisitor, Summoner)
MID_CASTER_SLOTS: Dict[int, Dict[int, int]] = {
    1: {0: 4, 1: 1},
    2: {0: 5, 1: 2},
    3: {0: 5, 1: 3},
    4: {0: 6, 1: 3, 2: 1},
    5: {0: 6, 1: 4, 2: 2},
    6: {0: 6, 1: 4, 2: 3},
    7: {0: 6, 1: 4, 2: 3, 3: 1},
    8: {0: 6, 1: 4, 2: 4, 3: 2},
    9: {0: 6, 1: 5, 2: 4, 3: 3},
    10: {0: 6, 1: 5, 2: 4, 3: 3, 4: 1},
    11: {0: 6, 1: 5, 2: 5, 3: 4, 4: 2},
    12: {0: 6, 1: 5, 2: 5, 3: 4, 4: 3},
    13: {0: 6, 1: 5, 2: 5, 3: 4, 4: 3, 5: 1},
    14: {0: 6, 1: 5, 2: 5, 3: 4, 4: 4, 5: 2},
    15: {0: 6, 1: 5, 2: 5, 3: 5, 4: 4, 5: 3},
    16: {0: 6, 1: 5, 2: 5, 3: 5, 4: 4, 5: 3, 6: 1},
    17: {0: 6, 1: 5, 2: 5, 3: 5, 4: 4, 5: 4, 6: 2},
    18: {0: 6, 1: 5, 2: 5, 3: 5, 4: 5, 5: 4, 6: 3},
    19: {0: 6, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 4},
    20: {0: 6, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5},
}


def get_casting_ability_for_class(class_name: str) -> Optional[str]:
    """Return primary casting ability score name (intelligence, wisdom, charisma) for class."""
    return CLASS_CASTING_ABILITIES.get(class_name.strip().lower())


def calculate_bonus_spell_slots(ability_score: int) -> Dict[int, int]:
    """
    Calculate PF1e bonus spell slots per day for spell levels 1..9 based on primary ability score.
    PF1e Rule: Score >= 10 + L required.
    Bonus slots for level L = math.ceil((modifier - L + 1) / 4) if modifier >= L else 0.
    """
    modifier = (ability_score - 10) // 2
    bonus_slots: Dict[int, int] = {}
    if modifier < 1:
        return bonus_slots

    for spell_lvl in range(1, 10):
        if ability_score < 10 + spell_lvl:
            continue
        if modifier >= spell_lvl:
            slots = math.ceil((modifier - spell_lvl + 1) / 4)
            if slots > 0:
                bonus_slots[spell_lvl] = slots

    return bonus_slots


def calculate_spell_save_dc(spell_level: int, casting_ability_modifier: int, misc_bonus: int = 0) -> int:
    """Calculate Save DC for a spell: 10 + Spell Level + Casting Ability Modifier + Misc Bonuses."""
    return 10 + spell_level + casting_ability_modifier + misc_bonus


def get_base_spell_slots(class_name: str, class_level: int) -> Dict[int, int]:
    """Get base spell slots per day for a class at a given level."""
    cn = class_name.strip().lower()
    cl = max(1, min(20, class_level))

    if cn in ("wizard", "cleric", "druid", "sorcerer", "witch", "oracle", "arcanist", "shaman"):
        return FULL_CASTER_SLOTS.get(cl, {}).copy()
    elif cn in ("bard", "magus", "alchemist", "inquisitor", "summoner"):
        return MID_CASTER_SLOTS.get(cl, {}).copy()
    elif cn in ("paladin", "ranger", "bloodrager"):
        # 4-level casters starting at level 4
        if cl < 4:
            return {}
        lvl_idx = cl - 3
        # Use adjusted mid caster scale for 4-level casters
        base = MID_CASTER_SLOTS.get(lvl_idx, {})
        return {lvl: count for lvl, count in base.items() if 1 <= lvl <= 4}

    return {}


def calculate_total_spell_slots(class_name: str, class_level: int, ability_score: int) -> Dict[int, int]:
    """Combine base class spell slots with bonus ability score slots."""
    base_slots = get_base_spell_slots(class_name, class_level)
    if not base_slots:
        return {}

    bonus_slots = calculate_bonus_spell_slots(ability_score)
    total_slots = base_slots.copy()

    for lvl, count in bonus_slots.items():
        if lvl in total_slots:
            total_slots[lvl] += count
        elif lvl <= max(base_slots.keys(), default=0):
            total_slots[lvl] = count

    return total_slots


def validate_spell_prerequisites(
    spell: Dict[str, Any],
    character: Dict[str, Any],
    is_overridden: bool = False
) -> Dict[str, Any]:
    """
    Check if a character meets prerequisites to learn/cast a spell.
    Returns {"valid": bool, "reasons": List[str], "is_overridden": bool}
    """
    if is_overridden:
        return {"valid": True, "reasons": ["[GM İZNİ] Kural ezildi (Override)"], "is_overridden": True}

    reasons: List[str] = []
    char_class = character.get("class", "").strip()
    char_level = character.get("level", 1)
    abilities = character.get("abilities", {})

    # Match class casting ability
    casting_ability = get_casting_ability_for_class(char_class) or "intelligence"
    ability_score = abilities.get(casting_ability) or abilities.get(casting_ability.title(), 10)

    # Determine spell level for character class
    levels_by_class = spell.get("levels_by_class", {})
    spell_level = spell.get("level")

    if isinstance(levels_by_class, dict) and char_class:
        # Check case-insensitive class match in levels_by_class
        matched_lvl = None
        for cname, lvl in levels_by_class.items():
            if cname.lower() == char_class.lower():
                matched_lvl = lvl
                break
        if matched_lvl is not None:
            spell_level = matched_lvl

    if spell_level is None:
        spell_level = 0

    # 1. Ability Score check: Ability score must be >= 10 + spell_level
    min_ability = 10 + spell_level
    if ability_score < min_ability:
        reasons.append(f"{char_class} için {casting_ability.title()} puanı en az {min_ability} olmalıdır (Mevcut: {ability_score}).")

    # 2. Maximum spell level check for character level
    total_slots = calculate_total_spell_slots(char_class, char_level, ability_score)
    max_accessible_lvl = max(total_slots.keys(), default=0) if total_slots else 0

    if spell_level > max_accessible_lvl and spell_level > 0:
        reasons.append(f"{char_level}. seviye {char_class} henüz {spell_level}. seviye büyüleri kullanamaz (Maksimum: {max_accessible_lvl}. Seviye).")

    valid = len(reasons) == 0
    return {"valid": valid, "reasons": reasons, "is_overridden": False}
