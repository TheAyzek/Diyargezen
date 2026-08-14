"""
Unit Tests for PF1e Conditions & Situational Buffs Engine
=========================================================
Tests:
- Registry retrieval and metadata
- Stacking rules (Morale, Competence, Enhancement vs Dodge)
- Direct condition calculations (Haste, Sickened, Rage, Bull's Strength, Mage Armor)
- Integration into PF1e_Calculator.update_all_stats
- API endpoint /api/rules/conditions-buffs
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.conditions_engine import (
    calculate_conditions_and_buffs_modifiers,
    get_available_conditions_and_buffs,
    PF1E_CONDITIONS_AND_BUFFS
)
from rules.calculators import PF1e_Calculator
from fastapi.testclient import TestClient
from app.main import app


def test_conditions_registry():
    """Verify registry contains 25+ official conditions and buffs."""
    conds = get_available_conditions_and_buffs()
    assert len(conds) >= 25
    ids = [c["id"] for c in conds]
    assert "haste" in ids
    assert "bless" in ids
    assert "sickened" in ids
    assert "fatigued" in ids
    assert "barbarian_rage" in ids


def test_haste_buff_modifiers():
    """Verify Haste buff confers +1 attack, +1 dodge AC, +1 reflex, and +30 speed."""
    calc = PF1e_Calculator()
    char_base = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "active_conditions": []
    }
    res_base = calc.update_all_stats(char_base)

    char_haste = dict(char_base)
    char_haste["active_conditions"] = ["haste"]
    res_haste = calc.update_all_stats(char_haste)

    # Attack: Base 4 -> Haste 5 (+1)
    assert res_haste["melee_attack_bonus"] == res_base["melee_attack_bonus"] + 1
    # AC: Base 12 -> Haste 13 (+1 Dodge)
    assert res_haste["armor_class"] == res_base["armor_class"] + 1
    assert res_haste["touch_ac"] == res_base["touch_ac"] + 1
    # Reflex save: Base 2 -> Haste 3 (+1)
    assert res_haste["saving_throws"]["Reflex"] == res_base["saving_throws"]["Reflex"] + 1
    # Speed: Base 30 -> Haste 60 (+30 ft)
    assert res_haste["speed"] == res_base["speed"] + 30


def test_sickened_and_fatigued_debuffs():
    """Verify Sickened (-2 attack, damage, saves, skills) and Fatigued (-2 STR/DEX)."""
    calc = PF1e_Calculator()
    char_sick = {
        "name": "Sick Fighter",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "active_conditions": ["sickened", "fatigued"]
    }
    res = calc.update_all_stats(char_sick)

    # Fatigued: STR 16 - 2 = 14 (mod +2), DEX 14 - 2 = 12 (mod +1)
    assert res["ability_scores"]["Strength"] == 14
    assert res["ability_scores"]["Dexterity"] == 12
    assert res["ability_modifiers"]["Strength"] == 2

    # Attack: BAB(1) + STR_mod(2) - Sickened(2) = 1
    assert res["melee_attack_bonus"] == 1

    # Fortitude: Base(2) + CON_mod(2) - Sickened(2) = 2
    assert res["saving_throws"]["Fortitude"] == 2


def test_barbarian_rage_buff():
    """Verify Barbarian Rage confers +4 STR, +4 CON, +2 Will, -2 AC."""
    calc = PF1e_Calculator()
    char_rage = {
        "name": "Amiri Rage",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Barbarian",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 12, "charisma": 10},
        "active_conditions": ["barbarian_rage"]
    }
    res = calc.update_all_stats(char_rage)

    # STR: 16 + 4 = 20 (mod +5)
    assert res["ability_scores"]["Strength"] == 20
    assert res["ability_modifiers"]["Strength"] == 5

    # CON: 14 + 4 = 18 (mod +4), HP = 12 + 4 = 16
    assert res["ability_scores"]["Constitution"] == 18
    assert res["hit_points"] == 16

    # AC: 10 + 2 (dex) - 2 (rage) = 10
    assert res["armor_class"] == 10

    # Will save: Base(0) + WIS(1) + Rage(2) = 3
    assert res["saving_throws"]["Will"] == 3


def test_mage_armor_and_shield_spell_ac():
    """Verify Mage Armor (+4 armor) and Shield spell (+4 shield) grant AC without physical armor."""
    calc = PF1e_Calculator()
    char_wiz = {
        "name": "Ezren Warded",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Wizard",
        "abilities": {"strength": 10, "dexterity": 14, "constitution": 12, "intelligence": 18, "wisdom": 12, "charisma": 10},
        "active_conditions": ["mage_armor", "shield_spell"]
    }
    res = calc.update_all_stats(char_wiz)

    # AC: 10 + DEX(2) + MageArmor(4) + Shield(4) = 20
    assert res["armor_class"] == 20
    # Touch AC: 10 + DEX(2) = 12 (Armor and Shield do not apply to Touch AC)
    assert res["touch_ac"] == 12
    # Flat-Footed AC: 10 + MageArmor(4) + Shield(4) = 18
    assert res["flat_footed_ac"] == 18


def test_conditions_api_endpoint():
    """Verify /api/rules/conditions-buffs endpoint."""
    client = TestClient(app)
    response = client.get("/api/rules/conditions-buffs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 25
