# tests/test_multi_system_rules.py
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
import sqlite3
import json
from models.entity import DiyargezenEntity
from parsers.base import extract_standard_mechanics, make_entity
from rules.calculators import DND5e_Calculator, PF1e_Calculator, MnM3e_Calculator
from utils.soft_validation import validate_character_soft

class TestMultiSystemRules(unittest.TestCase):
    def setUp(self):
        self.db_path = Path(__file__).resolve().parent.parent / "data" / "characters.db"

    def test_dnd5e_mechanics_extraction(self):
        # Test modifiers, requirements, bonuses parsing
        payload = {
            "name": "Heavy Plate Armor",
            "type": "equipment",
            "system": {
                "requirements": "Str 15",
                "modifiers": [
                    {"target": "ac", "mode": "armor", "value": 18, "dex_max": 0}
                ],
                "bonuses": {
                    "ac": "+1"
                }
            }
        }
        res = extract_standard_mechanics(payload, "dnd5e")
        mechanics = res["standard_mechanics"]
        prereqs = res["prerequisites"]

        # Assert requirements
        self.assertEqual(len(prereqs), 1)
        self.assertEqual(prereqs[0]["prerequisite"], "strength")
        self.assertEqual(prereqs[0]["value"], 15)

        # Assert modifiers
        self.assertEqual(len(mechanics), 2)
        ac_mod = next(m for m in mechanics if m["mode"] == "armor")
        self.assertEqual(ac_mod["target"], "ac")
        self.assertEqual(ac_mod["value"], 18)
        self.assertEqual(ac_mod["dex_max"], 0)

        bonus_mod = next(m for m in mechanics if m["mode"] == "add")
        self.assertEqual(bonus_mod["target"], "ac")
        self.assertEqual(bonus_mod["value"], 1)

    def test_pf1e_mechanics_extraction(self):
        # Test changes, prerequisites parsing
        payload = {
            "name": "Shield Bash",
            "type": "feat",
            "system": {
                "prerequisites": "Dex 13, Strength 13",
                "changes": [
                    {"target": "ac.shield", "value": "2", "operator": "shield"},
                    {"target": "ability.str", "value": "2", "operator": "add"}
                ]
            }
        }
        res = extract_standard_mechanics(payload, "pathfinder1e")
        mechanics = res["standard_mechanics"]
        prereqs = res["prerequisites"]

        # Assert prerequisites
        self.assertEqual(len(prereqs), 2)
        self.assertIn({"prerequisite": "dexterity", "value": 13}, prereqs)
        self.assertIn({"prerequisite": "strength", "value": 13}, prereqs)

        # Assert changes
        self.assertEqual(len(mechanics), 2)
        shield = next(m for m in mechanics if m["target"] == "ac")
        self.assertEqual(shield["mode"], "shield")
        self.assertEqual(shield["value"], 2)

        str_bonus = next(m for m in mechanics if m["target"] == "strength")
        self.assertEqual(str_bonus["value"], 2)

    def test_mm3e_mechanics_extraction(self):
        # Test effects, modifiers, text parsing
        payload = {
            "name": "Deflection Force",
            "type": "power",
            "description": "This power grants +4 Dodge and +2 Parry.",
            "system": {
                "effects": [
                    {"target": "toughness", "value": 3}
                ]
            }
        }
        res = extract_standard_mechanics(payload, "mm3e")
        mechanics = res["standard_mechanics"]

        # Assert effects
        self.assertTrue(any(m["target"] == "toughness" and m["value"] == 3 for m in mechanics))
        # Assert text parsing
        self.assertTrue(any(m["target"] == "dodge" and m["value"] == 4 for m in mechanics))
        self.assertTrue(any(m["target"] == "parry" and m["value"] == 2 for m in mechanics))

    def test_dnd5e_calculator_mechanics(self):
        calc = DND5e_Calculator(db_path=self.db_path)
        # 10 baseline Dex, has Heavy Plate Armor (Str 15 required)
        char = {
            "system": "dnd5e",
            "abilities": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "level": 1,
            "equipment": [
                {
                    "name": "Plate Armor",
                    "sistem_verisi": {
                        "standard_mechanics": [
                            {"target": "ac", "mode": "armor", "value": 18, "dex_max": 0}
                        ]
                    }
                }
            ]
        }
        derived = calc.calculate(char)
        # Heavy armor Dex cap is 0 -> AC is exactly 18
        self.assertEqual(derived["armor_class"], 18)

    def test_pf1e_calculator_mechanics_and_formulas(self):
        calc = PF1e_Calculator(db_path=self.db_path)
        char = {
            "system": "pathfinder1e",
            "abilities": {
                "strength": 14,
                "dexterity": 18,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "level": 1,
            "feats": [
                {
                    "name": "Graceful Strike",
                    "sistem_verisi": {
                        "standard_mechanics": [
                            {"target": "ac", "mode": "add", "value": "@abilities.dex.mod > @abilities.str.mod ? 2 : 0"}
                        ]
                    }
                }
            ]
        }
        derived = calc.calculate(char)
        # Dex mod is 4, Str mod is 2. Formula resolves to 2. Base AC is 10 + 4 (Dex) + 2 (formula) = 16.
        self.assertEqual(derived["armor_class"], 16)

    def test_pf1e_encumbrance_and_carrying_capacity(self):
        calc = PF1e_Calculator(db_path=self.db_path)
        # Str 14: Light <= 58 lbs, Medium 59..116 lbs, Heavy 117..175 lbs
        char_light = {
            "system": "pathfinder1e",
            "abilities": {"strength": 14, "dexterity": 14},
            "equipment": [{"name": "Light Pack", "weight": 30.0, "quantity": 1}]
        }
        derived_light = calc.calculate(char_light)
        self.assertEqual(derived_light["encumbrance"]["status"], "Light Load")
        self.assertEqual(derived_light["total_weight"], 30.0)
        self.assertEqual(derived_light["speed"], 30)

        char_medium = {
            "system": "pathfinder1e",
            "abilities": {"strength": 14, "dexterity": 18},
            "equipment": [{"name": "Heavy Gear", "weight": 80.0, "quantity": 1}]
        }
        derived_medium = calc.calculate(char_medium)
        self.assertEqual(derived_medium["encumbrance"]["status"], "Medium Load")
        self.assertEqual(derived_medium["speed"], 20)
        self.assertEqual(derived_medium["armor_check_penalty"], -3)


    def test_mm3e_calculator_defense_caps(self):
        calc = MnM3e_Calculator(db_path=self.db_path)
        # Power level 10 -> Cap is 20
        char = {
            "system": "mm3e",
            "pl_value": 10,
            "abilities": {
                "agility": 12,    # Dodge = 12
                "fighting": 10,   # Parry = 10
                "stamina": 12,    # Toughness = 12
            },
            "defenses": {
                "Dodge": 0,
                "Parry": 0,
                "Toughness": 0
            }
        }
        derived = calc.calculate(char)
        # Agility 12 + Stamina 12 = 24. Capped to 20 -> Dodge capped to 8.
        self.assertEqual(derived["defenses"]["Dodge"], 8)
        self.assertEqual(derived["defenses"]["Toughness"], 12)

    def test_soft_validation_prerequisites(self):
        # Strength 10, but feat Shield Bash requires Str 13
        char = {
            "system": "dnd5e",
            "abilities": {
                "strength": 10,
                "dexterity": 14,
            },
            "feats": [
                {
                    "name": "Shield Bash",
                    "sistem_verisi": {
                        "prerequisites": [
                            {"prerequisite": "strength", "value": 13}
                        ]
                    }
                }
            ]
        }
        # Clear database path validation
        res = validate_character_soft(char, "dnd5e")
        self.assertTrue(res.has_warnings)
        self.assertTrue(any("gereksinimi karşılanamadı" in w for w in res.warnings))

    def test_pf1e_trait_bonuses(self):
        calc = PF1e_Calculator(db_path=self.db_path)
        char = {
            "system": "pathfinder1e",
            "level": 1,
            "abilities": {
                "strength": 10,
                "dexterity": 14,    # Mod +2
                "constitution": 12, # Mod +1
                "intelligence": 10, # Mod 0
                "wisdom": 10,       # Mod 0
                "charisma": 14      # Mod +2
            },
            "class_data": {
                "name": "Wizard",   # Class skills do not normally include Diplomacy
                "class_skills": ["Spellcraft", "Knowledge (Arcana)"],
                "saving_throws": {"fortitude": "poor", "reflex": "poor", "will": "good"},
                "hit_die": "d6"
            },
            "skill_ranks": {
                "Diplomacy": 1
            },
            "traits": [
                {
                    "name": "Reactionary",
                    "sistem_verisi": {
                        "trait_category": "Combat",
                        "bonuses": [{"type": "initiative", "value": 2, "bonus_type": "untyped"}]
                    }
                },
                {
                    "name": "Resilient",
                    "sistem_verisi": {
                        "trait_category": "Combat",
                        "bonuses": [{"type": "save_fortitude", "value": 1, "bonus_type": "trait"}]
                    }
                },
                {
                    "name": "Ease of Faith",
                    "sistem_verisi": {
                        "trait_category": "Faith",
                        "bonuses": [{"type": "skill", "skill": "Diplomacy", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]
                    }
                }
            ]
        }
        derived = calc.update_all_stats(char)
        # Initiative: Dex mod (+2) + Reactionary (+2) = 4
        self.assertEqual(derived["initiative"], 4)

        # Fortitude Save: Wizard Lvl 1 Poor (0) + Con mod (+1) + Resilient (+1) = 2
        self.assertEqual(derived["saving_throws"]["Fortitude"], 2)

        # Diplomacy Skill: 1 rank + Cha mod (+2) + Class skill bonus (+3, granted by Ease of Faith) + Trait bonus (+1) = 7
        self.assertEqual(derived["skills"]["diplomacy"], 7)

