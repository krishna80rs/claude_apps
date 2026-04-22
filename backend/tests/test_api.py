import json

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


def post_profile(name="Alice", email="alice@example.com", extra=None):
    data = {
        "name": name,
        "email": email,
        "hobbies": json.dumps(["painting", "cycling"]),
        "interests": json.dumps(["technology", "music"]),
        **(extra or {}),
    }
    return client.post("/api/profiles", data=data)


def test_create_profile():
    r = post_profile()
    assert r.status_code == 201
    d = r.json()
    assert d["name"] == "Alice"
    assert d["hobbies"] == ["painting", "cycling"]
    assert "id" in d
    assert d["document_name"] is None


def test_list_profiles():
    post_profile()
    r = client.get("/api/profiles")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_profile():
    created = post_profile().json()
    r = client.get(f"/api/profiles/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == "alice@example.com"


def test_duplicate_email_rejected():
    post_profile()
    r = post_profile()
    assert r.status_code == 409


def test_delete_profile():
    created = post_profile().json()
    r = client.delete(f"/api/profiles/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"/api/profiles/{created['id']}").status_code == 404


def test_get_missing_profile():
    assert client.get("/api/profiles/9999").status_code == 404


def test_upload_document():
    r = client.post(
        "/api/profiles",
        data={
            "name": "Bob",
            "email": "bob@example.com",
            "hobbies": json.dumps(["reading"]),
            "interests": json.dumps(["science"]),
        },
        files={"document": ("cv.pdf", b"%PDF fake content", "application/pdf")},
    )
    assert r.status_code == 201
    assert r.json()["document_name"] == "cv.pdf"
    dl = client.get(f"/api/profiles/{r.json()['id']}/document")
    assert dl.status_code == 200
    assert dl.content == b"%PDF fake content"
