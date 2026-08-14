"""
Unit Tests for Character Showcase Card Engine
=============================================
Verifies:
- Data serialization and formatting for card export
- Ability matrix and combat statistics
- Backend API /api/rules/character-card
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.character_card import generate_character_card_data
from fastapi.testclient import TestClient
from app.main import app


def test_character_card_data_generation():
    """Verify structured showcase card data format."""
    character = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Fighter",
        "level": 3,
        "alignment": "NG",
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 10
        },
        "equipment": [
            {"isim": "Longsword", "kategori": "weapons_martial", "hasar": "1d8", "is_equipped": True}
        ]
    }

    card = generate_character_card_data(character)

    assert card["identity"]["name"] == "Valeros"
    assert card["identity"]["race"] == "Human"
    assert card["identity"]["level"] == 3
    assert len(card["abilities"]) == 6

    str_entry = next(a for a in card["abilities"] if a["name"] == "STR")
    # Human gets +2 to one ability score (default Str) -> 16 + 2 = 18 (+4)
    assert str_entry["score"] == 18
    assert str_entry["modifier"] == "+4"

    assert card["combat"]["hp"] > 0
    assert card["combat"]["ac"] >= 10
    assert card["combat"]["bab"] == "+3"
    assert "fortitude" in card["saves"]


def test_character_card_backend_api():
    """Verify POST /api/rules/character-card endpoint."""
    client = TestClient(app)

    res = client.post("/api/rules/character-card", json={
        "character": {
            "name": "Seoni",
            "system": "pathfinder1e",
            "race": "Human",
            "class": "Sorcerer",
            "level": 1,
            "abilities": {"charisma": 18, "dexterity": 14}
        }
    })

    assert res.status_code == 200
    data = res.json()
    assert data["identity"]["name"] == "Seoni"
    assert data["identity"]["class"] == "Sorcerer"
    assert data["combat"]["hp"] > 0
