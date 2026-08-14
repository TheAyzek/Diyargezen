"""
Unit Tests for PF1e Combat & Maneuver Matrix Engine (CRB p. 140-150, 198-201)
=============================================================================
Verifies CMB & CMD for all 10 combat maneuvers, Agile Maneuvers, Dwarf Stability,
Iterative Full Attack progressions, and Power Attack mechanics.
"""

import pytest
from rules.calculators import PF1e_Calculator


def test_standard_10_maneuvers_matrix_calculation():
    """Verify default CMB and CMD values for all 10 standard maneuvers."""
    calc = PF1e_Calculator()
    char = {
        "name": "Valeros Base",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "wisdom": 10},
        "feats": []
    }

    derived = calc.update_all_stats(char)
    maneuvers = derived.get("maneuvers", {})

    # 10 Official Maneuvers
    expected_maneuvers = [
        "Grapple", "Trip", "Disarm", "Sunder", "Bull Rush",
        "Overrun", "Dirty Trick", "Steal", "Reposition", "Drag"
    ]
    for m in expected_maneuvers:
        assert m in maneuvers
        # BAB 1 + STR 3 = 4 CMB
        assert maneuvers[m]["cmb"] == 4
        assert maneuvers[m]["cmb_str"] == "+4"
        # 10 + BAB 1 + STR 3 + DEX 2 = 16 CMD
        assert maneuvers[m]["cmd"] == 16


def test_improved_and_greater_maneuver_feats():
    """Improved Grapple (+2/+2) and Greater Grapple (+2/+2) stack to +4 CMB and +4 CMD."""
    calc = PF1e_Calculator()
    char = {
        "name": "Grappler Monk",
        "system": "pathfinder1e",
        "level": 6,
        "class": "Monk",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "wisdom": 10},
        "feats": ["Improved Grapple", "Greater Grapple", "Improved Trip"]
    }

    derived = calc.update_all_stats(char)
    maneuvers = derived.get("maneuvers", {})

    # BAB = floor(6 * 3/4) = 4, STR = 3 -> Base CMB = 7
    # Grapple has Improved (+2) + Greater (+2) -> CMB = 11
    assert maneuvers["Grapple"]["cmb"] == 11
    assert maneuvers["Grapple"]["bonus_cmb"] == 4
    # Base CMD = 10 + 4 + 3 + 2 = 19 -> +4 Grapple feat CMD = 23
    assert maneuvers["Grapple"]["cmd"] == 23

    # Trip has Improved Trip (+2/+2) -> CMB = 9, CMD = 21
    assert maneuvers["Trip"]["cmb"] == 9
    assert maneuvers["Trip"]["bonus_cmb"] == 2
    assert maneuvers["Trip"]["cmd"] == 21

    # Disarm has no feats -> CMB = 7, CMD = 19
    assert maneuvers["Disarm"]["cmd"] == 19


def test_agile_maneuvers_feat():
    """Agile Maneuvers uses DEX modifier (+4) instead of STR modifier (+1) for CMB."""
    calc = PF1e_Calculator()
    char = {
        "name": "Acrobatic Rogue",
        "system": "pathfinder1e",
        "level": 4,
        "class": "Rogue",
        "abilities": {"strength": 12, "dexterity": 18, "constitution": 14, "wisdom": 10},
        "feats": ["Agile Maneuvers"]
    }

    derived = calc.update_all_stats(char)
    # BAB = floor(4 * 3/4) = 3. With Agile Maneuvers: BAB 3 + DEX 4 = 7 CMB (instead of BAB 3 + STR 1 = 4)
    assert derived["cmb"] == 7
    assert derived["maneuvers"]["Grapple"]["cmb"] == 7


def test_dwarf_stability_racial_cmd_bonus():
    """Dwarves gain +4 CMD against Bull Rush and Trip."""
    calc = PF1e_Calculator()
    char = {
        "name": "Dwarf Defender",
        "system": "pathfinder1e",
        "race": "Dwarf",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 14, "dexterity": 12, "constitution": 16, "wisdom": 14},
        "feats": []
    }

    derived = calc.update_all_stats(char)
    maneuvers = derived.get("maneuvers", {})

    # Base CMD = 10 + BAB 1 + STR 2 + DEX 1 = 14
    assert maneuvers["Disarm"]["cmd"] == 14
    assert maneuvers["Grapple"]["cmd"] == 14
    # Dwarf Stability adds +4 to Bull Rush & Trip CMD
    assert maneuvers["Bull Rush"]["cmd"] == 18
    assert maneuvers["Trip"]["cmd"] == 18
    assert "+4 (Dwarf Stability)" in maneuvers["Bull Rush"]["cmd_summary"]


def test_full_attack_progression_iterative_attacks():
    """Level 11 Fighter (BAB 11) gets full attack progression +11/+6/+1."""
    calc = PF1e_Calculator()
    char = {
        "name": "Valeros High Level",
        "system": "pathfinder1e",
        "level": 11,
        "class": "Fighter",
        "abilities": {"strength": 18, "dexterity": 14, "constitution": 14, "wisdom": 10},
        "feats": ["Weapon Focus (Longsword)"],
        "equipment": [{"name": "+2 Longsword", "type": "Weapon", "quantity": 1}]
    }

    derived = calc.update_all_stats(char)
    weapon = derived["weapons"][0]

    # Total Attack 1st = BAB 11 + STR 4 + Enh 2 + WF 1 = +18
    # Full Attack = +18 / +13 / +8
    assert weapon["calculated_attack"] == "+18"
    assert weapon["full_attack"] == "+18 / +13 / +8"


def test_power_attack_calculations():
    """Level 8 Fighter (BAB 8) using Power Attack: penalty -3, 1H damage +6, 2H damage +9."""
    calc = PF1e_Calculator()
    char = {
        "name": "Two-Handed Amiri",
        "system": "pathfinder1e",
        "level": 8,
        "class": "Barbarian",
        "abilities": {"strength": 18, "dexterity": 14, "constitution": 14, "wisdom": 10},
        "feats": ["Power Attack"],
        "equipment": [
            {"name": "+1 Greatsword", "type": "Weapon", "quantity": 1},
            {"name": "+1 Longsword", "type": "Weapon", "quantity": 1}
        ]
    }

    derived = calc.update_all_stats(char)
    greatsword = derived["weapons"][0]
    longsword = derived["weapons"][1]

    # BAB 8 -> Power Attack penalty = 1 + floor(8/4) = 3
    # Greatsword (2H): PA bonus damage = 3 * 3 = +9
    assert greatsword["power_attack"] is not None
    assert greatsword["power_attack"]["penalty"] == -3
    assert greatsword["power_attack"]["bonus_damage"] == 9
    assert "2d6 +" in greatsword["power_attack"]["damage"]

    # Longsword (1H): PA bonus damage = 3 * 2 = +6
    assert longsword["power_attack"] is not None
    assert longsword["power_attack"]["penalty"] == -3
    assert longsword["power_attack"]["bonus_damage"] == 6
