"""
Unit Tests for PF1e Magic Item Body Slots & Wealth by Level (WBL) Engine
========================================================================
Verifies 12 body slot assignments, slot conflict detection, automatic pricing formulas,
and Wealth by Level (WBL Table 12-4) calculations.
"""

import pytest
from rules.calculators import PF1e_Calculator
from rules.magic_item_slots import (
    infer_item_body_slot,
    infer_magic_item_price_gp,
    evaluate_magic_item_slots_and_wealth,
    PF1E_WEALTH_BY_LEVEL
)


def test_infer_item_body_slots():
    """Verify standard Paizo magic items resolve to their correct 12 body slots."""
    assert infer_item_body_slot({"name": "Headband of Vast Intelligence +4"}) == "headband"
    assert infer_item_body_slot({"name": "Helm of Telepathy"}) == "head"
    assert infer_item_body_slot({"name": "Goggles of Night"}) == "eyes"
    assert infer_item_body_slot({"name": "Amulet of Natural Armor +2"}) == "neck"
    assert infer_item_body_slot({"name": "Cloak of Resistance +3"}) == "shoulders"
    assert infer_item_body_slot({"name": "+1 Mithral Breastplate"}) == "armor"
    assert infer_item_body_slot({"name": "Monk's Robe"}) == "body"
    assert infer_item_body_slot({"name": "Quick Runner's Shirt"}) == "chest"
    assert infer_item_body_slot({"name": "Belt of Giant Strength +2"}) == "belts"
    assert infer_item_body_slot({"name": "Bracers of Armor +4"}) == "wrists"
    assert infer_item_body_slot({"name": "Gauntlets of Ogre Power"}) == "hands"
    assert infer_item_body_slot({"name": "Boots of Speed"}) == "feet"
    assert infer_item_body_slot({"name": "Ring of Protection +2"}) == "ring"
    assert infer_item_body_slot({"name": "Dusty Rose Prism Ioun Stone"}) == "slotless"


def test_magic_item_formulaic_pricing():
    """Verify automatic price calculation according to PF1e CRB formulas."""
    # Cloak of Resistance (+1 = 1k, +2 = 4k, +3 = 9k, +4 = 16k, +5 = 25k)
    assert infer_magic_item_price_gp({"name": "Cloak of Resistance +1"}) == 1000.0
    assert infer_magic_item_price_gp({"name": "Cloak of Resistance +3"}) == 9000.0
    assert infer_magic_item_price_gp({"name": "Cloak of Resistance +5"}) == 25000.0

    # Ring of Protection (+1 = 2k, +2 = 8k, +3 = 18k)
    assert infer_magic_item_price_gp({"name": "Ring of Protection +2"}) == 8000.0

    # Stat Belts (+2 = 4k, +4 = 16k, +6 = 36k)
    assert infer_magic_item_price_gp({"name": "Belt of Giant Strength +2"}) == 4000.0
    assert infer_magic_item_price_gp({"name": "Belt of Incredible Dexterity +4"}) == 16000.0

    # Wonderous items
    assert infer_magic_item_price_gp({"name": "Boots of Speed"}) == 12000.0
    assert infer_magic_item_price_gp({"name": "Handy Haversack"}) == 2000.0


def test_slot_conflict_detection_belts():
    """Equipping two belts causes a slot conflict warning."""
    equipment = [
        {"name": "Belt of Giant Strength +2", "is_equipped": True},
        {"name": "Belt of Incredible Dexterity +2", "is_equipped": True}
    ]

    res = evaluate_magic_item_slots_and_wealth(equipment, level=5)
    assert res["has_conflicts"] is True
    assert len(res["slot_conflicts"]) == 1
    assert res["slot_conflicts"][0]["slot"] == "belts"
    assert res["slot_conflicts"][0]["equipped_count"] == 2


def test_ring_slot_limits_and_conflicts():
    """Equipping up to 2 rings is valid; equipping 3 rings triggers a conflict."""
    # 2 rings = valid
    two_rings = [
        {"name": "Ring of Protection +1", "is_equipped": True},
        {"name": "Ring of Sustenance", "is_equipped": True}
    ]
    res_2 = evaluate_magic_item_slots_and_wealth(two_rings, level=5)
    assert res_2["has_conflicts"] is False
    assert res_2["occupied_slots"]["ring_1"] is not None
    assert res_2["occupied_slots"]["ring_2"] is not None

    # 3 rings = conflict
    three_rings = two_rings + [{"name": "Ring of Invisibility", "is_equipped": True}]
    res_3 = evaluate_magic_item_slots_and_wealth(three_rings, level=5)
    assert res_3["has_conflicts"] is True
    assert res_3["slot_conflicts"][0]["slot"] == "ring"
    assert res_3["slot_conflicts"][0]["equipped_count"] == 3


def test_wealth_by_level_evaluation():
    """Verify Wealth by Level calculations against CRB Table 12-4."""
    # Level 5 character (Expected WBL: 10,500 gp)
    # Equipment: Cloak +2 (4,000 gp) + Belt +2 (4,000 gp) + Ring +1 (2,000 gp) = 10,000 gp
    equipment = [
        {"name": "Cloak of Resistance +2", "is_equipped": True},
        {"name": "Belt of Giant Strength +2", "is_equipped": True},
        {"name": "Ring of Protection +1", "is_equipped": True}
    ]

    res = evaluate_magic_item_slots_and_wealth(equipment, level=5)
    wealth = res["wealth"]

    assert wealth["total_wealth_gp"] == 10000.0
    assert wealth["expected_wbl_gp"] == 10500
    assert wealth["status_code"] == "balanced"
    assert wealth["percentage"] == 95.2


def test_calculator_update_all_stats_integration():
    """PF1e_Calculator.update_all_stats includes magic_item_slots and wealth analysis."""
    calc = PF1e_Calculator()
    char = {
        "name": "Valeros Geared",
        "system": "pathfinder1e",
        "level": 7,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14},
        "equipment": [
            {"name": "Cloak of Resistance +2", "is_equipped": True},
            {"name": "Ring of Protection +1", "is_equipped": True},
            {"name": "Belt of Giant Strength +2", "is_equipped": True}
        ]
    }

    derived = calc.update_all_stats(char)

    assert "magic_item_slots" in derived
    assert derived["magic_item_slots"]["shoulders"]["name"] == "Cloak of Resistance +2"
    assert derived["magic_item_slots"]["ring_1"]["name"] == "Ring of Protection +1"
    assert derived["magic_item_slots"]["belts"]["name"] == "Belt of Giant Strength +2"

    assert "wealth" in derived
    assert derived["wealth"]["expected_wbl_gp"] == 23500  # Level 7 WBL
    assert derived["wealth"]["total_wealth_gp"] == 10000.0
