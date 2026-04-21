import pytest
from fastapi.testclient import TestClient

from database import init_db
from main import app


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", test_db)
    init_db()


client = TestClient(app)

SAMPLE = {
    "name": "Alice",
    "email": "alice@example.com",
    "hobbies": ["painting", "cycling"],
    "interests": ["technology", "music"],
}


def test_create_profile():
    r = client.post("/api/profiles", json=SAMPLE)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Alice"
    assert data["hobbies"] == ["painting", "cycling"]
    assert "id" in data


def test_list_profiles():
    client.post("/api/profiles", json=SAMPLE)
    r = client.get("/api/profiles")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_profile():
    created = client.post("/api/profiles", json=SAMPLE).json()
    r = client.get(f"/api/profiles/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == SAMPLE["email"]


def test_duplicate_email_rejected():
    client.post("/api/profiles", json=SAMPLE)
    r = client.post("/api/profiles", json=SAMPLE)
    assert r.status_code == 409


def test_delete_profile():
    created = client.post("/api/profiles", json=SAMPLE).json()
    r = client.delete(f"/api/profiles/{created['id']}")
    assert r.status_code == 204
    r = client.get(f"/api/profiles/{created['id']}")
    assert r.status_code == 404


def test_get_missing_profile():
    r = client.get("/api/profiles/9999")
    assert r.status_code == 404
