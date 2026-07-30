import sys
import json
from pathlib import Path
from fastapi import status

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app

from sqlalchemy.pool import StaticPool

# Set up in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models so they are registered on Base.metadata before creating tables
from app.models.user import User, Character
from app.models.progression import LevelProgression

# Create tables in the in-memory database
Base.metadata.create_all(bind=engine)

# Override database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        db.execute(text("PRAGMA foreign_keys=ON"))
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_progression_workflow():
    # 1. Register and login User 1
    reg1 = client.post("/api/auth/register", json={"username": "user1", "password": "password1"})
    assert reg1.status_code == status.HTTP_201_CREATED
    token1 = reg1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2. Register and login User 2 (for ownership testing)
    reg2 = client.post("/api/auth/register", json={"username": "user2", "password": "password2"})
    assert reg2.status_code == status.HTTP_201_CREATED
    token2 = reg2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 3. Create a PF1e character for User 1
    initial_character = {
        "system": "pf1e",
        "name": "Valeros Test",
        "data": {
            "system": "pf1e",
            "name": "Valeros Test",
            "level": 1,
            "class": "Fighter",
            "race": "Human",
            "hit_points": 12,
            "abilities": {
                "strength": 16,
                "dexterity": 12,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 8
            },
            "skill_ranks": {
                "Climb": 1,
                "Swim": 1
            },
            "feats": ["Weapon Focus"],
            "class_data": {
                "hit_die": "10",
                "bab_progression": "full",
                "saving_throws": {
                    "fortitude": "good",
                    "reflex": "poor",
                    "will": "poor"
                }
            }
        }
    }
    
    char_res = client.post("/api/characters", json=initial_character, headers=headers1)
    assert char_res.status_code == status.HTTP_201_CREATED
    char_data = char_res.json()
    char_id = char_data["id"]
    
    # Check initial level 1 stats
    assert char_data["data"]["level"] == 1
    assert char_data["data"]["hit_points"] == 12
    # Base Attack Bonus (BAB) at level 1 Fighter should be 1
    assert char_data["data"]["bab"] == 1

    # 4. Attempt Level-Up on User 1's character using User 2's token (should fail)
    level_up_payload = {
        "class_name": "Fighter",
        "hp_added": 6,
        "skill_ranks": {
            "Climb": 1,
            "Survival": 1
        },
        "feats": ["Power Attack"],
        "ability_increase": None,
        "spells_learned": []
    }
    
    lvl_err_res = client.post(f"/api/characters/{char_id}/level-up", json=level_up_payload, headers=headers2)
    assert lvl_err_res.status_code == status.HTTP_403_FORBIDDEN

    # 5. Level Up User 1's character (User 1 token) - Level 2
    lvl_ok_res = client.post(f"/api/characters/{char_id}/level-up", json=level_up_payload, headers=headers1)
    assert lvl_ok_res.status_code == status.HTTP_200_OK
    lvl_data = lvl_ok_res.json()["data"]
    
    # Verify level 2 updates
    assert lvl_data["level"] == 2
    # HP should increase by hp_added (6) + constitution modifier (14 con = +2 mod) = 8
    # 12 (initial) + 8 = 20 HP
    assert lvl_data["hit_points"] == 20
    # Skill ranks updated: Climb (1 + 1 = 2), Swim (1), Survival (1)
    assert lvl_data["skill_ranks"]["Climb"] == 2
    assert lvl_data["skill_ranks"]["Swim"] == 1
    assert lvl_data["skill_ranks"]["Survival"] == 1
    # Feats list should now contain "Power Attack"
    assert "Power Attack" in lvl_data["feats"]
    # BAB at level 2 Fighter should be 2
    assert lvl_data["bab"] == 2

    # 6. Attempt duplicate Level-Up (should fail because we manually seed level 3 progression first)
    import datetime
    db = TestingSessionLocal()
    db.add(LevelProgression(
        character_id=char_id,
        level=3,
        class_name="Fighter",
        choices="{}",
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    ))
    db.commit()
    db.close()

    lvl_dup_res = client.post(f"/api/characters/{char_id}/level-up", json=level_up_payload, headers=headers1)
    assert lvl_dup_res.status_code == status.HTTP_400_BAD_REQUEST

    # Clean up the dummy Level 3 progression record so we can test undoing Level 2
    db = TestingSessionLocal()
    db.query(LevelProgression).filter(
        LevelProgression.character_id == char_id,
        LevelProgression.level == 3
    ).delete()
    db.commit()
    db.close()

    # 7. Attempt Level-Undo using User 2's token (should fail)
    undo_err_res = client.post(f"/api/characters/{char_id}/level-undo", headers=headers2)
    assert undo_err_res.status_code == status.HTTP_403_FORBIDDEN

    # 8. Undo Level-Up (User 1 token)
    undo_ok_res = client.post(f"/api/characters/{char_id}/level-undo", headers=headers1)
    assert undo_ok_res.status_code == status.HTTP_200_OK
    undo_data = undo_ok_res.json()["data"]
    
    # Verify character returned to level 1 stats
    assert undo_data["level"] == 1
    assert undo_data["hit_points"] == 12
    assert undo_data["skill_ranks"]["Climb"] == 1
    assert "Survival" not in undo_data["skill_ranks"] or undo_data["skill_ranks"]["Survival"] == 0
    assert "Power Attack" not in undo_data["feats"]
    assert undo_data["bab"] == 1
    
    # 9. Try undoing level 1 character (should fail since Level 1 is base level)
    undo_base_res = client.post(f"/api/characters/{char_id}/level-undo", headers=headers1)
    assert undo_base_res.status_code == status.HTTP_400_BAD_REQUEST
