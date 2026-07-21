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

app.dependency_overrides[get_db] = override_get_db

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
