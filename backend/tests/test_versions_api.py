from pathlib import Path
import json

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))
    from backend.main import app
    return TestClient(app)

@pytest.fixture
def project_id(client):
    response = client.post("/api/v1/projects/", json={"name": "Dataset Project"})
    assert response.status_code == 201
    return response.json()["id"]

def _upload_and_annotate(client, project_id):
    _, encoded = cv2.imencode(".png", np.zeros((8, 8, 3), dtype=np.uint8))
    client.post(
        f"/api/v1/projects/{project_id}/dataset/upload",
        files={"files": ("sample.png", encoded.tobytes(), "image/png")},
    )
    client.post(f"/api/v1/projects/{project_id}/dataset/auto-annotate")

def test_get_version(client, project_id):
    _upload_and_annotate(client, project_id)
    created = client.post(
        f"/api/v1/projects/{project_id}/versions",
        json={"name": "Version 1"}
    )
    assert created.status_code == 201
    version_id = created.json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}/versions/{version_id}")
    assert response.status_code == 200
    assert response.json()["id"] == version_id
    assert response.json()["name"] == "Version 1"

def test_get_version_not_found(client, project_id):
    response = client.get(f"/api/v1/projects/{project_id}/versions/nonexistent")
    assert response.status_code == 404

def test_delete_version(client, project_id):
    _upload_and_annotate(client, project_id)
    created = client.post(
        f"/api/v1/projects/{project_id}/versions",
        json={"name": "Version 1"}
    )
    version_id = created.json()["id"]

    delete_resp = client.delete(f"/api/v1/projects/{project_id}/versions/{version_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/api/v1/projects/{project_id}/versions/{version_id}")
    assert get_resp.status_code == 404

def test_delete_version_not_found(client, project_id):
    response = client.delete(f"/api/v1/projects/{project_id}/versions/nonexistent")
    assert response.status_code == 404

def test_create_version_with_description(client, project_id):
    _upload_and_annotate(client, project_id)
    created = client.post(
        f"/api/v1/projects/{project_id}/versions",
        json={"name": "Version 1", "description": "My test version"}
    )
    assert created.status_code == 201
    assert created.json()["description"] == "My test version"

def test_create_version_multiplier_cap(client, project_id):
    _upload_and_annotate(client, project_id)
    created = client.post(
        f"/api/v1/projects/{project_id}/versions",
        json={"name": "Version 1", "multiplier": 15}
    )
    assert created.status_code == 422

def test_create_version_no_annotated_assets(client, project_id):
    created = client.post(
        f"/api/v1/projects/{project_id}/versions",
        json={"name": "Version 1"}
    )
    assert created.status_code == 400
    assert created.json()["detail"] == "No annotated assets to version"

def test_create_version_builds_folder_structure(client, project_id, tmp_path):
    _upload_and_annotate(client, project_id)
    created = client.post(
        f"/api/v1/projects/{project_id}/versions",
        json={"name": "Version 1", "split": {"train": 100, "valid": 0, "test": 0}}
    )
    assert created.status_code == 201
    version_id = created.json()["id"]
    
    version_dir = tmp_path / "projects" / project_id / "versions" / version_id
    assert (version_dir / "train" / "images").exists()
    assert (version_dir / "train" / "labels").exists()
    assert (version_dir / "valid" / "images").exists()
    assert (version_dir / "valid" / "labels").exists()
    assert (version_dir / "test" / "images").exists()
    assert (version_dir / "test" / "labels").exists()
    assert (version_dir / "version_meta.json").exists()

