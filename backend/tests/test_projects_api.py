import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))
    from backend.main import app
    return TestClient(app)


def test_create_list_update_delete(client):
    created = client.post("/api/v1/projects/", json={"name": "My Proj", "description": "d"})
    assert created.status_code == 201
    pid = created.json()["id"]

    listed = client.get("/api/v1/projects/")
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "My Proj"

    updated = client.patch(f"/api/v1/projects/{pid}", json={"name": "Renamed"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Renamed"

    deleted = client.delete(f"/api/v1/projects/{pid}")
    assert deleted.status_code == 200
    assert client.get("/api/v1/projects/").json() == []


def test_get_project_detail(client):
    created = client.post("/api/v1/projects/", json={"name": "Detail", "description": "d"})
    pid = created.json()["id"]

    detail = client.get(f"/api/v1/projects/{pid}")

    assert detail.status_code == 200
    assert detail.json()["id"] == pid
    assert detail.json()["name"] == "Detail"


def test_missing_project_returns_404(client):
    assert client.get("/api/v1/projects/nope").status_code == 404
    assert client.patch("/api/v1/projects/nope", json={"name": "x"}).status_code == 404
    assert client.delete("/api/v1/projects/nope").status_code == 404


def test_empty_name_rejected(client):
    assert client.post("/api/v1/projects/", json={"name": ""}).status_code == 422


def test_create_project_with_task_type(client):
    response = client.post("/api/v1/projects/", json={
        "name": "Test CV",
        "description": "Desc",
        "task_type": "object_detection"
    })
    assert response.status_code == 201
    assert response.json()["task_type"] == "object_detection"
