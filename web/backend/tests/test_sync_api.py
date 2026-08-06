"""
Unit Tests for Sync Engine API
==============================
FastAPI /api/sync ve JWT Auth entegrasyon birim testleri.
Çevrimdışı senkronizasyon, LWW çakışma çözümü ve Soft Delete doğrulamaları.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_and_sync_pipeline():
    # 1. Register a test user
    username = "sync_test_user_unique"
    password = "Password123!"

    reg_resp = client.post("/api/auth/register", json={"username": username, "password": password})
    assert reg_resp.status_code in (201, 400, 422)

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


def test_sync_lww_and_soft_delete():
    # 1. Register/login test user
    username = "sync_lww_user_unique"
    password = "Password123!"

    client.post("/api/auth/register", json={"username": username, "password": password})
    login_resp = client.post("/api/auth/token", data={"username": username, "password": password})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    server_id = "test-uuid-lww-100"

    # Step A: Push initial version (v1) with timestamp T1
    p1 = {
        "last_sync_timestamp": None,
        "dirty_characters": [
            {
                "server_id": server_id,
                "system": "pathfinder1e",
                "name": "Initial Ezren",
                "data": {"class": "Wizard", "level": 1},
                "updated_at": "2026-08-01T10:00:00Z",
                "is_deleted": False
            }
        ]
    }
    res1 = client.post("/api/sync", json=p1, headers=headers)
    assert res1.status_code == 200

    # Step B: Push older version (v0) with timestamp T0 < T1 -> LWW should ignore update
    p_old = {
        "last_sync_timestamp": None,
        "dirty_characters": [
            {
                "server_id": server_id,
                "system": "pathfinder1e",
                "name": "Older Ezren",
                "data": {"class": "Wizard", "level": 1},
                "updated_at": "2026-07-01T10:00:00Z",
                "is_deleted": False
            }
        ]
    }
    res_old = client.post("/api/sync", json=p_old, headers=headers)
    assert res_old.status_code == 200
    m_old = [c for c in res_old.json()["updated_characters"] if c.get("server_id") == server_id]
    assert m_old[0]["name"] == "Initial Ezren"  # Retains T1 state

    # Step C: Push Soft Delete with timestamp T2 > T1
    p_del = {
        "last_sync_timestamp": None,
        "dirty_characters": [
            {
                "server_id": server_id,
                "system": "pathfinder1e",
                "name": "Initial Ezren",
                "data": {"class": "Wizard", "level": 1},
                "updated_at": "2026-08-02T10:00:00Z",
                "is_deleted": True
            }
        ]
    }
    res_del = client.post("/api/sync", json=p_del, headers=headers)
    assert res_del.status_code == 200

    # PULL since T1 should list server_id in deleted_server_ids
    pull_payload = {
        "last_sync_timestamp": "2026-08-01T12:00:00Z",
        "dirty_characters": []
    }
    res_pull = client.post("/api/sync", json=pull_payload, headers=headers)
    assert res_pull.status_code == 200
    pull_data = res_pull.json()
    assert server_id in pull_data["deleted_server_ids"]

