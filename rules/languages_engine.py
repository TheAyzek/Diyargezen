"""
Pathfinder 1st Edition Languages & Linguistics Engine
=====================================================
References:
- PF1e Core Rulebook p. 65 (Starting Languages & Bonus Languages)
- PF1e Core Rulebook p. 100 (Linguistics Skill Rules)

Mechanics:
- Automatic Languages: Free starting languages granted by race.
- Bonus Languages: Characters with positive INT modifier can select up to INT mod additional languages from their racial list.
- Linguistics Skill: Each rank invested in Linguistics grants 1 additional language of choice.
- Total Allowed Languages = Automatic Count + max(0, INT mod) + Linguistics Ranks.
- Druidic is a secret language reserved exclusively for Druids.
"""

from typing import Dict, Any, List, Optional, Set


OFFICIAL_PF1E_LANGUAGES: Dict[str, Dict[str, str]] = {
    "Common": {"alphabet": "Common", "type": "standard", "speakers": "Humans, trade, general populace"},
    "Elven": {"alphabet": "Elven", "type": "standard", "speakers": "Elves, half-elves"},
    "Dwarven": {"alphabet": "Dwarven", "type": "standard", "speakers": "Dwarves"},
    "Gnome": {"alphabet": "Dwarven", "type": "standard", "speakers": "Gnomes"},
    "Halfling": {"alphabet": "Common", "type": "standard", "speakers": "Halflings"},
    "Orc": {"alphabet": "Dwarven", "type": "standard", "speakers": "Orcs, half-orcs"},
    "Sylvan": {"alphabet": "Elven", "type": "standard", "speakers": "Fey, plant creatures"},
    "Abyssal": {"alphabet": "Infernal", "type": "planar", "speakers": "Demons, evil outsiders"},
    "Aquan": {"alphabet": "Aquan", "type": "elemental", "speakers": "Water elementals"},
    "Auran": {"alphabet": "Auran", "type": "elemental", "speakers": "Air elementals"},
    "Celestial": {"alphabet": "Celestial", "type": "planar", "speakers": "Angels, good outsiders"},
    "Draconic": {"alphabet": "Draconic", "type": "ancient", "speakers": "Dragons, reptilian humanoids"},
    "Giant": {"alphabet": "Dwarven", "type": "standard", "speakers": "Giants, ogres, trolls"},
    "Gnoll": {"alphabet": "Common", "type": "standard", "speakers": "Gnolls"},
    "Goblin": {"alphabet": "Dwarven", "type": "standard", "speakers": "Goblins, hobgoblins, bugbears"},
    "Ignan": {"alphabet": "Ignan", "type": "elemental", "speakers": "Fire elementals"},
    "Infernal": {"alphabet": "Infernal", "type": "planar", "speakers": "Devils, evil outsiders"},
    "Terran": {"alphabet": "Dwarven", "type": "elemental", "speakers": "Earth elementals"},
    "Undercommon": {"alphabet": "Elven", "type": "underground", "speakers": "Drow, subterranean races"},
    "Druidic": {"alphabet": "Druidic", "type": "secret", "speakers": "Druids exclusively"},
}


RACE_LANGUAGES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "human": {
        "automatic": ["Common"],
        "bonus": ["Any (except secret)"]
    },
    "elf": {
        "automatic": ["Common", "Elven"],
        "bonus": ["Celestial", "Draconic", "Gnoll", "Gnome", "Goblin", "Orc", "Sylvan"]
    },
    "dwarf": {
        "automatic": ["Common", "Dwarven"],
        "bonus": ["Giant", "Gnome", "Goblin", "Orc", "Terran", "Undercommon"]
    },
    "gnome": {
        "automatic": ["Common", "Gnome", "Sylvan"],
        "bonus": ["Draconic", "Dwarven", "Elven", "Giant", "Goblin", "Orc"]
    },
    "half-elf": {
        "automatic": ["Common", "Elven"],
        "bonus": ["Any (except secret)"]
    },
    "half-orc": {
        "automatic": ["Common", "Orc"],
        "bonus": ["Abyssal", "Draconic", "Giant", "Gnoll", "Goblin"]
    },
    "halfling": {
        "automatic": ["Common", "Halfling"],
        "bonus": ["Dwarven", "Elven", "Gnome", "Goblin"]
    }
}


