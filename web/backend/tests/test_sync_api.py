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
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app import models as orm_models  # Register tables without shadowing the FastAPI app.


@pytest.fixture(autouse=True)
def isolated_sync_database():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    def test_session():
        with factory() as session:
            yield session

    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = test_session
    try:
        yield
    finally:
        if previous is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous
        engine.dispose()

client = TestClient(app)


@pytest.mark.parametrize("deleted", [False, True])
def test_legacy_push_is_rejected_without_changing_records(deleted):
    registration = client.post("/api/auth/register", json={"username": "legacy_user", "password": "Password123!"})
    headers = {"Authorization": "Bearer " + registration.json()["access_token"]}
    response = client.post("/api/sync", headers=headers, json={
        "dirty_characters": [{"server_id": "legacy-id", "system": "pf1e",
                              "name": "Legacy", "data": {}, "is_deleted": deleted}],
    })
    assert response.status_code == 426
    assert client.post("/api/sync/v2", headers=headers, json={}).json()["characters"] == []


def test_legacy_pull_remains_read_only_compatible():
    registration = client.post("/api/auth/register", json={"username": "pull_user", "password": "Password123!"})
    headers = {"Authorization": "Bearer " + registration.json()["access_token"]}
    created = client.post("/api/sync/v2", headers=headers, json={"operations": [{
        "operation_id": "create", "server_id": "pull-id", "base_revision": 0,
        "system": "pf1e", "name": "Character", "data": {},
    }]})
    assert created.status_code == 200
    response = client.post("/api/sync", headers=headers, json={})
    assert response.status_code == 200
    assert response.json()["updated_characters"][0]["revision"] == 1
