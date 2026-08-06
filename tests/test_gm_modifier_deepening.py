"""
Unit Tests for PF1e GM Soft-Block Inspector & Custom Modifier System
======================================================================
Verifies GM custom modifiers for skills (skill:Stealth, skill:Perception),
Initiative, Speed, and GM soft-block override warning suppression.
"""

import pytest
from rules.calculators import PF1e_Calculator
from rules.pf1e_rules import PF1EValidator


def test_gm_custom_skill_initiative_speed_modifiers():
    """Verify custom GM modifiers applied to skills, initiative, and speed."""
    calc = PF1e_Calculator()
    char_sheet = {
        "name": "Ezren GM",
        "system": "pathfinder1e",
        "level": 4,
        "class": "Wizard",
        "abilities": {"dexterity": 14, "intelligence": 16},
        "custom_modifiers": [
            {"stat": "skill:Stealth", "value": 5, "name": "Shadow Cloak", "is_active": True},
            {"stat": "skill:Perception", "value": 3, "name": "Keen Ear", "is_active": True},
            {"stat": "init", "value": 4, "name": "Tactical Awareness", "is_active": True},
            {"stat": "speed", "value": 10, "name": "Boots of Striding", "is_active": True}
        ]
    }

    derived = calc.update_all_stats(char_sheet)

    # Base Stealth: Rank 0 + Dex 2 = 2. With GM +5 = 7
    assert derived["skills"]["stealth"] == 7
    # Base Perception: Rank 0 + Wis 0 = 0. With GM +3 = 3
    assert derived["skills"]["perception"] == 3
    # Base Init: Dex 2. With GM +4 = 6
    assert derived["initiative"] == 6
    # Base Speed: 30 ft. With GM +10 = 40 ft
    assert derived["speed"] == 40


def test_gm_soft_block_override_warning_suppression():
    """Verify gm_override suppresses soft-block warnings completely."""
    validator = PF1EValidator()
    invalid_char = {
        "level": 1,
        "bab": 0,
        "abilities": {"str": 8, "dex": 8},
        "feats": ["Spring Attack", "Great Cleave"],
        "gm_override": False
    }

    warnings = validator.validate(invalid_char)
    assert len(warnings) > 0

    # Apply GM override
    invalid_char["gm_override"] = True
    assert validator.validate(invalid_char) == []
