"""
Unit Tests for PF1e Languages & Linguistics Engine
==================================================
Verifies:
- Automatic racial languages (Common, Elven, Dwarven, etc.)
- INT bonus language slots
- Linguistics skill rank bonus language slots
- Druidic secret language restrictions
- Language quota overflow warnings
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.languages_engine import (
    evaluate_character_languages,
    get_languages_catalog
)
from rules.calculators import PF1e_Calculator
from fastapi.testclient import TestClient
from app.main import app


def test_human_int_bonus_languages():
    """Verify Human with INT 14 gets 1 Automatic (Common) + 2 Bonus = 3 Allowed."""
    character = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 14, "wisdom": 10, "charisma": 10},
        "languages": ["Common", "Draconic", "Orc"]
    }

    res = evaluate_character_languages(character)
    assert res["automatic_languages"] == ["Common"]
    assert res["int_modifier"] == 2
    assert res["bonus_slots"] == 2
    assert res["linguistics_slots"] == 0
    assert res["total_allowed_languages"] == 3
    assert res["total_selected_languages"] == 3
    assert res["unallocated_slots"] == 0
    assert res["is_valid"] is True
    assert len(res["warnings"]) == 0
    assert "Common" in res["selected_languages"]
    assert "Draconic" in res["selected_languages"]


def test_elf_linguistics_ranks_languages():
    """Verify Elf with INT 16 and 2 Linguistics ranks gets 2 Auto + 3 INT + 2 Ling = 7 Allowed."""
    character = {
        "name": "Merisiel",
        "system": "pathfinder1e",
        "race": "Elf",
        "class": "Rogue",
        "abilities": {"strength": 10, "dexterity": 18, "constitution": 12, "intelligence": 16, "wisdom": 12, "charisma": 10},
        "skill_ranks": {
            "Linguistics": 2,
            "Stealth": 5
        },
        "languages": ["Common", "Elven", "Celestial", "Draconic", "Sylvan", "Undercommon"]
    }

    res = evaluate_character_languages(character)
    assert res["automatic_languages"] == ["Common", "Elven"]
    assert res["int_modifier"] == 3
    assert res["bonus_slots"] == 3
    assert res["linguistics_slots"] == 2
    assert res["total_allowed_languages"] == 7
    assert res["total_selected_languages"] == 6
    assert res["unallocated_slots"] == 1
    assert res["is_valid"] is True


def test_druidic_secret_language_restriction():
    """Verify non-Druids cannot learn Druidic without warning, while Druids can."""
    fighter_char = {
        "name": "Fighter",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Fighter",
        "abilities": {"intelligence": 14},
        "languages": ["Common", "Druidic"]
    }
    f_res = evaluate_character_languages(fighter_char)
    assert f_res["is_valid"] is False
    assert any("Druidic" in w for w in f_res["warnings"])

    druid_char = {
        "name": "Druid",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Druid",
        "abilities": {"intelligence": 14},
        "languages": ["Common", "Druidic", "Sylvan"]
    }
    d_res = evaluate_character_languages(druid_char)
    assert d_res["is_valid"] is True
    assert len(d_res["warnings"]) == 0


def test_language_quota_overflow_warning():
    """Verify exceeding allowed languages produces an overflow warning."""
    character = {
        "name": "Overloaded",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Fighter",
        "abilities": {"intelligence": 10},  # 0 bonus -> 1 total allowed
        "languages": ["Common", "Elven", "Dwarven", "Orc"]  # 4 selected -> +3 over quota
    }
    res = evaluate_character_languages(character)
    assert res["total_allowed_languages"] == 1
    assert res["total_selected_languages"] == 4
    assert res["is_valid"] is False
    assert any("aşıldı" in w for w in res["warnings"])


def test_languages_backend_api():
    """Verify /api/rules/languages-catalog and /api/rules/evaluate-languages endpoints."""
    client = TestClient(app)

    # 1. Catalog query
    res_cat = client.get("/api/rules/languages-catalog")
    assert res_cat.status_code == 200
    data_c = res_cat.json()
    assert "Common" in data_c["languages"]
    assert "human" in data_c["race_configurations"]

    # 2. Evaluate POST
    res_eval = client.post("/api/rules/evaluate-languages", json={
        "character": {
            "race": "Dwarf",
            "class": "Cleric",
            "abilities": {"intelligence": 12},
            "languages": ["Common", "Dwarven", "Terran"]
        }
    })
    assert res_eval.status_code == 200
    data_e = res_eval.json()
    assert data_e["total_allowed_languages"] == 3 # 2 auto + 1 int
    assert data_e["total_selected_languages"] == 3
    assert data_e["is_valid"] is True
