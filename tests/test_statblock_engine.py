"""
Unit Tests for PF1e Official Paizo Statblock & JSON Portability Engine
======================================================================
Verifies:
- Standard Paizo monster/character statblock formatting
- Defense, Offense, and Statistics section compilation
- Markdown and Plain Text formatting outputs
- JSON Export and Import schema validation
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.statblock_engine import (
    generate_paizo_statblock,
    export_character_json,
    validate_imported_character_json
)
from fastapi.testclient import TestClient
from app.main import app


def test_paizo_statblock_generation_sections():
    """Verify Defense, Offense, and Statistics are correctly formatted."""
    char = {
        "name": "Valeros",
        "race": "Human",
        "class": "Fighter",
        "level": 3,
        "alignment": "NG",
        "scores": {"Strength": 16, "Dexterity": 14, "Constitution": 14, "Intelligence": 10, "Wisdom": 12, "Charisma": 10},
        "feats": [{"isim": "Power Attack"}, {"isim": "Weapon Focus (Longsword)"}],
        "weapons": [{"name": "Longsword", "damage": "1d8", "crit": "19-20/x2"}],
        "languages": ["Common"],
        "inventory": [{"name": "Breastplate"}]
    }

    res = generate_paizo_statblock(char)
    assert "plain_text" in res
    assert "markdown" in res

    text = res["plain_text"]
    assert "VALEROS CR 3" in text
    assert "DEFENSE" in text
    assert "OFFENSE" in text
    assert "STATISTICS" in text
    assert "Str 16 (+3)" in text
    assert "Power Attack" in text
    assert "Breastplate" in text


def test_export_character_json():
    """Verify structured export format."""
    char = {"name": "Seoni", "race": "Human", "class": "Sorcerer", "level": 5}
    exp = export_character_json(char)

    assert exp["schema_version"] == "2.0"
    assert exp["character"]["name"] == "Seoni"
    assert "export_date" in exp


def test_validate_imported_character_json():
    """Verify import validation handles valid and invalid payloads."""
    # Valid
    v1 = validate_imported_character_json({"name": "Ezren", "race": "Human", "class": "Wizard"})
    assert v1["is_valid"] is True

    # Invalid (missing race and class)
    v2 = validate_imported_character_json({"name": "Incomplete"})
    assert v2["is_valid"] is False
    assert len(v2["warnings"]) >= 2


def test_statblock_backend_api():
    """Verify /api/rules/generate-statblock and /api/rules/validate-character-json."""
    client = TestClient(app)

    # 1. Statblock POST
    res_sb = client.post("/api/rules/generate-statblock", json={
        "character": {
            "name": "Kyra",
            "race": "Human",
            "class": "Cleric",
            "level": 1,
            "alignment": "NG",
            "scores": {"Strength": 14, "Dexterity": 10, "Constitution": 14, "Intelligence": 10, "Wisdom": 16, "Charisma": 12}
        }
    })
    assert res_sb.status_code == 200
    assert "KYRA CR 1" in res_sb.json()["plain_text"]

    # 2. Validate JSON POST
    res_val = client.post("/api/rules/validate-character-json", json={
        "json_data": {"character": {"name": "Harsk", "race": "Dwarf", "class": "Ranger"}}
    })
    assert res_val.status_code == 200
    assert res_val.json()["is_valid"] is True
