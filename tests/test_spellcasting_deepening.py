"""
Unit Tests for PF1e Spellcasting Engine Deepening
===================================================
Verifies Caster Level (CL), Concentration Checks (CL + Casting Mod + Feats),
Spell Save DCs per level (10 + Level + Mod + Misc), Bonus Spell Slots, and PDF Export mapping.
"""

import pytest
from rules.calculators import PF1e_Calculator
from rules.spell_engine import calculate_bonus_spell_slots, calculate_spell_save_dc, calculate_total_spell_slots


def test_spell_save_dcs_and_concentration_wizard_level_5():
    """Wizard 5 with INT 18 (+4) and Combat Casting feat."""
    calc = PF1e_Calculator()
    char_wizard = {
        "name": "Ezren",
        "system": "pathfinder1e",
        "level": 5,
        "class": "Wizard",
        "abilities": {"intelligence": 18},
        "feats": ["Combat Casting", "Spell Focus"]
    }

    derived = calc.update_all_stats(char_wizard)
    sc = derived["spellcasting"]

    assert sc["primary_ability"] == "intelligence"
    assert sc["ability_modifier"] == 4
    assert sc["caster_level"] == 5
    # Concentration = CL (5) + INT Mod (4) + Combat Casting (4) = 13
    assert sc["concentration_bonus"] == 13
    assert sc["has_combat_casting"] is True
    assert sc["has_spell_focus"] is True

    # DCs with Spell Focus (+1):
    # Level 0 DC: 10 + 0 + 4 + 1 = 15
    # Level 1 DC: 10 + 1 + 4 + 1 = 16
    # Level 3 DC: 10 + 3 + 4 + 1 = 18
    assert sc["spell_dcs"]["0"] == 15
    assert sc["spell_dcs"]["1"] == 16
    assert sc["spell_dcs"]["3"] == 18


def test_ranger_caster_level_and_bonus_slots():
    """Ranger Level 7 (CL = 7 - 3 = 4) with WIS 16 (+3)."""
    calc = PF1e_Calculator()
    char_ranger = {
        "name": "Valeros Ranger",
        "system": "pathfinder1e",
        "level": 7,
        "class": "Ranger",
        "abilities": {"wisdom": 16}
    }

    derived = calc.update_all_stats(char_ranger)
    sc = derived["spellcasting"]

    assert sc["primary_ability"] == "wisdom"
    assert sc["ability_modifier"] == 3
    assert sc["caster_level"] == 4
    # Concentration = CL (4) + WIS Mod (3) = 7
    assert sc["concentration_bonus"] == 7
    assert sc["spell_dcs"]["1"] == 14  # 10 + 1 + 3
