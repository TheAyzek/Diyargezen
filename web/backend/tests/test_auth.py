import sys
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

import pytest


@pytest.fixture(autouse=True)
def isolated_database(request):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    try:
        if request.node.name not in {"test_register_success", "test_register_invalid_inputs"}:
            from app.services.auth_service import AuthService
            with TestingSessionLocal() as session:
                AuthService.register_user(session, "testuser", "securepassword")
        yield
    finally:
        if previous is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous
        Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_register_success():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "securepassword"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "testuser"

def test_register_duplicate_username():
    # Attempt to register the same username again
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "anotherpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()

def test_register_invalid_inputs():
    # Username too short
    response = client.post(
        "/api/auth/register",
        json={"username": "us", "password": "password"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Password too short
    response = client.post(
        "/api/auth/register",
        json={"username": "user", "password": "123"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_json_success():
    response = client.post(
        "/api/auth/login-json",
        json={"username": "testuser", "password": "securepassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "testuser"

def test_login_json_wrong_password():
    response = client.post(
        "/api/auth/login-json",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect username or password" in response.json()["detail"].lower()

def test_login_form_success():
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "securepassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "testuser"

def test_access_protected_endpoint():
    # Login to get token
    login_resp = client.post(
        "/api/auth/login-json",
        json={"username": "testuser", "password": "securepassword"}
    )
    token = login_resp.json()["access_token"]
    
    # Request without token should fail
    resp_no_auth = client.get("/api/characters")
    assert resp_no_auth.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Request with valid token should succeed (even if character list is empty)
    headers = {"Authorization": f"Bearer {token}"}
    resp_auth = client.get("/api/characters", headers=headers)
    assert resp_auth.status_code == status.HTTP_200_OK
    assert isinstance(resp_auth.json(), list)


@pytest.mark.parametrize("token", ["offline-guest-token", "offline_guest_token", "invalid"])
def test_synthetic_guest_tokens_cannot_read_or_sync_or_create_users(token):
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/characters", headers=headers).status_code == 401
    assert client.post("/api/sync/v2", headers=headers, json={"operations": []}).status_code == 401
    assert client.post("/api/characters", headers=headers, json={
        "system": "pf1e", "name": "Must not be created", "data": {},
    }).status_code == 401
    with TestingSessionLocal() as session:
        assert session.query(User).count() == 1
        assert session.query(Character).count() == 0


def test_legacy_guest_password_and_signed_token_are_disabled_without_deleting_data():
    from app.services.auth_service import AuthService
    with TestingSessionLocal() as session:
        guest = User(username="Yerel Gezgin", hashed_password=AuthService.hash_password("local_guest_password"), created_at="2026-01-01T00:00:00+00:00")
        session.add(guest)
        session.flush()
        record = Character(user_id=guest.id, name="Legacy hero", system="pf1e", data='{"name":"Legacy hero"}', created_at=guest.created_at, updated_at=guest.created_at)
        session.add(record)
        session.commit()
        owner_id, record_id = guest.id, record.id
    credentials = {"username": "Yerel Gezgin", "password": "local_guest_password"}
    assert client.post("/api/auth/login-json", json=credentials).status_code == 401
    assert client.post("/api/auth/token", data=credentials).status_code == 401
    token = AuthService.create_access_token({"sub": "Yerel Gezgin"})
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/api/characters/{record_id}", headers=headers).status_code == 401
    assert client.post("/api/sync/v2", headers=headers, json={"operations": []}).status_code == 401
    assert client.delete(f"/api/characters/{record_id}", headers={**headers, "If-Match": "1"}).status_code == 401
    personal = client.post("/api/auth/login-json", json={"username": "testuser", "password": "securepassword"}).json()["access_token"]
    assert client.get(f"/api/characters/{record_id}", headers={"Authorization": f"Bearer {personal}"}).status_code == 403
    with TestingSessionLocal() as session:
        preserved = session.get(Character, record_id)
        assert preserved.user_id == owner_id
        assert preserved.data == '{"name":"Legacy hero"}'
        assert session.get(User, owner_id).username == "Yerel Gezgin"


@pytest.mark.parametrize("name", ["Yerel Gezgin", "yerel gezgin", " Yerel Gezgin "])
def test_reserved_guest_name_cannot_be_registered(name):
    assert client.post("/api/auth/register", json={"username": name, "password": "password"}).status_code == 400
    with TestingSessionLocal() as session:
        assert session.query(User).count() == 1
