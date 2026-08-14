"""
Unit Tests for PF1e Inventory Quick-Equip & Slot Engine
========================================================
Verifies:
- Equipped vs In-Backpack armor & shield AC and ACP mechanics
- Magic item stat enhancements (Belt of Strength, Cloak of Resistance)
- Magic slot conflict detection strictly ignoring unequipped backpack items
- Total wealth and total weight preservation
"""

import pytest
from rules.calculators import PF1e_Calculator
from rules.magic_item_slots import evaluate_magic_item_slots_and_wealth


def test_armor_equipped_vs_unequipped_backpack():
    """Verify equipped armor gives AC and ACP, while unequipped armor only adds weight."""
    calc = PF1e_Calculator()

    char_equipped = {
        "name": "Valeros Knight",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": [
            {
                "name": "Breastplate",
                "is_equipped": True,
                "sistem_verisi": {
                    "armor_class": {"value": 6, "dex": 3},
                    "check_penalty": -4,
                    "weight": {"value": 30}
                }
            }
        ]
    }
    res_eq = calc.update_all_stats(char_equipped)
    # AC: 10 + DEX_mod(2) + Armor(6) = 18
    assert res_eq["armor_class"] == 18
    assert res_eq["armor_check_penalty"] == -4
    assert res_eq["total_weight"] == 30.0

    # Unequip the breastplate (put into backpack)
    char_backpack = {
        "name": "Valeros Knight",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": [
            {
                "name": "Breastplate",
                "is_equipped": False,
                "sistem_verisi": {
                    "armor_class": {"value": 6, "dex": 3},
                    "check_penalty": -4,
                    "weight": {"value": 30}
                }
            }
        ]
    }
    res_uneq = calc.update_all_stats(char_backpack)
    # AC without armor: 10 + DEX_mod(2) = 12
    assert res_uneq["armor_class"] == 12
    assert res_uneq["armor_check_penalty"] == 0
    # Total weight is STILL 30 lbs in backpack!
    assert res_uneq["total_weight"] == 30.0


def test_magic_belt_equipped_vs_unequipped():
    """Verify magic belt only gives stat bonus when equipped."""
    calc = PF1e_Calculator()

    char_belt_eq = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": [
            {"name": "Belt of Giant Strength +2", "is_equipped": True, "price": 4000}
        ]
    }
    res_eq = calc.update_all_stats(char_belt_eq)
    assert res_eq["ability_scores"]["Strength"] == 18
    assert res_eq["ability_modifiers"]["Strength"] == 4

    char_belt_bag = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": [
            {"name": "Belt of Giant Strength +2", "is_equipped": False, "price": 4000}
        ]
    }
    res_bag = calc.update_all_stats(char_belt_bag)
    assert res_bag["ability_scores"]["Strength"] == 16
    assert res_bag["ability_modifiers"]["Strength"] == 3
    # Total wealth still includes the 4,000 gp belt in bag
    assert res_bag["wealth"]["total_wealth_gp"] == 4000.0


def test_slot_conflict_resolution_with_unequipped_items():
    """Verify that having two belts in inventory does NOT conflict if one is unequipped."""
    eq_list = [
        {"name": "Belt of Giant Strength +2", "is_equipped": True, "price": 4000},
        {"name": "Belt of Mighty Constitution +2", "is_equipped": False, "price": 4000}
    ]
    eval_res = evaluate_magic_item_slots_and_wealth(eq_list, level=5)
    # Belt slot is occupied by the equipped one
    assert eval_res["occupied_slots"]["belts"] is not None
    assert eval_res["occupied_slots"]["belts"]["name"] == "Belt of Giant Strength +2"
    # No conflict because the second belt is in the backpack!
    assert eval_res["has_conflicts"] is False
    assert len(eval_res["slot_conflicts"]) == 0
    # Both items count toward wealth (8,000 gp)
    assert eval_res["wealth"]["total_wealth_gp"] == 8000.0
