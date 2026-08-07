"""
Unit Tests for PF1e Companion & Familiar Engine Deepening
=========================================================
Verifies official PF1e Effective Druid Level (EDL) scaling, Hit Dice, Natural Armor,
Familiar HP (50% of Master HP), and Familiar Toad (+3 Max HP) master bonus application.
"""

import math
import pytest
from rules.companion_calculator import PF1eCompanionCalculator, ANIMAL_COMPANION_TABLE, FAMILIAR_MASTER_BONUSES
from rules.calculators import PF1e_Calculator


def test_effective_druid_level_calculation():
    """Ranger has Level - 3 penalty; Druid/Hunter has 100% level."""
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Druid", 5) == 5
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Hunter", 7) == 7
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Ranger", 5) == 2
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Ranger", 2) == 1  # Min 1


def test_animal_companion_scaling():
    """Wolf companion HD, HP, AC, and BAB scaling for Level 5 Druid."""
    wolf_data = {
        "name": "Fenrir",
        "species": "Wolf",
        "str": 13,
        "dex": 15,
        "con": 15,
        "int": 2,
        "wis": 12,
        "cha": 6,
        "acBonus": 2,
        "attacks": "Isırık 1d6"
    }

    res = PF1eCompanionCalculator.calculate_animal_companion(wolf_data, master_class="Druid", master_level=5)

    assert res["effective_druid_level"] == 5
    assert res["hd_count"] == 5
    assert res["natural_armor_bonus"] == 4
    assert res["str"] == 15  # 13 base + 2 adj
    assert res["dex"] == 17  # 15 base + 2 adj
    assert "Link" in res["special_abilities"]
    assert "Evasion" in res["special_abilities"]


def test_familiar_scaling_and_toad_master_bonus():
    """Familiar Toad grants 50% Master HP to familiar and +3 Max HP to master."""
    toad_data = {
        "name": "Goliath",
        "species": "Toad",
        "presetKey": "toad",
        "dex": 12
    }

    fam_res = PF1eCompanionCalculator.calculate_familiar(toad_data, master_level=4, master_max_hp=30)

    assert fam_res["hp"] == 15  # 50% of 30
    assert fam_res["master_bonus"]["value"] == 3

    # Now verify calculator applies Toad's +3 HP to master's sheet
    calc = PF1e_Calculator()
    char_sheet = {
        "name": "Ezren",
        "system": "pathfinder1e",
        "level": 4,
        "class": "Wizard",
        "abilities": {"constitution": 12},
        "companion": {
            "type": "familiar",
            "presetKey": "toad",
            "name": "Goliath",
            "dex": 12
        }
    }

    derived = calc.update_all_stats(char_sheet)
    # Master base HP (Level 4 Wizard d6 + 1 Con mod): 6 + 1 + 3*(3 + 1 + 1) = 22. With Toad +3 HP = 25 HP.
    assert derived["hit_points"] == 25
    assert derived["companion"]["hp"] == 11  # 50% of master base 22 HP
