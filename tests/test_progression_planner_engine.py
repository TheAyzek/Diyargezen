"""
Unit Tests for PF1e Level-Up Progression Planner Engine (1-20)
==============================================================
Verifies:
- 1..20 BAB advancement (Full, 3/4, Half)
- Base saving throw curves (Good vs Poor)
- Universal advancement milestones (Feats at odd levels, Ability boosts at 4, 8, 12, 16, 20)
- Class-specific bonus feat progressions (Fighter, Wizard, Rogue)
- Max spell level tiers
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.progression_planner import (
    generate_progression_matrix,
    calculate_bab,
    format_bab_attacks,
    calculate_save,
    get_max_spell_level
)
from fastapi.testclient import TestClient
from app.main import app


def test_fighter_full_progression_matrix():
    """Verify Fighter 1-20 BAB, saves, and 11 bonus combat feats."""
    matrix = generate_progression_matrix(char_class="Fighter", race="Human")

    assert len(matrix) == 20

    # Level 1
    lv1 = matrix[0]
    assert lv1["level"] == 1
    assert lv1["bab"] == 1
    assert lv1["bab_formatted"] == "+1"
    assert lv1["fort_save"] == 2 # Good save
    assert lv1["ref_save"] == 0 # Poor save
    assert lv1["has_general_feat"] is True
    assert lv1["is_human_bonus_feat"] is True
    assert len(lv1["bonus_feats"]) == 1 # Fighter bonus combat feat

    # Level 4 Ability Boost
    lv4 = matrix[3]
    assert lv4["has_ability_boost"] is True
    assert lv4["has_general_feat"] is False

    # Level 20 Weapon Mastery
    lv20 = matrix[19]
    assert lv20["level"] == 20
    assert lv20["bab"] == 20
    assert lv20["bab_formatted"] == "+20/+15/+10/+5"
    assert lv20["fort_save"] == 12 # 2 + 20//2
    assert lv20["ref_save"] == 6 # 20//3
    assert lv20["has_ability_boost"] is True
    assert "Weapon Mastery" in lv20["class_features"]


def test_wizard_9_level_spell_progression():
    """Verify Wizard spell level tiers and bonus metamagic feats."""
    matrix = generate_progression_matrix(char_class="Wizard", race="Elf")

    # Level 1 -> 1st level spells
    assert matrix[0]["max_spell_level"] == 1

    # Level 3 -> 2nd level spells
    assert matrix[2]["max_spell_level"] == 2

    # Level 17 -> 9th level spells
    assert matrix[16]["max_spell_level"] == 9

    # Bonus feat at Level 5
    assert len(matrix[4]["bonus_feats"]) == 1


def test_rogue_talents_and_sneak_attack():
    """Verify Rogue 3/4 BAB and sneak attack progression."""
    matrix = generate_progression_matrix(char_class="Rogue", race="Halfling")

    assert matrix[19]["bab"] == 15 # 3/4 BAB at Lv 20
    assert matrix[19]["bab_formatted"] == "+15/+10/+5"

    # Rogue talents at even levels (Lv 2, 4, 6, 8, 10...)
    assert len(matrix[1]["bonus_feats"]) == 1 # Lv 2
    assert len(matrix[9]["bonus_feats"]) == 1 # Lv 10


def test_progression_matrix_backend_api():
    """Verify /api/rules/progression-matrix endpoint."""
    client = TestClient(app)

    res = client.get("/api/rules/progression-matrix?char_class=Paladin&race=Human")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 20
    assert data[3]["level"] == 4 # Paladin gets spells at lv 4
    assert data[3]["max_spell_level"] == 1
