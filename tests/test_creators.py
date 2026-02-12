# tests/test_creators.py
"""
Unit tests for character creators
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from creators import CharacterFactory


class TestCharacterCreators(unittest.TestCase):
    """Test character creator functionality"""

    def test_factory_registration(self):
        """Test that all creators are registered"""
        available = CharacterFactory.get_available_systems()
        expected = ['dnd5e', 'dungeonsanddragons', 'd&d', 'pathfinder1e', 'pathfinder', 'pf1e', 'vtm5e', 'vampire', 'vtm', 'mm3e', 'mutantsandmasterminds', 'm&m']
        for system in expected:
            self.assertIn(system, available)

    def test_dnd_creator_creation(self):
        """Test D&D 5e character creation"""
        creator = CharacterFactory.create_creator('dnd5e')

        # Mock character data for validation
        test_char = {
            'system': 'DND5E',
            'race': 'Human',
            'class': 'Fighter',
            'background': 'Soldier',
            'abilities': {'strength': 16, 'dexterity': 14, 'constitution': 15, 'intelligence': 10, 'wisdom': 12, 'charisma': 8},
            'modifiers': {'strength': 3, 'dexterity': 2, 'constitution': 2, 'intelligence': 0, 'wisdom': 1, 'charisma': -1},
            'level': 1,
            'background_data': {'skill_proficiencies': ['Athletics', 'Intimidation']}
        }

        # Test validation
        errors = creator.validate_character(test_char)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")

        # Test derived stats
        derived = creator.calculate_derived_stats(test_char)
        self.assertIn('proficiency_bonus', derived)
        self.assertIn('saving_throws', derived)
        self.assertIn('skills', derived)
        self.assertEqual(derived['proficiency_bonus'], 2)  # Level 1

    def test_pathfinder_creator_validation(self):
        """Test Pathfinder 1e character validation"""
        creator = CharacterFactory.create_creator('pathfinder1e')

        # Valid character
        valid_char = {
            'system': 'PATHFINDER_1E',
            'race': 'Human',
            'class': 'Fighter',
            'abilities': {'strength': 16, 'dexterity': 14, 'constitution': 15, 'intelligence': 10, 'wisdom': 12, 'charisma': 8},
            'level': 1,
            'bab': 1,
            'saves': {'fortitude': 2, 'reflex': 0, 'will': 0}
        }

        errors = creator.validate_character(valid_char)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")

        # Invalid character (abilities too high)
        invalid_char = {
            'system': 'PATHFINDER_1E',
            'race': 'Human',
            'class': 'Fighter',
            'abilities': {'strength': 20, 'dexterity': 14, 'constitution': 15, 'intelligence': 10, 'wisdom': 12, 'charisma': 8},
            'level': 1,
            'bab': 1,
            'saves': {'fortitude': 2, 'reflex': 0, 'will': 0}
        }

        errors = creator.validate_character(invalid_char)
        self.assertGreater(len(errors), 0, "Should have validation errors for invalid abilities")

    def test_vtm_creator_validation(self):
        """Test VtM 5e character validation"""
        creator = CharacterFactory.create_creator('vtm5e')

        # Valid character
        valid_char = {
            'system': 'VAMPIRE_THE_MASQUERADE_5E',
            'clan': 'Brujah',
            'attributes': {
                'physical': {'Strength': 2, 'Dexterity': 3, 'Stamina': 2},
                'social': {'Charisma': 2, 'Manipulation': 1, 'Composure': 2},
                'mental': {'Intelligence': 2, 'Wits': 2, 'Resolve': 1}
            },
            'skills': {
                'physical': {'Athletics': 1, 'Brawl': 2, 'Stealth': 1},
                'social': {'Intimidation': 2, 'Persuasion': 1, 'Streetwise': 1},
                'mental': {'Awareness': 1, 'Investigation': 1, 'Politics': 1}
            },
            'disciplines': {'Celerity': 1, 'Potence': 1, 'Presence': 1}
        }

        errors = creator.validate_character(valid_char)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")

        # Test derived stats
        derived = creator.calculate_derived_stats(valid_char)
        self.assertIn('max_health', derived)
        self.assertIn('max_willpower', derived)
        self.assertIn('initiative', derived)

    def test_mm_creator_validation(self):
        """Test M&M 3e character validation"""
        creator = CharacterFactory.create_creator('mm3e')

        # Valid character
        valid_char = {
            'system': 'MUTANTS_AND_MASTERMINDS_3E',
            'power_level': 'PL10',
            'pl_value': 10,
            'abilities': {
                'strength': 8, 'stamina': 8, 'agility': 6, 'dexterity': 6,
                'fighting': 8, 'intellect': 4, 'awareness': 4, 'presence': 4
            },
            'powers': {},
            'remaining_power_points': 50
        }

        errors = creator.validate_character(valid_char)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")

        # Test PL limits
        invalid_char = {
            'system': 'MUTANTS_AND_MASTERMINDS_3E',
            'power_level': 'PL10',
            'pl_value': 10,
            'abilities': {'strength': 15},  # Too high for PL 10
            'powers': {},
            'remaining_power_points': 50
        }

        errors = creator.validate_character(invalid_char)
        self.assertGreater(len(errors), 0, "Should have PL limit validation errors")

    def test_data_loading(self):
        """Test that all creators can load their data"""
        systems = ['dnd5e', 'pathfinder1e', 'vtm5e', 'mm3e']

        for system in systems:
            with self.subTest(system=system):
                creator = CharacterFactory.create_creator(system)
                self.assertIsNotNone(creator.data)
                self.assertGreater(len(creator.data), 0)


if __name__ == '__main__':
    unittest.main()