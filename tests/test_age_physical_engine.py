"""
Unit Tests for PF1e Age, Height & Weight Engine
================================================
Verifies:
- Cumulative aging modifiers (Middle Age, Old, Venerable)
- Racial starting age categories & dice formulas
- Table 7-3 Height & Weight generation formulas
- PF1e Calculator ability score adjustments
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.age_height_weight import (
    get_age_category_and_modifiers,
    generate_random_starting_age,
    generate_random_height_weight,
    get_physical_rules_catalog
)
from rules.calculators import PF1e_Calculator
from fastapi.testclient import TestClient
from app.main import app


def test_human_aging_categories_and_modifiers():
    """Verify Human aging thresholds and cumulative modifiers."""
    # Adulthood (25 yrs)
    res_adult = get_age_category_and_modifiers("Human", 25)
    assert res_adult["category_code"] == "adulthood"
    assert res_adult["physical_modifier"] == 0
    assert res_adult["mental_modifier"] == 0

    # Middle Age (38 yrs)
    res_mid = get_age_category_and_modifiers("Human", 38)
    assert res_mid["category_code"] == "middle_age"
    assert res_mid["physical_modifier"] == -1
    assert res_mid["mental_modifier"] == +1

    # Old (55 yrs)
    res_old = get_age_category_and_modifiers("Human", 55)
    assert res_old["category_code"] == "old"
    assert res_old["physical_modifier"] == -3
    assert res_old["mental_modifier"] == +2

    # Venerable (75 yrs)
    res_ven = get_age_category_and_modifiers("Human", 75)
    assert res_ven["category_code"] == "venerable"
    assert res_ven["physical_modifier"] == -6
    assert res_ven["mental_modifier"] == +3


def test_calculator_aging_stat_adjustments():
    """Verify Old Human Wizard (+2 Int, -3 Con) updates ability scores and HP."""
    calc = PF1e_Calculator()
    character = {
        "name": "Old Ezren",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Wizard",
        "level": 1,
        "age": 55, # Old (-3 Phys / +2 Ment)
        "abilities": {
            "strength": 10,
            "dexterity": 10,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 12,
            "charisma": 10
        },
        "racial_ability_choice": "intelligence" # +2 Racial
    }

    res = calc.update_all_stats(character)
    # Int: 16 (base) + 2 (racial) + 2 (old age) = 20
    assert res["ability_scores"]["Intelligence"] == 20
    # Con: 12 (base) - 3 (old age) = 9 (Mod: -1)
    assert res["ability_scores"]["Constitution"] == 9
    assert res["ability_modifiers"]["Constitution"] == -1
    # Str: 10 - 3 = 7
    assert res["ability_scores"]["Strength"] == 7
    # Dex: 10 - 3 = 7
    assert res["ability_scores"]["Dexterity"] == 7


def test_starting_age_and_height_weight_formulas():
    """Verify starting age class training and Table 7-3 height/weight formulas."""
    # Human Wizard (Trained 15 + 2d6) with roll 8 -> 23 yrs
    age_wiz = generate_random_starting_age("Human", "Wizard", roll_override=8)
    assert age_wiz["starting_age"] == 23
    assert age_wiz["training_type"] == "trained"

    # Human Male with height roll 10 (Base 58 in, Base 120 lb, Mult 5)
    # Total H: 58 + 10 = 68 in (5'8"), Total W: 120 + (10 * 5) = 170 lb
    hw_male = generate_random_height_weight("Human", "male", height_roll_override=10)
    assert hw_male["height_inches"] == 68
    assert hw_male["height_imperial"] == "5'8\""
    assert hw_male["weight_lbs"] == 170


def test_age_physical_backend_api():
    """Verify /api/rules/age-tables, /api/rules/evaluate-age and /api/rules/generate-physical."""
    client = TestClient(app)

    # 1. Age Tables
    res_tables = client.get("/api/rules/age-tables")
    assert res_tables.status_code == 200
    data_t = res_tables.json()
    assert "human" in data_t["age_thresholds"]

    # 2. Evaluate Age
    res_eval = client.post("/api/rules/evaluate-age", json={"race": "Elf", "age": 270})
    assert res_eval.status_code == 200
    data_e = res_eval.json()
    assert data_e["category_code"] == "old" # Elf 263+ is Old

    # 3. Generate Physical
    res_gen = client.post("/api/rules/generate-physical", json={
        "race": "Dwarf",
        "char_class": "Fighter",
        "gender": "female"
    })
    assert res_gen.status_code == 200
    data_g = res_gen.json()
    assert "starting_age" in data_g
    assert "height_weight" in data_g
