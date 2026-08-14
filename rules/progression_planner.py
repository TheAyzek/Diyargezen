"""
Pathfinder 1st Edition Level-Up Progression Planner (1-20)
===========================================================
References:
- PF1e Core Rulebook Chapter 3 (Table 3-1: Character Advancement and Level-Dependent Benefits)
- PF1e Core Rulebook Chapter 4 (Classes Progression Tables)

Progression Rules:
- Feats: 1st, 3rd, 5th, 7th, 9th, 11th, 13th, 15th, 17th, 19th level (+1 at 1st for Humans).
- Ability Score Increases: 4th, 8th, 12th, 16th, 20th level (+1 to any ability score).
- BAB: Full (+1/lvl), 3/4 (+0.75/lvl), 1/2 (+0.5/lvl).
- Base Saves: Good (2 + lvl/2), Poor (lvl/3).
"""

from typing import Dict, Any, List, Optional


CLASS_PROFILES: Dict[str, Dict[str, Any]] = {
    "fighter": {
        "bab_type": "full",
        "good_saves": ["fort"],
        "hit_die": 10,
        "spell_type": None,
        "bonus_feat_levels": [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "bonus_feat_type": "Bonus Combat Feat",
        "features": {
            1: ["Bonus Combat Feat"],
            2: ["Bonus Combat Feat", "Bravery +1"],
            3: ["Armor Training 1"],
            4: ["Bonus Combat Feat"],
            5: ["Weapon Training 1"],
            6: ["Bonus Combat Feat", "Bravery +2"],
            7: ["Armor Training 2"],
            8: ["Bonus Combat Feat"],
            9: ["Weapon Training 2"],
            10: ["Bonus Combat Feat", "Bravery +3"],
            11: ["Armor Training 3"],
            12: ["Bonus Combat Feat"],
            13: ["Weapon Training 3"],
            14: ["Bonus Combat Feat", "Bravery +4"],
            15: ["Armor Training 4"],
            16: ["Bonus Combat Feat"],
            17: ["Weapon Training 4"],
            18: ["Bonus Combat Feat", "Bravery +5"],
            19: ["Armor Mastery"],
            20: ["Bonus Combat Feat", "Weapon Mastery"]
        }
    },
    "wizard": {
        "bab_type": "half",
        "good_saves": ["will"],
        "hit_die": 6,
        "spell_type": "9_level",
        "bonus_feat_levels": [5, 10, 15, 20],
        "bonus_feat_type": "Metamagic or Item Creation Feat",
        "features": {
            1: ["Arcane Bond", "Arcane School", "Cantrips", "Scribe Scroll"],
            2: [],
            3: [],
            4: [],
            5: ["Bonus Feat (Metamagic/Item)"],
            6: [],
            7: [],
            8: ["School Power 2"],
            9: [],
            10: ["Bonus Feat (Metamagic/Item)"],
            11: [],
            12: [],
            13: [],
            14: [],
            15: ["Bonus Feat (Metamagic/Item)"],
            16: [],
            17: [],
            18: [],
            19: [],
            20: ["Bonus Feat (Metamagic/Item)", "True Name / Immortality"]
        }
    },
    "rogue": {
        "bab_type": "three_quarter",
        "good_saves": ["ref"],
        "hit_die": 8,
        "spell_type": None,
        "bonus_feat_levels": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "bonus_feat_type": "Rogue Talent",
        "features": {
            1: ["Sneak Attack +1d6", "Trapfinding"],
            2: ["Evasion", "Rogue Talent"],
            3: ["Sneak Attack +2d6", "Trap Sense +1"],
            4: ["Rogue Talent", "Uncanny Dodge"],
            5: ["Sneak Attack +3d6"],
            6: ["Rogue Talent", "Trap Sense +2"],
            7: ["Sneak Attack +4d6"],
            8: ["Improved Uncanny Dodge", "Rogue Talent"],
            9: ["Sneak Attack +5d6", "Trap Sense +3"],
            10: ["Advanced Talents", "Rogue Talent"],
            11: ["Sneak Attack +6d6"],
            12: ["Rogue Talent", "Trap Sense +4"],
            13: ["Sneak Attack +7d6"],
            14: ["Rogue Talent"],
            15: ["Sneak Attack +8d6", "Trap Sense +5"],
            16: ["Rogue Talent"],
            17: ["Sneak Attack +9d6"],
            18: ["Rogue Talent", "Trap Sense +6"],
            19: ["Sneak Attack +10d6"],
            20: ["Master Strike", "Rogue Talent"]
        }
    },
    "cleric": {
        "bab_type": "three_quarter",
        "good_saves": ["fort", "will"],
        "hit_die": 8,
        "spell_type": "9_level",
        "bonus_feat_levels": [],
        "bonus_feat_type": "",
        "features": {
            1: ["Aura", "Channel Energy 1d6", "Domains (2)", "Spells", "Spontaneous Casting"],
            2: [],
            3: ["Channel Energy 2d6"],
            4: [],
            5: ["Channel Energy 3d6"],
            6: [],
            7: ["Channel Energy 4d6"],
            8: ["Domain Powers 2"],
            9: ["Channel Energy 5d6"],
            10: [],
            11: ["Channel Energy 6d6"],
            12: [],
            13: ["Channel Energy 7d6"],
            14: [],
            15: ["Channel Energy 8d6"],
            16: [],
            17: ["Channel Energy 9d6"],
            18: [],
            19: ["Channel Energy 10d6"],
            20: ["Channel Energy 10d6 Max", "Holy/Unholy Apotheosis"]
        }
    },
    "barbarian": {
        "bab_type": "full",
        "good_saves": ["fort"],
        "hit_die": 12,
        "spell_type": None,
        "bonus_feat_levels": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "bonus_feat_type": "Rage Power",
        "features": {
            1: ["Fast Movement +10 ft", "Rage"],
            2: ["Rage Power", "Uncanny Dodge"],
            3: ["Trap Sense +1"],
            4: ["Rage Power"],
            5: ["Improved Uncanny Dodge"],
            6: ["Rage Power", "Trap Sense +2"],
            7: ["Damage Reduction 1/-"],
            8: ["Rage Power"],
            9: ["Trap Sense +3"],
            10: ["Damage Reduction 2/-", "Rage Power"],
            11: ["Greater Rage"],
            12: ["Rage Power", "Trap Sense +4"],
            13: ["Damage Reduction 3/-"],
            14: ["Rage Power"],
            15: ["Trap Sense +5"],
            16: ["Damage Reduction 4/-", "Rage Power"],
            17: ["Tireless Rage"],
            18: ["Rage Power", "Trap Sense +6"],
            19: ["Damage Reduction 5/-"],
            20: ["Mighty Rage", "Rage Power"]
        }
    },
    "paladin": {
        "bab_type": "full",
        "good_saves": ["fort", "will"],
        "hit_die": 10,
        "spell_type": "4_level",
        "bonus_feat_levels": [3, 6, 9, 12, 15, 18],
        "bonus_feat_type": "Mercy",
        "features": {
            1: ["Aura of Good", "Detect Evil", "Smite Evil 1/day"],
            2: ["Divine Grace", "Lay on Hands"],
            3: ["Aura of Courage", "Divine Health", "Mercy"],
            4: ["Channel Positive Energy", "Smite Evil 2/day", "Spells (1st Lv)"],
            5: ["Divine Bond"],
            6: ["Mercy"],
            7: ["Smite Evil 3/day"],
            8: ["Spells (2nd Lv)"],
            9: ["Mercy"],
            10: ["Smite Evil 4/day"],
            11: ["Aura of Justice", "Spells (3rd Lv)"],
            12: ["Mercy"],
            13: ["Smite Evil 5/day"],
            14: ["Spells (4th Lv)"],
            15: ["Mercy"],
            16: ["Smite Evil 6/day"],
            17: ["Aura of Righteousness"],
            18: ["Mercy"],
            19: ["Smite Evil 7/day"],
            20: ["Holy Champion"]
        }
    }
}


def calculate_bab(bab_type: str, level: int) -> int:
    """Calculates Base Attack Bonus for a given level."""
    if bab_type == "full":
        return level
    elif bab_type == "three_quarter":
        return (level * 3) // 4
    else: # half
        return level // 2


def format_bab_attacks(bab: int) -> str:
    """Formats iterative attacks e.g. 16 -> +16/+11/+6/+1."""
    if bab <= 0:
        return "+0"
    attacks = []
    curr = bab
    while curr > 0:
        attacks.append(f"+{curr}")
        curr -= 5
    return "/".join(attacks)


def calculate_save(is_good: bool, level: int) -> int:
    """Calculates base saving throw value."""
    if is_good:
        return 2 + (level // 2)
    else:
        return level // 3


def get_max_spell_level(spell_type: Optional[str], level: int) -> int:
    """Calculates highest accessible spell level for a caster."""
    if not spell_type:
        return 0
    if spell_type == "9_level":
        # 1st at lv 1, 2nd at 3, 3rd at 5, 4th at 7, 5th at 9, 6th at 11, 7th at 13, 8th at 15, 9th at 17
        return min(9, (level + 1) // 2)
    elif spell_type == "6_level":
        # 1st at lv 1, 2nd at 4, 3rd at 7, 4th at 10, 5th at 13, 6th at 16
        if level < 1: return 0
        return min(6, 1 + (level - 1) // 3)
    elif spell_type == "4_level":
        # 1st at lv 4, 2nd at 7, 3rd at 10, 4th at 13
        if level < 4: return 0
        return min(4, 1 + (level - 4) // 3)
    return 0


def generate_progression_matrix(
    char_class: str = "Fighter",
    race: str = "Human",
    archetype: str = ""
) -> List[Dict[str, Any]]:
    """
    Generates complete 1..20 character progression roadmap matrix.
    """
    c_key = (char_class or "Fighter").lower().strip()
    profile = CLASS_PROFILES.get(c_key, CLASS_PROFILES["fighter"])

    is_human = (race or "Human").lower().strip() == "human"
    matrix = []

    for lvl in range(1, 21):
        bab = calculate_bab(profile["bab_type"], lvl)
        bab_str = format_bab_attacks(bab)

        fort_good = "fort" in profile["good_saves"]
        ref_good = "ref" in profile["good_saves"]
        will_good = "will" in profile["good_saves"]

        fort_val = calculate_save(fort_good, lvl)
        ref_val = calculate_save(ref_good, lvl)
        will_val = calculate_save(will_good, lvl)

        has_ability_boost = lvl in [4, 8, 12, 16, 20]
        has_general_feat = (lvl % 2 == 1) # 1, 3, 5, 7, 9, 11, 13, 15, 17, 19
        is_human_bonus_feat = (lvl == 1 and is_human)

        # Bonus feats from class
        bonus_feats = []
        if lvl in profile.get("bonus_feat_levels", []):
            bonus_feats.append(profile.get("bonus_feat_type", "Bonus Feat"))

        # Features
        class_features = profile.get("features", {}).get(lvl, [])
        max_spell = get_max_spell_level(profile.get("spell_type"), lvl)

        matrix.append({
            "level": lvl,
            "bab": bab,
            "bab_formatted": bab_str,
            "fort_save": fort_val,
            "ref_save": ref_val,
            "will_save": will_val,
            "has_ability_boost": has_ability_boost,
            "has_general_feat": has_general_feat,
            "is_human_bonus_feat": is_human_bonus_feat,
            "bonus_feats": bonus_feats,
            "class_features": class_features,
            "max_spell_level": max_spell,
            "fcb_benefit": "+1 HP veya +1 Yetenek Puanı"
        })

    return matrix