def normalize_race_key(race: str) -> str:
    """Normalizes race name (handling Turkish and English variants)."""
    r = (race or "").lower().strip().replace(" ", "-").replace("i̇", "i")
    TURKISH_RACE_MAP = {
        "insan": "human", "yarim-elf": "half-elf", "yarım-elf": "half-elf",
        "yarim-ork": "half-orc", "yarım-ork": "half-orc", "cuce": "dwarf", "cüce": "dwarf",
        "bucukluk": "halfling", "buçukluk": "halfling", "gnom": "gnome"
    }
    return TURKISH_RACE_MAP.get(r, r)


def get_languages_catalog() -> Dict[str, Any]:
    """Returns official languages catalog and race starter configurations."""
    return {
        "languages": OFFICIAL_PF1E_LANGUAGES,
        "race_configurations": RACE_LANGUAGES_REGISTRY
    }


def evaluate_character_languages(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates character's starting, bonus, and linguistics languages.
    Validates against quotas and secret language restrictions.
    """
    char_race = str(character.get("race", "Human")).strip()
    r_key = normalize_race_key(char_race)
    char_class = str(character.get("class", "Fighter")).strip().lower()

    # Determine Intelligence Modifier
    abilities = character.get("abilities") or character.get("ability_scores") or {}
    int_score = 10
    for k, v in abilities.items():
        if str(k).lower().strip() == "intelligence":
            try:
                int_score = int(v)
            except (ValueError, TypeError):
                int_score = 10
            break
    int_mod = (int_score - 10) // 2

    # Determine Linguistics Skill Ranks
    skill_ranks = character.get("skill_ranks") or character.get("skills") or {}
    ling_ranks = 0
    for k, v in skill_ranks.items():
        if str(k).lower().strip() == "linguistics":
            try:
                if isinstance(v, dict):
                    ling_ranks = int(v.get("ranks", 0))
                else:
                    ling_ranks = int(v)
            except (ValueError, TypeError):
                ling_ranks = 0
            break

    # Get race configs
    race_config = RACE_LANGUAGES_REGISTRY.get(r_key, RACE_LANGUAGES_REGISTRY["human"])
    automatic_langs: List[str] = list(race_config["automatic"])
    bonus_pool: List[str] = list(race_config["bonus"])

    bonus_slots = max(0, int_mod)
    ling_slots = max(0, ling_ranks)
    total_allowed = len(automatic_langs) + bonus_slots + ling_slots

    # Parse selected languages
    raw_langs = character.get("languages", [])
    selected_set: Set[str] = set()

    if isinstance(raw_langs, str):
        # Comma-separated string
        for part in raw_langs.split(","):
            p = part.strip()
            if p:
                selected_set.add(p.title())
    elif isinstance(raw_langs, list):
        for item in raw_langs:
            if isinstance(item, str) and item.strip():
                selected_set.add(item.strip().title())
            elif isinstance(item, dict) and item.get("name"):
                selected_set.add(str(item["name"]).strip().title())

    # Ensure automatic languages are always included
    for auto in automatic_langs:
        selected_set.add(auto.title())

    all_selected_sorted = sorted(list(selected_set))

    # Warnings & Validation
    warnings = []
    is_druid = "druid" in char_class

    for lang in all_selected_sorted:
        if lang == "Druidic" and not is_druid:
            warnings.append("Druidic dili yalnızca Druid sınıfı tarafından öğrenilebilir.")

    if len(all_selected_sorted) > total_allowed:
        diff = len(all_selected_sorted) - total_allowed
        warnings.append(f"İzin verilen dil kotası aşıldı ({len(all_selected_sorted)} / {total_allowed}, +{diff} fazla dil).")

    unallocated_slots = max(0, total_allowed - len(all_selected_sorted))
    formatted_string = ", ".join(all_selected_sorted)

    return {
        "race": char_race,
        "class": char_class.title(),
        "int_modifier": int_mod,
        "linguistics_ranks": ling_ranks,
        "automatic_languages": automatic_langs,
        "bonus_language_pool": bonus_pool,
        "bonus_slots": bonus_slots,
        "linguistics_slots": ling_slots,
        "total_allowed_languages": total_allowed,
        "total_selected_languages": len(all_selected_sorted),
        "unallocated_slots": unallocated_slots,
        "selected_languages": all_selected_sorted,
        "formatted_string": formatted_string,
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }
