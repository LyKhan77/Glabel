import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_list_models():
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check if SAM 2 and YOLO11 exist
    architectures = {m["architecture"] for m in data}
    assert "YOLOv11" in architectures
    assert "SAM 2" in architectures
    assert "SAM 3" in architectures
    assert "YOLOv8" not in architectures

def test_download_model_not_found():
    response = client.post("/api/v1/models/invalid-model-id/download")
    assert response.status_code == 404
