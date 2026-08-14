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
        },
        "tower shield specialist": {
            "replaces": ["Armor Training 1", "Armor Training 2", "Armor Training 3", "Armor Training 4", "Weapon Training 1"],
            "grants": ["Tower Shield Defense", "Tower Shield Specialist", "Tower Shield Evasion"]
        },
        "mutation warrior": {
            "replaces": ["Armor Training 1", "Armor Training 2", "Armor Training 3", "Armor Training 4", "Armor Mastery"],
            "grants": ["Mutagen", "Mutagen Discoveries"]
        },
        "trench fighter": {
            "replaces": ["Armor Training 1", "Armor Training 2", "Armor Training 3", "Armor Training 4"],
            "grants": ["Firearm Training", "Trench Warfare"]
        },
        "dragoon": {
            "replaces": ["Bravery", "Weapon Training 1", "Armor Training 1", "Armor Training 2"],
            "grants": ["Spear Fighter", "Spinning Lance", "Banner Charge"]
        }
    },
    "rogue": {
        "knife master": {
            "replaces": ["Trapfinding"],
            "grants": ["Hidden Blade", "Sneak Stab (d8/d4)"]
        },
        "scout": {
            "replaces": ["Uncanny Dodge"],
            "grants": ["Scout's Charge", "Skirmish"]
        },
        "swashbuckler": {
            "replaces": ["Trapfinding"],
            "grants": ["Martial Weapon Proficiency", "Daring Attempt"]
        },
        "sniper": {
            "replaces": ["Trapfinding"],
            "grants": ["Accuracy", "Deadly Range"]
        },
        "underground chemist": {
            "replaces": ["Evasion", "Rogue Talent 4"],
            "grants": ["Chemical Weapons", "Precise Thrower"]
        },
        "rake": {
            "replaces": ["Trapfinding"],
            "grants": ["Bravado's Blade", "Rake's Smile"]
        },
        "acrobat": {
            "replaces": ["Trapfinding", "Trap Sense"],
            "grants": ["Expert Acrobat", "Second Chance"]
        },
        "arcane trickster": {
            "replaces": ["Trap Sense"],
            "grants": ["Roguish Spellcasting", "Mage Hand Legerdemain"]
        }
    },
    "wizard": {
        "spellslinger": {
            "replaces": ["Arcane Bond", "Cantrips", "Bonus Feats 5"],
            "grants": ["Gunsmith", "Arcane Gun", "Mage Bullets"]
        },
        "scrollmaster": {
            "replaces": ["Arcane Bond", "Bonus Feats 5"],
            "grants": ["Scroll Blade", "Scroll Shield"]
        },
        "arcane bomber": {
            "replaces": ["Arcane Bond", "Cantrips"],
            "grants": ["Bomb 1d6", "Bomb Discoveries", "Explosion Specialty"]
        },
        "exploiter wizard": {
            "replaces": ["Arcane School", "Arcane Bond"],
            "grants": ["Arcane Reservoir", "Arcanist Exploits"]
        }
    },
    "cleric": {
        "crusader": {
            "replaces": ["Domain 2", "Spells per Day"],
            "grants": ["Bonus Combat Feats", "Legion's Blessing"]
        },
        "evangelist": {
            "replaces": ["Channel Energy", "Armor Proficiency Medium", "Shield Proficiency"],
            "grants": ["Sermon", "Inspire Courage", "Spontaneous Casting (Enchantment)"]
        },
        "undead lord": {
            "replaces": ["Domain 2"],
            "grants": ["Undead Companion", "Corpse Companion"]
        },
        "theologian": {
            "replaces": ["Domain 2"],
            "grants": ["Focused Domain", "Domain Secret"]
        },
        "cloistered cleric": {
            "replaces": ["Armor Proficiency Medium", "Armor Proficiency Heavy", "Shield Proficiency"],
            "grants": ["Lore Lorekeeper", "Verbal Spellcasting"]
        }
    },
    "barbarian": {
        "urban barbarian": {
            "replaces": ["Fast Movement", "Damage Reduction"],
            "grants": ["Controlled Rage", "Crowd Control"]
        },
        "titan mauler": {
            "replaces": ["Fast Movement", "Trap Sense"],
            "grants": ["Big Game Hunter", "Jotungrip", "Massive Weapons"]
        },
        "invulnerable rager": {
            "replaces": ["Uncanny Dodge", "Improved Uncanny Dodge"],
            "grants": ["Damage Reduction (Heavy)", "Extreme Endurance"]
        },
        "hurler": {
            "replaces": ["Fast Movement"],
            "grants": ["Long Hurler", "Powerful Throw"]
        },
        "mad dog": {
            "replaces": ["Trap Sense", "Damage Reduction"],
            "grants": ["War Beast Companion", "Pack Tactics", "Ferocious Fetch"]
        },
        "savage technologist": {
            "replaces": ["Fast Movement", "Trap Sense"],
            "grants": ["Sword and Gun", "Rage (Strength + Dexterity)"]
        }
    },
    "bard": {
        "archaeologist": {
            "replaces": ["Bardic Performance", "Inspire Courage", "Inspire Competence"],
            "grants": ["Archaeologist's Luck", "Clever Explorer", "Uncanny Dodge"]
        },
        "dervish dancer": {
            "replaces": ["Bardic Performance", "Inspire Competence"],
            "grants": ["Dervish Dance", "Fleet", "Dance of Fury"]
        },
        "sound striker": {
            "replaces": ["Inspire Competence", "Suggestion"],
            "grants": ["Word of Strike", "Weird Words"]
        },
        "court bard": {
            "replaces": ["Inspire Courage", "Inspire Competence"],
            "grants": ["Satire", "Mockery", "Glorious Presence"]
        },
        "magician": {
            "replaces": ["Inspire Courage", "Inspire Competence"],
            "grants": ["Dweomercraft", "Expanded Spell Repertory"]
        }
    },
    "druid": {
        "menhir savant": {
            "replaces": ["Nature Sense", "Wild Empathy", "Woodland Stride"],
            "grants": ["Spirit Sense", "Place of Power", "Walk the Lines"]
        },
        "tempest druid": {
            "replaces": ["Nature Sense", "Wild Shape"],
            "grants": ["Storm Shield", "Wind Walker", "Tempest Form"]
        },
        "mooncaller": {
            "replaces": ["Venom Immunity", "A Thousand Faces"],
            "grants": ["Night Sight", "Purity of Body", "Moon Shape"]
        },
        "nature fang": {
            "replaces": ["Wild Shape"],
            "grants": ["Studied Target", "Slayer Talents", "Sneak Attack"]
        },
        "blight druid": {
            "replaces": ["Nature Sense", "Woodland Stride"],
            "grants": ["Miasma", "Blighted Blood", "Plaguebearer"]
        }
    },
    "monk": {
        "zen archer": {
            "replaces": ["Flurry of Blows", "Stunning Fist", "Evasion"],
            "grants": ["Flurry of Bows", "Perfect Strike", "Zen Archery (Wis to Attack)"]
        },
        "master of many styles": {
            "replaces": ["Flurry of Blows"],
            "grants": ["Fuse Style", "Bonus Style Feats"]
        },
        "tetori": {
            "replaces": ["Flurry of Blows", "Fast Movement"],
            "grants": ["Graceful Grappler", "Snatch and Squeeze", "Inescapable Grasp"]
        },
        "sohei": {
            "replaces": ["Stunning Fist", "Evasion", "Fast Movement"],
            "grants": ["Weapon Training (Sohei)", "Devoted Mount", "Ki Weapon Flurry"]
        },
        "qinggong monk": {
            "replaces": ["Slow Fall", "Wholeness of Body", "Diamond Body"],
            "grants": ["Qinggong Ki Powers", "Spell-Like Abilities"]
        }
    },
    "paladin": {
        "hospitaler": {
            "replaces": ["Smite Evil 2", "Smite Evil 4", "Smite Evil 6"],
            "grants": ["Healing Hands", "Separate Channel Energy Pool"]
        },
        "divine hunter": {
            "replaces": ["Heavy Armor Proficiency", "Aura of Courage"],
            "grants": ["Ranged Smite", "Distant Mercy", "Aura of Protection (Ranged)"]
        },
        "sacred shield": {
            "replaces": ["Smite Evil"],
            "grants": ["Bastion of Good", "Holy Shield", "Aura of Protection (Shield)"]
        },
        "undead scourge": {
            "replaces": ["Aura of Resolve"],
            "grants": ["Smite Undead", "Aura of Life"]
        },
        "warrior of the holy light": {
            "replaces": ["Spellcasting"],
            "grants": ["Power of Light", "Shining Light", "Aura of Brilliant Light"]
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
        },
        "falconer": {
            "replaces": ["Hunter's Bond"],
            "grants": ["Falcon Companion", "Feathered Ally"]
        },
        "freebooter": {
            "replaces": ["Favored Enemy"],
            "grants": ["Freebooter's Bane", "Freebooter's Bond"]
        },
        "skirmisher": {
            "replaces": ["Spellcasting"],
            "grants": ["Hunter's Tricks", "Skirmish Actions"]
        },
        "guide": {
            "replaces": ["Favored Enemy", "Favored Terrain"],
            "grants": ["Ranger's Focus", "Inspired Wayfinding"]
        }
    },
    "sorcerer": {
        "crossblooded": {
            "replaces": ["Bloodline Arcana", "Bloodline Feats"],
            "grants": ["Dual Bloodline Powers", "Crossblooded Spells"]
        },
        "wildblooded": {
            "replaces": ["Bloodline Power 1"],
            "grants": ["Mutated Bloodline Power"]
        },
        "tattooed sorcerer": {
            "replaces": ["Bloodline Power 1"],
            "grants": ["Familiar Tattoo", "Mage's Tattoo", "Enhanced Varisian Magic"]
        }
    },
    "alchemist": {
        "vivisectionist": {
            "replaces": ["Bomb 1d6", "Bomb Discoveries"],
            "grants": ["Sneak Attack", "Torturer's Eye", "Cruel Anatomist"]
        },
        "grenadier": {
            "replaces": ["Brew Potion", "Poison Resistance"],
            "grants": ["Martial Weapon Proficiency", "Alchemical Weapon", "Directed Blast"]
        },
        "mindchemist": {
            "replaces": ["Mutagen"],
            "grants": ["Cognatogen", "Perfect Recall"]
        },
        "chirurgeon": {
            "replaces": ["Poison Resistance"],
            "grants": ["Infused Curative", "Anaesthetic"]
        },
        "beastmorph": {
            "replaces": ["Poison Resistance", "Poison Immunity"],
            "grants": ["Beastform Mutagen", "Beastform Wings"]
        }
    },
    "inquisitor": {
        "sanctified slayer": {
            "replaces": ["Judgment"],
            "grants": ["Studied Target", "Sneak Attack", "Slayer Talents"]
        },
        "monster tactician": {
            "replaces": ["Judgment"],
            "grants": ["Summon Monster", "Tactical Teamwork"]
        },
        "preacher": {
            "replaces": ["Solo Tactics"],
            "grants": ["Determination", "Guiding Words"]
        },
        "infiltrator": {
            "replaces": ["Monster Lore", "Stern Gaze"],
            "grants": ["Misdirection", "Guile"]
        }
    },
    "magus": {
        "bladebound": {
            "replaces": ["Arcane Pool (Size)", "Magus Arcana 3"],
            "grants": ["Black Blade", "Strike of the Blade"]
        },
        "eldritch archer": {
            "replaces": ["Spell Combat", "Spellstrike"],
            "grants": ["Ranged Spell Combat", "Ranged Spellstrike"]
        },
        "kensai": {
            "replaces": ["Armor Proficiency Light", "Armor Proficiency Medium", "Armor Proficiency Heavy", "Spell Recall"],
            "grants": ["Canny Defense (Int to AC)", "Weapon Focus", "Perfect Strike", "Critical Perfection"]
        },
        "hextracker": {
            "replaces": ["Magus Arcana 3"],
            "grants": ["Witch Hex", "Accursed Strike"]
        },
        "staff magus": {
            "replaces": ["Medium Armor Proficiency", "Heavy Armor Proficiency"],
            "grants": ["Quarterstaff Defense", "Staff Weapon"]
        }
    },
    "gunslinger": {
        "pistolero": {
            "replaces": ["Gun Training 1"],
            "grants": ["Pistol Training", "Pistolero's Deed"]
        },
        "musket master": {
            "replaces": ["Gun Training 1"],
            "grants": ["Musket Training", "Fast Musket Reload"]
        },
        "mysterious stranger": {
            "replaces": ["Grit (Wisdom)"],
            "grants": ["Stranger's Grit (Charisma)", "Focused Aim"]
        },
        "gun tank": {
            "replaces": ["Nimble 1", "Nimble 2", "Nimble 3"],
            "grants": ["Armor Training (Gunslinger)", "Shield Defense"]
        }
    },
    "cavalier": {
        "gendarme": {
            "replaces": ["Tactician", "Greater Tactician", "Master Tactician"],
            "grants": ["Bonus Combat Feats", "Transfixing Charge"]
        },
        "beast rider": {
            "replaces": ["Mount (Standard)"],
            "grants": ["Exotic Mount", "Monstrous Steed"]
        },
        "strategist": {
            "replaces": ["Cavalier's Charge"],
            "grants": ["Tactician Master", "Drill Instructor"]
        }
    },
    "witch": {
        "gravewalker": {
            "replaces": ["Witch's Familiar"],
            "grants": ["Poppet Familiar", "Aura of Desecration", "Command Undead"]
        },
        "hedge witch": {
            "replaces": ["Hex 4", "Hex 8"],
            "grants": ["Spontaneous Healing", "Empathic Touch"]
        },
        "winter witch": {
            "replaces": ["Hex 4"],
            "grants": ["Ice Magic", "Cold Hexes", "Freeze"]
        }
    },
    "summoner": {
        "synthesist": {
            "replaces": ["Summon Monster", "Life Link"],
            "grants": ["Fused Eidolon", "Fused Link", "Shielded Meld"]
        },
        "master summoner": {
            "replaces": ["Eidolon Power (Half HD)"],
            "grants": ["Expanded Summon Monster", "Multiple Summons"]
        },
        "broodmaster": {
            "replaces": ["Eidolon (Single)"],
            "grants": ["Brood Eidolons (Multiple Smaller)"]
        }
    },
    "oracle": {
        "dual-cursed oracle": {
            "replaces": ["Class Skills", "Mystery Spells 2"],
            "grants": ["Dual Curse", "Misfortune", "Fortune"]
        },
        "ancient lorekeeper": {
            "replaces": ["Bonus Spells"],
            "grants": ["Elven Lore", "Arcane Spells in Divine Slots"]
        },
        "spirit guide": {
            "replaces": ["Mystery Revelations 3", "Mystery Revelations 7"],
            "grants": ["Shaman Spirits", "Spirit Magic"]
        }
    },
    "slayer": {
        "bounty hunter": {
            "replaces": ["Slayer Talent 2"],
            "grants": ["Submission Hold", "Incapacitating Strike"]
        },
        "executioner": {
            "replaces": ["Stalker"],
            "grants": ["Focused Execution", "Assassination Strike"]
        },
        "stygian slayer": {
            "replaces": ["Medium Armor Proficiency", "Shield Proficiency"],
            "grants": ["Invisibility", "Shadowy Disguise", "Mist Form"]
        }
    },
    "swashbuckler": {
        "inspired blade": {
            "replaces": ["Panache (Charisma)", "Swashbuckler Finesse"],
            "grants": ["Inspired Panache (Int + Cha)", "Rapier Finesse", "Rapier Weapon Focus"]
        },
        "musketeer": {
            "replaces": ["Swashbuckler Finesse"],
            "grants": ["Firearm Proficiency", "Gunsmithing", "Rapid Reload"]
        },
        "mysterious avenger": {
            "replaces": ["Swashbuckler Weapon Training"],
            "grants": ["Avenger's Disguise", "Whip Finesse"]
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
    def get_available_archetypes(base_class: str) -> List[str]:
        """Returns list of all official archetype names registered for a base class."""
        c_key = str(base_class).lower().strip()
        class_archs = ARCHETYPE_DATABASE.get(c_key, {})
        return [name.title() for name in class_archs.keys()]

    @staticmethod
    def validate_archetype_compatibility(base_class: str, archetypes: Any) -> Tuple[bool, List[str]]:
        """
        Checks if multiple archetypes for the same class conflict (i.e. replace the same base feature).
        Returns (is_compatible: bool, conflict_reasons: List[str]).
        """
        if isinstance(archetypes, str):
            archetypes = [archetypes] if archetypes.strip() else []
        elif not isinstance(archetypes, (list, tuple, set)):
            archetypes = []

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
                        f"Çakışma: Hem '{existing_arch.title()}' hem de '{str(arch_name).title()}' arketipleri '{feat}' yeteneğini değiştiriyor!"
                    )
                else:
                    replaced_features[feat_norm] = str(arch_name)

        return (len(conflicts) == 0, conflicts)

    @staticmethod
    def get_archetype_features(base_class: str, archetypes: Any) -> Dict[str, List[str]]:
        """Returns lists of replaced features and granted features for selected archetypes."""
        if isinstance(archetypes, str):
            archetypes = [archetypes] if archetypes.strip() else []
        elif not isinstance(archetypes, (list, tuple, set)):
            archetypes = []

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

