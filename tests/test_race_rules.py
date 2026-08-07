import unittest
from rules.calculators import PF1e_Calculator
from utils.soft_validation import validate_pf1e_soft

class TestRaceRules(unittest.TestCase):
    def setUp(self):
        self.calc = PF1e_Calculator()

    def test_dwarf_negative_charisma_modifier(self):
        char = {
            "system": "pathfinder1e",
            "race": "Dwarf",
            "class": "Fighter",
            "level": 1,
            "abilities": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }
        res = self.calc.calculate(char)
        abilities = res["ability_scores"]
        # Dwarf has +2 CON, +2 WIS, -2 CHA
        self.assertEqual(abilities["Constitution"], 12)
        self.assertEqual(abilities["Wisdom"], 12)
        self.assertEqual(abilities["Charisma"], 8)

    def test_elf_negative_constitution_modifier(self):
        char = {
            "system": "pathfinder1e",
            "race": "Elf",
            "class": "Wizard",
            "level": 1,
            "abilities": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }
        res = self.calc.calculate(char)
        abilities = res["ability_scores"]
        # Elf has +2 DEX, +2 INT, -2 CON
        self.assertEqual(abilities["Dexterity"], 12)
        self.assertEqual(abilities["Intelligence"], 12)
        self.assertEqual(abilities["Constitution"], 8)

    def test_alternate_racial_trait_mutual_exclusion(self):
        # Craftman replaces Greed, Lorekeeper replaces Greed
        char = {
            "system": "pathfinder1e",
            "race": "Dwarf",
            "race_data": {
                "sistem_verisi": {
                    "alternate_traits": [
                        {"name": "Craftsman", "replaces": ["Greed"]},
                        {"name": "Lorekeeper", "replaces": ["Greed"]}
                    ]
                }
            },
            "selected_racial_traits": ["Craftsman", "Lorekeeper"]
        }
        val_res = validate_pf1e_soft(char)
        self.assertTrue(val_res.has_warnings)
        self.assertTrue(any("Greed" in w for w in val_res.warnings))

if __name__ == "__main__":
    unittest.main()
