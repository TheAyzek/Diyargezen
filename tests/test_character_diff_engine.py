import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.character_diff import compute_character_diff
from fastapi.testclient import TestClient
from app.main import app


def test_character_level_up_diff_same_character():
    """Verify level 1 vs level 5 Fighter diff reflects BAB, HP, Feat, and Save progressions."""
    char_lv1 = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "race": "Human",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 12, "charisma": 10},
        "feats": ["Weapon Focus (Longsword)", "Power Attack"],
        "equipment": [{"name": "Longsword", "price": 15, "quantity": 1}],
        "skill_ranks": {"Climb": 1, "Swim": 1}
    }

    char_lv5 = {
        "name": "Valeros Veteran",
        "system": "pathfinder1e",
        "level": 5,
        "class": "Fighter",
        "race": "Human",
        "abilities": {"strength": 17, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 12, "charisma": 10},
        "feats": ["Weapon Focus (Longsword)", "Power Attack", "Weapon Specialization (Longsword)", "Cleave"],
        "equipment": [
            {"name": "Longsword", "price": 15, "quantity": 1},
            {"name": "+1 Mithral Breastplate", "price": 4200, "quantity": 1},
            {"name": "Belt of Giant Strength +2", "price": 4000, "quantity": 1}
        ],
        "skill_ranks": {"Climb": 5, "Swim": 5, "Perception": 3}
    }

    diff = compute_character_diff(char_lv1, char_lv5)

    # 1. Progression
    prog = diff["progression"]
    assert prog["level_a"] == 1
    assert prog["level_b"] == 5
    assert prog["level_delta"] == 4
    assert prog["level_delta_str"] == "+4"

    # 2. Abilities (Strength went from 16 to 17 + 2 belt = 19)
    ab = diff["abilities"]
    assert ab["Strength"]["score_delta"] > 0
    assert ab["Strength"]["mod_delta"] >= 1

    # 3. Combat Metrics
    combat = diff["combat"]
    assert combat["bab"]["val_a"] == 1
    assert combat["bab"]["val_b"] == 5
    assert combat["bab"]["delta"] == 4
    assert combat["hit_points"]["delta"] > 20
    assert combat["saving_throws"]["Fortitude"]["delta"] >= 2

    # 4. Feats Added
    feats = diff["feats"]
    assert "Weapon Specialization (Longsword)" in feats["added"]
    assert "Cleave" in feats["added"]
    assert "Weapon Focus (Longsword)" in feats["common"]
    assert len(feats["removed"]) == 0

    # 5. Skills
    skills = diff["skills"]
    assert "Climb" in skills
    assert skills["Climb"]["rank_delta"] == 4
    assert "Perception" in skills
    assert skills["Perception"]["rank_delta"] == 3

    # 6. Wealth & Gear
    wealth = diff["wealth_and_gear"]
    assert wealth["total_wealth_gp"]["delta"] > 5000
    assert len(wealth["items_added"]) >= 2


def test_character_diff_two_different_classes():
    """Verify comparing a Fighter and a Wizard highlights distinct BAB, HP, and spellcasting diffs."""
    char_fighter = {
        "name": "Valeros Fighter",
        "system": "pathfinder1e",
        "level": 5,
        "class": "Fighter",
        "abilities": {"strength": 18, "intelligence": 10}
    }

    char_wizard = {
        "name": "Ezren Wizard",
        "system": "pathfinder1e",
        "level": 5,
        "class": "Wizard",
        "abilities": {"strength": 10, "intelligence": 18}
    }

    diff = compute_character_diff(char_fighter, char_wizard)

    # BAB: Fighter (5) -> Wizard (2) = -3 delta
    assert diff["combat"]["bab"]["delta"] == -3
    assert diff["combat"]["bab"]["delta_str"] == "-3"

    # Intelligence: 10 -> 18 = +8 delta
    assert diff["abilities"]["Intelligence"]["score_delta"] == 8

    # Spellcasting: Wizard has spells
    assert diff["spellcasting"]["has_spellcasting_b"] is True
    assert diff["spellcasting"]["caster_level"]["val_b"] == 5


def test_character_diff_backend_api():
    """Verify /api/rules/character-diff API endpoint."""
    client = TestClient(app)

    char_a = {
        "name": "Alice Lv1",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Rogue",
        "abilities": {"dexterity": 16}
    }
    char_b = {
        "name": "Alice Lv2",
        "system": "pathfinder1e",
        "level": 2,
        "class": "Rogue",
        "abilities": {"dexterity": 16}
    }

    response = client.post("/api/rules/character-diff", json={
        "character_a": char_a,
        "character_b": char_b
    })

    assert response.status_code == 200
    data = response.json()
    assert data["progression"]["level_delta"] == 1
    assert "combat" in data
    assert "abilities" in data
