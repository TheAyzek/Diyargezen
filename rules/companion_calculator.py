"""
Diyargezen Pathfinder 1st Edition Companion & Familiar Rules Engine

Architecture & Rule Specifications:
----------------------------------
This module implements official Pathfinder 1st Edition progression math for:
1. Animal Companions (PF1e Core Rulebook p. 52, Table 3-8):
   - Effective Druid Level (EDL) calculation based on class:
     - Druid, Hunter, Sacred Huntsmaster: 100% of Class Level.
     - Ranger: Class Level - 3 (min 1).
     - Paladin / Cavalier (Mount): 100% of Class Level.
   - Stats progression scaling by EDL (Hit Dice 1d8 to 16d8, BAB +0 to +12,
     Fort/Ref saves, Natural Armor +0 to +12, Str/Dex Bonus +0 to +6,
     Bonus Tricks 1 to 7, Special Abilities like Link, Share Spells, Evasion, Devotion, Multiattack, Improved Evasion).

2. Familiars (PF1e Core Rulebook p. 82, Table 3-9):
   - Master Level (Wizard, Witch, Sorcerer, Arcanist).
   - Familiar HD = Master Level.
   - Familiar HP = 50% of Master's Max HP.
   - Natural Armor Bonus = +1 per 2 Master Levels (+1 at lvl 1 to +10 at lvl 19).
   - Familiar Intelligence = 6 + floor(Master Level / 2) (max 15).
   - Master Stat Bonuses:
     - Toad: +3 Max HP to Master
     - Cat: +3 Stealth to Master
     - Raven: +3 Appraise to Master
     - Bat: +3 Fly to Master
     - Viper: +3 Bluff to Master
     - Owl: +3 Perception in dim light to Master
     - Weasel: +2 Reflex Save to Master
     - Compsognathus: +4 Initiative to Master
     - Greensting Scorpion: +4 Initiative to Master
     - Thrush: +3 Diplomacy to Master
     - Bluejay: +3 Knowledge (local) to Master
"""

from __future__ import annotations

import math
from typing import Dict, Any, List, Optional


# PF1e Animal Companion Progression Table (CRB p. 52, Table 3-8)
# Key: Effective Druid Level (1-20) -> { hd, bab, fort_ref, will, nat_armor, str_dex_adj, bonus_tricks, special }
ANIMAL_COMPANION_TABLE: Dict[int, Dict[str, Any]] = {
    1:  {"hd": 2,  "bab": 1,  "fort_ref": 3, "will": 0, "nat_armor": 0,  "str_dex": 0, "tricks": 1, "special": ["Link", "Share Spells"]},
    2:  {"hd": 3,  "bab": 2,  "fort_ref": 3, "will": 1, "nat_armor": 0,  "str_dex": 0, "tricks": 1, "special": ["Evasion"]},
    3:  {"hd": 3,  "bab": 2,  "fort_ref": 3, "will": 1, "nat_armor": 2,  "str_dex": 1, "tricks": 2, "special": []},
    4:  {"hd": 4,  "bab": 3,  "fort_ref": 4, "will": 1, "nat_armor": 2,  "str_dex": 1, "tricks": 2, "special": ["Ability Score Increase"]},
    5:  {"hd": 5,  "bab": 3,  "fort_ref": 4, "will": 1, "nat_armor": 4,  "str_dex": 2, "tricks": 3, "special": []},
    6:  {"hd": 6,  "bab": 4,  "fort_ref": 5, "will": 2, "nat_armor": 4,  "str_dex": 2, "tricks": 3, "special": ["Devotion"]},
    7:  {"hd": 6,  "bab": 4,  "fort_ref": 5, "will": 2, "nat_armor": 6,  "str_dex": 3, "tricks": 4, "special": []},
    8:  {"hd": 7,  "bab": 5,  "fort_ref": 5, "will": 2, "nat_armor": 6,  "str_dex": 3, "tricks": 4, "special": []},
    9:  {"hd": 8,  "bab": 6,  "fort_ref": 6, "will": 2, "nat_armor": 8,  "str_dex": 4, "tricks": 5, "special": ["Multiattack", "Ability Score Increase"]},
    10: {"hd": 9,  "bab": 6,  "fort_ref": 6, "will": 3, "nat_armor": 8,  "str_dex": 4, "tricks": 5, "special": []},
    11: {"hd": 9,  "bab": 6,  "fort_ref": 6, "will": 3, "nat_armor": 10, "str_dex": 5, "tricks": 6, "special": []},
    12: {"hd": 10, "bab": 7,  "fort_ref": 7, "will": 3, "nat_armor": 10, "str_dex": 5, "tricks": 6, "special": []},
    13: {"hd": 11, "bab": 8,  "fort_ref": 7, "will": 3, "nat_armor": 12, "str_dex": 6, "tricks": 7, "special": []},
    14: {"hd": 12, "bab": 9,  "fort_ref": 8, "will": 4, "nat_armor": 12, "str_dex": 6, "tricks": 7, "special": ["Ability Score Increase"]},
    15: {"hd": 12, "bab": 9,  "fort_ref": 8, "will": 4, "nat_armor": 14, "str_dex": 7, "tricks": 8, "special": ["Improved Evasion"]},
    16: {"hd": 13, "bab": 9,  "fort_ref": 8, "will": 4, "nat_armor": 14, "str_dex": 7, "tricks": 8, "special": []},
    17: {"hd": 14, "bab": 10, "fort_ref": 9, "will": 4, "nat_armor": 16, "str_dex": 8, "tricks": 9, "special": []},
    18: {"hd": 15, "bab": 11, "fort_ref": 9, "will": 5, "nat_armor": 16, "str_dex": 8, "tricks": 9, "special": []},
    19: {"hd": 15, "bab": 11, "fort_ref": 9, "will": 5, "nat_armor": 18, "str_dex": 9, "tricks": 10, "special": ["Ability Score Increase"]},
    20: {"hd": 16, "bab": 12, "fort_ref": 10, "will": 5, "nat_armor": 18, "str_dex": 9, "tricks": 10, "special": []}
}


