"""
Unit Tests for PF1e Alignment & Class Restrictions Engine
==========================================================
Verifies:
- Paladin LG restriction
- Monk Lawful restriction (LG, LN, LE)
- Barbarian Non-Lawful restriction (NG, CG, TN, CN, NE, CE)
- Druid Neutral axis restriction (NG, LN, TN, CN, NE)
- Cleric Deity One-Step Rule (Sarenrae, Pharasma, Asmodeus)
- Permissive unrestricted classes (Fighter, Wizard, Rogue)
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.alignment_restrictions import (
    validate_character_alignment,
    is_within_one_step,
    get_all_alignment_rules
)
from fastapi.testclient import TestClient
from app.main import app


def test_paladin_lawful_good_rule():
    """Verify Paladin is strictly Lawful Good."""
    # Valid
    val_lg = validate_character_alignment("Paladin", "LG")
    assert val_lg["is_valid"] is True
    assert val_lg["allowed_alignments"] == ["LG"]

    # Invalid (CG, LE, TN)
    val_cg = validate_character_alignment("Paladin", "CG")
    assert val_cg["is_valid"] is False
    assert any("Lawful Good" in w for w in val_cg["warnings"])

    val_le = validate_character_alignment("Paladin", "LE")
    assert val_le["is_valid"] is False


def test_monk_lawful_rule():
    """Verify Monk must be Lawful (LG, LN, LE)."""
    assert validate_character_alignment("Monk", "LG")["is_valid"] is True
    assert validate_character_alignment("Monk", "LN")["is_valid"] is True
    assert validate_character_alignment("Monk", "LE")["is_valid"] is True

    # Non-lawful
    assert validate_character_alignment("Monk", "CG")["is_valid"] is False
    assert validate_character_alignment("Monk", "TN")["is_valid"] is False
    assert validate_character_alignment("Monk", "CN")["is_valid"] is False


def test_barbarian_non_lawful_rule():
    """Verify Barbarian must be Non-Lawful."""
    assert validate_character_alignment("Barbarian", "CG")["is_valid"] is True
    assert validate_character_alignment("Barbarian", "CN")["is_valid"] is True
    assert validate_character_alignment("Barbarian", "TN")["is_valid"] is True

    # Lawful
    assert validate_character_alignment("Barbarian", "LG")["is_valid"] is False
    assert validate_character_alignment("Barbarian", "LN")["is_valid"] is False


def test_druid_neutral_axis_rule():
    """Verify Druid must have Neutral on at least one axis."""
    assert validate_character_alignment("Druid", "NG")["is_valid"] is True
    assert validate_character_alignment("Druid", "LN")["is_valid"] is True
    assert validate_character_alignment("Druid", "TN")["is_valid"] is True
    assert validate_character_alignment("Druid", "CN")["is_valid"] is True
    assert validate_character_alignment("Druid", "NE")["is_valid"] is True

    # Extreme non-neutrals (LG, CG, LE, CE)
    assert validate_character_alignment("Druid", "LG")["is_valid"] is False
    assert validate_character_alignment("Druid", "CG")["is_valid"] is False
    assert validate_character_alignment("Druid", "LE")["is_valid"] is False
    assert validate_character_alignment("Druid", "CE")["is_valid"] is False


def test_cleric_deity_one_step_rule():
    """Verify Cleric one-step alignment rule."""
    # Sarenrae is NG -> LG, NG, CG, TN are valid
    assert validate_character_alignment("Cleric", "NG", deity_name="Sarenrae")["is_valid"] is True
    assert validate_character_alignment("Cleric", "LG", deity_name="Sarenrae")["is_valid"] is True
    assert validate_character_alignment("Cleric", "CG", deity_name="Sarenrae")["is_valid"] is True
    assert validate_character_alignment("Cleric", "TN", deity_name="Sarenrae")["is_valid"] is True
    # LE is 2 steps away -> invalid
    assert validate_character_alignment("Cleric", "LE", deity_name="Sarenrae")["is_valid"] is False

    # Pharasma is TN -> LN, NG, TN, CN, NE are valid
    assert validate_character_alignment("Cleric", "TN", deity_name="Pharasma")["is_valid"] is True
    assert validate_character_alignment("Cleric", "LN", deity_name="Pharasma")["is_valid"] is True
    assert validate_character_alignment("Cleric", "LG", deity_name="Pharasma")["is_valid"] is False


def test_unrestricted_classes():
    """Verify Fighter, Wizard, Rogue have no alignment restrictions."""
    for c in ["Fighter", "Wizard", "Rogue", "Ranger", "Sorcerer"]:
        assert validate_character_alignment(c, "CE")["is_valid"] is True
        assert validate_character_alignment(c, "LG")["is_valid"] is True


def test_alignment_backend_api():
    """Verify /api/rules/class-alignment-rules and /api/rules/validate-alignment."""
    client = TestClient(app)

    # 1. Catalog
    res_cat = client.get("/api/rules/class-alignment-rules")
    assert res_cat.status_code == 200
    data = res_cat.json()
    assert "paladin" in data["class_rules"]
    assert "sarenrae" in data["deities"]

    # 2. Validate POST
    res_val = client.post("/api/rules/validate-alignment", json={
        "char_class": "Paladin",
        "alignment": "CE"
    })
    assert res_val.status_code == 200
    assert res_val.json()["is_valid"] is False
