import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_systems():
    response = client.get("/api/systems")
    assert response.status_code == 200
    systems = response.json()
    assert len(systems) > 0
    assert any(s["key"] == "dnd5e" for s in systems)

def test_recalculate_dnd5e():
    payload = {
        "data": {
            "system": "dnd5e",
            "name": "Test Wizard",
            "level": 5,
            "abilities": {
                "strength": 10,
                "dexterity": 14,
                "constitution": 12,
                "intelligence": 16,
                "wisdom": 10,
                "charisma": 8
            }
        }
    }
    response = client.post("/api/characters/recalculate", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "data" in res_data
    # Level 5 proficiency bonus is +3
    assert res_data["data"]["proficiency_bonus"] == 3
    # Intelligence modifier for 16 is +3
    assert res_data["data"]["ability_modifiers"]["Intelligence"] == 3

def test_validate_dnd5e_warning():
    payload = {
        "data": {
            "system": "dnd5e",
            "name": "Overleveled",
            "level": 25,  # D&D 5e level cap is 20
            "abilities": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        }
    }
    response = client.post("/api/characters/validate", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["valid"] is False
    assert len(res_data["warnings"]) > 0
    assert any("20" in w for w in res_data["warnings"])

def test_recalculate_pf1e():
    payload = {
        "data": {
            "system": "pf1e",
            "name": "Test Fighter",
            "level": 4,
            "abilities": {
                "strength": 16,
                "dexterity": 12,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 8
            },
            "class_data": {
                "bab_progression": "full",
                "saving_throws": {
                    "fortitude": "good",
                    "reflex": "poor",
                    "will": "poor"
                }
            }
        }
    }
    response = client.post("/api/characters/recalculate", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    # Level 4 Fighter with Full BAB has BAB +4
    assert res_data["data"]["bab"] == 4
    # Melee attack is BAB (4) + Strength mod (3) = 7
    assert res_data["data"]["melee_attack_bonus"] == 7

def test_recalculate_mm3e():
    payload = {
        "data": {
            "system": "mnm",
            "name": "Super Hero",
            "pl_value": 10,
            "abilities": {
                "strength": 12,  # 12 rank = 12 mod
                "stamina": 8,
                "agility": 4,
                "dexterity": 2,
                "fighting": 6,
                "intellect": 0,
                "awareness": 2,
                "presence": 0
            },
            "defenses": {
                "Dodge": 2,
                "Parry": 2,
                "Fortitude": 2,
                "Toughness": 2,
                "Will": 4
            }
        }
    }
    response = client.post("/api/characters/recalculate", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    # Dodge total = Agility (4) + Dodge bought (2) = 6
    assert res_data["data"]["defenses"]["Dodge"] == 6
    # Will total = Awareness (2) + Will bought (4) = 6
    assert res_data["data"]["defenses"]["Will"] == 6