# Master bonuses granted by Familiars (PF1e CRB p. 82)
FAMILIAR_MASTER_BONUSES: Dict[str, Dict[str, Any]] = {
    "toad": {"target": "hp", "value": 3, "reason": "Familiar Bonusu (Toad +3 HP)"},
    "kurbağa": {"target": "hp", "value": 3, "reason": "Familiar Bonusu (Kurbağa +3 HP)"},
    "cat": {"target": "skill:Stealth", "value": 3, "reason": "Familiar Bonusu (Cat +3 Stealth)"},
    "kedi": {"target": "skill:Stealth", "value": 3, "reason": "Familiar Bonusu (Kedi +3 Stealth)"},
    "raven": {"target": "skill:Appraise", "value": 3, "reason": "Familiar Bonusu (Raven +3 Appraise)"},
    "kuzgun": {"target": "skill:Appraise", "value": 3, "reason": "Familiar Bonusu (Kuzgun +3 Appraise)"},
    "bat": {"target": "skill:Fly", "value": 3, "reason": "Familiar Bonusu (Bat +3 Fly)"},
    "yarasa": {"target": "skill:Fly", "value": 3, "reason": "Familiar Bonusu (Yarasa +3 Fly)"},
    "viper": {"target": "skill:Bluff", "value": 3, "reason": "Familiar Bonusu (Viper +3 Bluff)"},
    "engerek": {"target": "skill:Bluff", "value": 3, "reason": "Familiar Bonusu (Engerek +3 Bluff)"},
    "owl": {"target": "skill:Perception", "value": 3, "reason": "Familiar Bonusu (Owl +3 Perception)"},
    "baykuş": {"target": "skill:Perception", "value": 3, "reason": "Familiar Bonusu (Baykuş +3 Perception)"},
    "weasel": {"target": "saving_throws.Reflex", "value": 2, "reason": "Familiar Bonusu (Weasel +2 Reflex)"},
    "gelincik": {"target": "saving_throws.Reflex", "value": 2, "reason": "Familiar Bonusu (Gelincik +2 Reflex)"},
    "compsognathus": {"target": "initiative", "value": 4, "reason": "Familiar Bonusu (Compsognathus +4 Init)"},
    "greensting scorpion": {"target": "initiative", "value": 4, "reason": "Familiar Bonusu (Scorpion +4 Init)"},
    "akrep": {"target": "initiative", "value": 4, "reason": "Familiar Bonusu (Akrep +4 Init)"},
    "thrush": {"target": "skill:Diplomacy", "value": 3, "reason": "Familiar Bonusu (Thrush +3 Diplomacy)"},
    "bluejay": {"target": "skill:Knowledge (local)", "value": 3, "reason": "Familiar Bonusu (Bluejay +3 Know Local)"}
}


