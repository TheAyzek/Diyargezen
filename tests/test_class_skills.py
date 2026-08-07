import unittest
from rules.calculators import PF1e_Calculator

class TestPF1eClassSkills(unittest.TestCase):
    def setUp(self):
        self.calc = PF1e_Calculator()

    def test_fighter_class_skills_and_plus3_bonus(self):
        """Fighter class skills get +3 bonus when ranks >= 1, but 0 when ranks == 0."""
        character = {
            "system": "pathfinder1e",
            "class": "Fighter",
            "level": 1,
            "ability_scores": {"strength": 14, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            "skills": {
                "Climb": 1,        # Class skill for Fighter (+3 bonus)
                "Intimidate": 0,   # Class skill for Fighter, but 0 ranks (0 bonus)
                "Spellcraft": 1,   # Non-class skill for Fighter (0 bonus)
            }
        }
        res = self.calc.update_all_stats(character)
        skills_detail = res["skills_detail"]

        # Climb (Class Skill with 1 rank, STR mod +2): 1 + 2 + 3 = 6
        self.assertTrue(skills_detail["Climb"]["is_class_skill"])
        self.assertEqual(skills_detail["Climb"]["class_bonus"], 3)
        self.assertEqual(skills_detail["Climb"]["total"], 6)

        # Intimidate (Class Skill with 0 ranks, CHA mod +0): 0 + 0 + 0 = 0
        self.assertTrue(skills_detail["Intimidate"]["is_class_skill"])
        self.assertEqual(skills_detail["Intimidate"]["class_bonus"], 0)
        self.assertEqual(skills_detail["Intimidate"]["total"], 0)

        # Spellcraft (Non-class Skill with 1 rank, INT mod +0): 1 + 0 + 0 = 1
        self.assertFalse(skills_detail["Spellcraft"]["is_class_skill"])
        self.assertEqual(skills_detail["Spellcraft"]["class_bonus"], 0)
        self.assertEqual(skills_detail["Spellcraft"]["total"], 1)

    def test_knowledge_all_expansion_wizard(self):
        """Classes with 'Knowledge (all)' get all Knowledge skills as class skills."""
        character = {
            "system": "pathfinder1e",
            "class": "Wizard",
            "level": 1,
            "ability_scores": {"intelligence": 16},
            "skills": {
                "Knowledge (Arcana)": 1,
                "Knowledge (Nature)": 1,
            }
        }
        res = self.calc.update_all_stats(character)
        skills_detail = res["skills_detail"]

        # Knowledge (Arcana) (1 rank, INT mod +3, class bonus +3): 1 + 3 + 3 = 7
        self.assertTrue(skills_detail["Knowledge (Arcana)"]["is_class_skill"])
        self.assertEqual(skills_detail["Knowledge (Arcana)"]["class_bonus"], 3)
        self.assertEqual(skills_detail["Knowledge (Arcana)"]["total"], 7)

        # Knowledge (Nature) (1 rank, INT mod +3, class bonus +3): 1 + 3 + 3 = 7
        self.assertTrue(skills_detail["Knowledge (Nature)"]["is_class_skill"])
        self.assertEqual(skills_detail["Knowledge (Nature)"]["class_bonus"], 3)
        self.assertEqual(skills_detail["Knowledge (Nature)"]["total"], 7)

if __name__ == "__main__":
    unittest.main()
