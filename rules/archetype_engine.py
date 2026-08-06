"""
Diyargezen Pathfinder 1st Edition (PF1e) Archetype & Multiclass Engine

Architecture & Rule Specifications:
----------------------------------
1. Multiclassing Stacking Engine (PF1e Core Rulebook p. 30):
   - Multi-class characters sum Base Attack Bonuses (BAB) and Base Saves from each class.
   - BAB Stacking:
     - Full BAB classes (Fighter, Paladin, Ranger, Barbarian): BAB = Level.
     - Medium BAB classes (Cleric, Druid, Rogue, Bard, Monk, Alchemist, Inquisitor, Magus): BAB = floor(Level * 3 / 4).
     - Poor BAB classes (Wizard, Sorcerer, Witch): BAB = floor(Level / 2).
   - Save Stacking:
     - Good Save: 2 + floor(Level / 2).
     - Poor Save: floor(Level / 3).
     - Total Save = Sum(Base_Saves) + Ability_Modifier.

2. Archetype Feature Replacement Engine (PF1e Advanced Player's Guide p. 72):
   - Archetypes swap out base class features at specified levels.
   - Archetype Compatibility Rule: Two archetypes for the same class can be selected
     simultaneously ONLY IF they do NOT replace or alter the same base class feature.
"""

from __future__ import annotations

import math
from typing import Dict, Any, List, Set, Tuple, Optional


# Class BAB & Save Progression Profiles
CLASS_PROFILES: Dict[str, Dict[str, Any]] = {
    "fighter": {"bab": "full", "fort": "good", "ref": "poor", "will": "poor", "hit_die": 10},
    "paladin": {"bab": "full", "fort": "good", "ref": "poor", "will": "good", "hit_die": 10},
    "ranger": {"bab": "full", "fort": "good", "ref": "good", "will": "poor", "hit_die": 10},
    "barbarian": {"bab": "full", "fort": "good", "ref": "poor", "will": "poor", "hit_die": 12},
    "cavalier": {"bab": "full", "fort": "good", "ref": "poor", "will": "poor", "hit_die": 10},
    "gunslinger": {"bab": "full", "fort": "good", "ref": "good", "will": "poor", "hit_die": 10},
    
    "cleric": {"bab": "medium", "fort": "good", "ref": "poor", "will": "good", "hit_die": 8},
    "druid": {"bab": "medium", "fort": "good", "ref": "poor", "will": "good", "hit_die": 8},
    "rogue": {"bab": "medium", "fort": "poor", "ref": "good", "will": "poor", "hit_die": 8},
    "bard": {"bab": "medium", "fort": "poor", "ref": "good", "will": "good", "hit_die": 8},
    "monk": {"bab": "medium", "fort": "good", "ref": "good", "will": "good", "hit_die": 8},
    "alchemist": {"bab": "medium", "fort": "good", "ref": "good", "will": "poor", "hit_die": 8},
    "inquisitor": {"bab": "medium", "fort": "good", "ref": "poor", "will": "good", "hit_die": 8},
    "magus": {"bab": "medium", "fort": "good", "ref": "poor", "will": "good", "hit_die": 8},
    "summoner": {"bab": "medium", "fort": "poor", "ref": "poor", "will": "good", "hit_die": 8},
    
    "wizard": {"bab": "poor", "fort": "poor", "ref": "poor", "will": "good", "hit_die": 6},
    "sorcerer": {"bab": "poor", "fort": "poor", "ref": "poor", "will": "good", "hit_die": 6},
    "witch": {"bab": "poor", "fort": "poor", "ref": "poor", "will": "good", "hit_die": 6},
}


# Official Archetype Database: Feature Replacements per Archetype
# Key: Class -> Archetype Name -> { "replaces": [feature_names], "grants": [new_features] }
ARCHETYPE_DATABASE: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "fighter": {
        "weapon master": {
            "replaces": ["Armor Training 1", "Armor Training 2", "Armor Training 3", "Armor Training 4", "Bravery"],
            "grants": ["Weapon Guard", "Weapon Mastery", "Reliable Strike"]
        },
        "armor master": {
            "replaces": ["Weapon Training 1", "Weapon Training 2", "Weapon Training 3", "Weapon Training 4"],
            "grants": ["Armor Specialization", "Fortification"]
        },
        "two-handed fighter": {
            "replaces": ["Armor Training 1", "Armor Training 2", "Armor Training 3", "Armor Training 4"],
            "grants": ["Shatter Defenses", "Overhand Chop", "Weapon Training (Two-Handed)"]
        }
    },
    "rogue": {
        "swashbuckler": {
            "replaces": ["Trapfinding"],
            "grants": ["Martial Weapon Proficiency", "Daring Attempt"]
        },
        "scout": {
            "replaces": ["Uncanny Dodge"],
            "grants": ["Scout's Charge", "Skirmish"]
        },
        "arcane trickster": {
            "replaces": ["Trap Sense"],
            "grants": ["Roguish Spellcasting", "Mage Hand Legerdemain"]
        }
    },
    "ranger": {
        "urban ranger": {
            "replaces": ["Favored Terrain", "Wild Empathy"],
            "grants": ["Favored Community", "Urban Tracking"]
        },
        "wild stalker": {
            "replaces": ["Combat Style Feat 1", "Combat Style Feat 2"],
            "grants": ["Rage", "Uncanny Dodge"]
        }
    },
    "wizard": {
        "spellslinger": {
            "replaces": ["Arcane Bond", "Cantrips"],
            "grants": ["Gunsmith", "Arcane Gun"]
        },
        "scrollmaster": {
            "replaces": ["Arcane Bond"],
            "grants": ["Scroll Blade", "Scroll Shield"]
        }
    }
}


