"""
Unit Tests for Sync Engine API
==============================
FastAPI /api/sync ve JWT Auth entegrasyon birim testleri.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_and_sync_pipeline():
    # 1. Register a test user
    username = "sync_test_user"
    password = "sync_password_123"

    reg_resp = client.post("/api/auth/register", json={"username": username, "password": password})
    assert reg_resp.status_code in (201, 400)  # 201 or 400 if already exists

    # 2. Login to get JWT access token
    login_resp = client.post("/api/auth/token", data={"username": username, "password": password})
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data

    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Perform Sync with a dirty local character
    sync_payload = {
        "last_sync_timestamp": None,
        "dirty_characters": [
            {
                "server_id": "test-uuid-9999",
                "system": "pathfinder1e",
                "name": "Sync Test Valeros",
                "data": {"race": "Human", "class": "Fighter", "level": 3},
                "updated_at": "2026-07-21T13:40:00Z",
                "is_deleted": False
            }
        ]
    }

    sync_resp = client.post("/api/sync", json=sync_payload, headers=headers)
    assert sync_resp.status_code == 200

    sync_data = sync_resp.json()
    assert sync_data["status"] == "ok"
    assert "synced_at" in sync_data
    assert len(sync_data["updated_characters"]) >= 1

    matched = [c for c in sync_data["updated_characters"] if c.get("server_id") == "test-uuid-9999"]
    assert len(matched) == 1
    assert matched[0]["name"] == "Sync Test Valeros"
