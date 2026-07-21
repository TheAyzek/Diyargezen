"""
Unit Tests for Desktop Offline-First Engine & Sync Protocol
===========================================================
Yerel SQLite 'is_dirty' kuyruğu, 'updated_at' çakışma çözümü ve
çevrimdışı kayıt işlemlerinin testi.
"""

import os
from pathlib import Path
from desktop import local_db


def test_local_db_offline_crud(tmp_path: Path):
    db_path = tmp_path / "test_offline.db"
    local_db.init_local_db(db_path)

    # 1. Save local character in offline mode
    char_data = {
        "system": "PATHFINDER1E",
        "name": "Offline Valeros",
        "race": "Human",
        "class": "Fighter"
    }

    rec1 = local_db.save_local_character(db_path, char_data)
    assert rec1.id is not None
    assert rec1.is_dirty is True
    assert rec1.name == "Offline Valeros"

    # 2. Check dirty queue
    dirty_list = local_db.get_dirty_characters(db_path)
    assert len(dirty_list) == 1
    assert dirty_list[0].server_id == rec1.server_id

    # 3. Apply sync response
    synced_item = {
        "server_id": rec1.server_id,
        "system": "PATHFINDER1E",
        "name": "Offline Valeros (Synced)",
        "data": char_data,
        "created_at": rec1.created_at,
        "updated_at": rec1.updated_at,
        "is_deleted": False
    }
    local_db.apply_sync_response(db_path, [synced_item], [])

    # 4. Verify is_dirty is now False
    dirty_after = local_db.get_dirty_characters(db_path)
    assert len(dirty_after) == 0

    all_local = local_db.list_local_characters(db_path)
    assert len(all_local) == 1
    assert "Synced" in all_local[0].name


def test_local_auth_persistence(tmp_path: Path):
    db_path = tmp_path / "test_auth.db"
    local_db.init_local_db(db_path)

    assert local_db.get_local_auth(db_path) is None

    local_db.save_local_auth(db_path, "ayzek", "jwt_mock_token_123")
    auth_data = local_db.get_local_auth(db_path)
    assert auth_data is not None
    assert auth_data[0] == "ayzek"
    assert auth_data[1] == "jwt_mock_token_123"

    local_db.clear_local_auth(db_path)
    assert local_db.get_local_auth(db_path) is None