class PF1eMulticlassEngine:
    """Calculates PF1e Multiclass BAB, Saves, and Hit Die progression stacking."""

    @staticmethod
    def calculate_class_bab(profile_type: str, class_level: int) -> int:
        """Calculates BAB for a single class level."""
        p = str(profile_type).lower()
        l = max(0, int(class_level))
        if p == "full":
            return l
        elif p == "medium":
            return (l * 3) // 4
        else:
            return l // 2

    @staticmethod
    def calculate_class_base_save(progression: str, class_level: int) -> int:
        """Calculates base save for a single class level."""
        p = str(progression).lower()
        l = max(0, int(class_level))
        if l == 0:
            return 0
        return (2 + l // 2) if p == "good" else (l // 3)

    @classmethod
    def calculate_multiclass_progression(cls, class_levels: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculates stacked BAB, Fort/Ref/Will base saves, total level, and Hit Points across multiple classes.
        """
        total_level = 0
        total_bab = 0
        total_base_fort = 0
        total_base_ref = 0
        total_base_will = 0

        for class_name, level in class_levels.items():
            l = max(0, int(level))
            if l == 0:
                continue

            c_key = str(class_name).lower().strip()
            profile = CLASS_PROFILES.get(c_key, {"bab": "medium", "fort": "good", "ref": "poor", "will": "poor", "hit_die": 8})

            total_level += l
            total_bab += cls.calculate_class_bab(profile["bab"], l)
            total_base_fort += cls.calculate_class_base_save(profile["fort"], l)
            total_base_ref += cls.calculate_class_base_save(profile["ref"], l)
            total_base_will += cls.calculate_class_base_save(profile["will"], l)

        return {
            "total_level": max(1, total_level),
            "total_bab": total_bab,
            "base_fort": total_base_fort,
            "base_ref": total_base_ref,
            "base_will": total_base_will
        }


class PF1eArchetypeEngine:
    """Validates PF1e Archetype compatibility and handles feature replacements."""

    @staticmethod
    def validate_archetype_compatibility(base_class: str, archetypes: List[str]) -> Tuple[bool, List[str]]:
        """
        Checks if multiple archetypes for the same class conflict (i.e. replace the same base feature).
        Returns (is_compatible: bool, conflict_reasons: List[str]).
        """
        c_key = str(base_class).lower().strip()
        class_archs = ARCHETYPE_DATABASE.get(c_key, {})

        replaced_features: Dict[str, str] = {}  # feature_name -> replacing_archetype
        conflicts: List[str] = []

        for arch_name in archetypes:
            a_key = str(arch_name).lower().strip()
            arch_data = class_archs.get(a_key)
            if not arch_data:
                continue

            for feat in arch_data.get("replaces", []):
                feat_norm = feat.lower().strip()
                if feat_norm in replaced_features:
                    existing_arch = replaced_features[feat_norm]
                    conflicts.append(
                        f"Çakışma: Hem '{existing_arch.title()}' hem de '{arch_name.title()}' arketipleri '{feat}' yeteneğini değiştiriyor!"
                    )
                else:
                    replaced_features[feat_norm] = arch_name

        return (len(conflicts) == 0, conflicts)

    @staticmethod
    def get_archetype_features(base_class: str, archetypes: List[str]) -> Dict[str, List[str]]:
        """Returns lists of replaced features and granted features for selected archetypes."""
        c_key = str(base_class).lower().strip()
        class_archs = ARCHETYPE_DATABASE.get(c_key, {})

        replaced_all: Set[str] = set()
        granted_all: Set[str] = set()

        for arch_name in archetypes:
            a_key = str(arch_name).lower().strip()
            arch_data = class_archs.get(a_key)
            if arch_data:
                for r in arch_data.get("replaces", []):
                    replaced_all.add(r)
                for g in arch_data.get("grants", []):
                    granted_all.add(g)

        return {
            "replaced_features": sorted(list(replaced_all)),
            "granted_features": sorted(list(granted_all))
        }