class PF1eCompanionCalculator:
    """Calculates PF1e Companion & Familiar derived statistics and master bonuses."""

    @staticmethod
    def calculate_effective_druid_level(char_class: str, char_level: int) -> int:
        """Calculates Effective Druid Level (EDL) based on class."""
        cls_lower = str(char_class or "").lower().strip()
        lvl = max(1, int(char_level or 1))

        if "ranger" in cls_lower:
            return max(1, lvl - 3)
        return lvl

    @staticmethod
    def calculate_animal_companion(companion_data: Dict[str, Any], master_class: str, master_level: int) -> Dict[str, Any]:
        """
        Calculates animal companion scaled stats (HD, HP, AC, BAB, Saves, Str/Dex, Tricks, Special).
        """
        edl = PF1eCompanionCalculator.calculate_effective_druid_level(master_class, master_level)
        row = ANIMAL_COMPANION_TABLE.get(min(20, max(1, edl)), ANIMAL_COMPANION_TABLE[1])

        base_str = int(companion_data.get("str", 13))
        base_dex = int(companion_data.get("dex", 15))
        base_con = int(companion_data.get("con", 15))
        base_int = int(companion_data.get("int", 2))
        base_wis = int(companion_data.get("wis", 12))
        base_cha = int(companion_data.get("cha", 6))

        str_dex_adj = row["str_dex"]
        total_str = base_str + str_dex_adj
        total_dex = base_dex + str_dex_adj
        con_mod = (base_con - 10) // 2
        dex_mod = (total_dex - 10) // 2

        hd = row["hd"]
        # HP: 4.5 average per d8 HD + con_mod * HD
        hp = math.floor(hd * 4.5) + (con_mod * hd)
        # Natural armor + base 10 + dex_mod + preset AC bonus
        preset_ac_bonus = int(companion_data.get("acBonus", 2))
        total_ac = 10 + row["nat_armor"] + dex_mod + preset_ac_bonus

        # Accumulate special abilities from level 1 to edl
        accumulated_specials = []
        for lvl_idx in range(1, min(20, max(1, edl)) + 1):
            for sp in ANIMAL_COMPANION_TABLE[lvl_idx]["special"]:
                if sp not in accumulated_specials:
                    accumulated_specials.append(sp)

        return {
            "name": companion_data.get("name", "Yoldaş"),
            "species": companion_data.get("species", "Animal Companion"),
            "effective_druid_level": edl,
            "hd": f"{hd}d8",
            "hd_count": hd,
            "hp": max(1, hp),
            "ac": total_ac,
            "natural_armor_bonus": row["nat_armor"],
            "bab": row["bab"],
            "formatted_bab": f"+{row['bab']}",
            "fort_save": row["fort_ref"] + con_mod,
            "ref_save": row["fort_ref"] + dex_mod,
            "will_save": row["will"] + ((base_wis - 10) // 2),
            "str": total_str,
            "dex": total_dex,
            "con": base_con,
            "int": base_int,
            "wis": base_wis,
            "cha": base_cha,
            "bonus_tricks": row["tricks"],
            "special_abilities": accumulated_specials,
            "attacks": companion_data.get("attacks", "Doğal Saldırı"),
            "notes": companion_data.get("notes", "")
        }

    @staticmethod
    def calculate_familiar(familiar_data: Dict[str, Any], master_level: int, master_max_hp: int) -> Dict[str, Any]:
        """
        Calculates familiar scaled stats (HD, HP, AC, Intelligence, Special Abilities).
        """
        lvl = min(20, max(1, int(master_level or 1)))
        preset_key = str(familiar_data.get("presetKey", "")).lower()

        nat_armor_bonus = max(1, math.floor((lvl + 1) / 2))
        dex_val = int(familiar_data.get("dex", 15))
        dex_mod = (dex_val - 10) // 2
        total_ac = 10 + nat_armor_bonus + dex_mod

        fam_int = min(15, 6 + math.floor(lvl / 2))
        fam_hp = max(1, math.floor(master_max_hp * 0.5))

        specials = ["Alertness", "Empathic Link", "Share Spells"]
        if lvl >= 3: specials.append("Deliver Touch Spells")
        if lvl >= 5: specials.append("Speak with Master")
        if lvl >= 7: specials.append("Speak with Animals of its Kind")
        if lvl >= 11: specials.append("Spell Resistance")

        master_bonus = FAMILIAR_MASTER_BONUSES.get(preset_key)

        return {
            "name": familiar_data.get("name", "Familiar"),
            "species": familiar_data.get("species", "Familiar"),
            "master_level": lvl,
            "hd": f"{lvl}d8",
            "hp": fam_hp,
            "ac": total_ac,
            "natural_armor_bonus": nat_armor_bonus,
            "str": familiar_data.get("str", 3),
            "dex": dex_val,
            "con": familiar_data.get("con", 8),
            "int": fam_int,
            "wis": familiar_data.get("wis", 12),
            "cha": familiar_data.get("cha", 7),
            "special_abilities": specials,
            "master_bonus": master_bonus,
            "notes": familiar_data.get("notes", "")
        }
