"""
Unit Tests for PF1e Favored Class Bonus (FCB) & Racial Options Engine
=====================================================================
Verifies:
- Standard HP and Skill point FCB allocation
- APG/ARG Racial FCB options and fractional scaling (e.g. 1/6 spell, 1/2 damage)
- Multiclass and Half-Elf dual favored class support
- PF1e Calculator stat impact (HP and total skill ranks)
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.favored_class_engine import (
    evaluate_favored_class_bonuses,
    get_racial_fcb_options
)
from rules.calculators import PF1e_Calculator
from fastapi.testclient import TestClient
from app.main import app


def test_standard_fcb_hp_and_skill_allocation():
    """Verify level 5 fighter allocating 3 HP and 2 Skill ranks."""
    character = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Fighter",
        "level": 5,
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "favored_class": "Fighter",
        "favored_class_bonuses": [
            {"level": 1, "choice": "hp"},
            {"level": 2, "choice": "hp"},
            {"level": 3, "choice": "hp"},
            {"level": 4, "choice": "skill"},
            {"level": 5, "choice": "skill"}
        ]
    }

    fcb_res = evaluate_favored_class_bonuses(character)
    assert fcb_res["favored_class"] == "Fighter"
    assert fcb_res["total_eligible_levels"] == 5
    assert fcb_res["allocated_count"] == 5
    assert fcb_res["unallocated_count"] == 0
    assert fcb_res["hp_bonus"] == 3
    assert fcb_res["skill_bonus"] == 2
    assert fcb_res["is_complete"] is True

    calc = PF1e_Calculator()
    res = calc.update_all_stats(character)

    # Base Fighter HP at Lv 5 (d10 + Con 2): 10+2 + 4*(6+2) = 12 + 32 = 44
    # + 3 FCB HP = 47 HP
    assert res["hit_points"] == 47

    # Fighter Skill points per Lv (2 + Int 0) = 2*5 = 10
    # + Human bonus (5) + FCB skill (2) = 17 available skill points
    assert res["total_available_skill_points"] == 17


def test_human_wizard_racial_fcb_fractional_spell():
    """Verify Human Wizard taking 6 levels of +1/6 bonus spell known."""
    character = {
        "name": "Ezren",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Wizard",
        "level": 6,
        "abilities": {"strength": 10, "dexterity": 12, "constitution": 12, "intelligence": 18, "wisdom": 12, "charisma": 10},
        "favored_class": "Wizard",
        "favored_class_bonuses": [
            {"level": i, "choice": "human_wizard_spell"} for i in range(1, 7)
        ]
    }

    fcb_res = evaluate_favored_class_bonuses(character)
    assert fcb_res["total_eligible_levels"] == 6
    assert fcb_res["hp_bonus"] == 0
    assert fcb_res["skill_bonus"] == 0
    assert len(fcb_res["racial_bonuses"]) == 1

    rb = fcb_res["racial_bonuses"][0]
    assert rb["key"] == "human_wizard_spell"
    assert rb["allocated_ranks"] == 6
    assert rb["effective_value"] == 1  # 6 * (1/6) = 1


def test_half_elf_multitalented_multiclass_fcb():
    """Verify Half-Elf with Fighter and Ranger as dual favored classes."""
    character = {
        "name": "Kyra-HalfElf",
        "system": "pathfinder1e",
        "race": "Half-Elf",
        "class": "Fighter",
        "level": 6,
        "favored_class": "Fighter",
        "secondary_favored_class": "Ranger",
        "multiclass": {
            "Fighter": 4,
            "Ranger": 2
        },
        "favored_class_bonuses": [
            {"level": 1, "choice": "hp"},
            {"level": 2, "choice": "hp"},
            {"level": 3, "choice": "skill"},
            {"level": 4, "choice": "skill"},
            {"level": 5, "choice": "hp"},
            {"level": 6, "choice": "hp"}
        ]
    }

    fcb_res = evaluate_favored_class_bonuses(character)
    # Both Fighter (4) and Ranger (2) are eligible -> total 6
    assert fcb_res["total_eligible_levels"] == 6
    assert fcb_res["secondary_favored_class"] == "Ranger"
    assert fcb_res["hp_bonus"] == 4
    assert fcb_res["skill_bonus"] == 2


def test_favored_class_options_and_eval_api():
    """Verify /api/rules/favored-class-options and /api/rules/evaluate-fcb endpoints."""
    client = TestClient(app)

    # 1. Options query
    res_opts = client.get("/api/rules/favored-class-options?race=Human&char_class=Fighter")
    assert res_opts.status_code == 200
    opts = res_opts.json()
    assert any(o["key"] == "hp" for o in opts)
    assert any(o["key"] == "skill" for o in opts)
    assert any(o["key"] == "human_fighter_cmd" for o in opts)

    # 2. Evaluate POST
    res_eval = client.post("/api/rules/evaluate-fcb", json={
        "character": {
            "race": "Dwarf",
            "class": "Fighter",
            "level": 3,
            "favored_class_bonuses": [{"level": 1, "choice": "hp"}, {"level": 2, "choice": "hp"}]
        }
    })
    assert res_eval.status_code == 200
    data_e = res_eval.json()
    assert data_e["hp_bonus"] == 2
    assert data_e["unallocated_count"] == 1
