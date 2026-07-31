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
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    html_resp = client.get("/")
    assert html_resp.status_code == 200


def test_list_systems():
    response = client.get("/api/systems")
    assert response.status_code == 200
    systems = response.json()
    assert len(systems) > 0
    assert any(s["key"] == "pf1e" for s in systems)

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
    assert "data" in res_data
    # Level 4 Fighter with Full BAB has BAB +4
    assert res_data["data"]["bab"] == 4
    # Melee attack is BAB (4) + Strength mod (3) = 7
    assert res_data["data"]["melee_attack_bonus"] == 7

def test_validate_pf1e_warning():
    payload = {
        "data": {
            "system": "pf1e",
            "name": "Invalid Stat Fighter",
            "level": 1,
            "abilities": {
                "strength": 25,  # PF1e point buy standard range at level 1 is 7-18
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
    assert any("7-18" in w for w in res_data["warnings"])
