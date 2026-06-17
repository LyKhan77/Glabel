from pathlib import Path

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


def test_upload_image_lists_unassigned_asset(client, project_id):
    _, encoded = cv2.imencode(".png", np.zeros((8, 8, 3), dtype=np.uint8))

    uploaded = client.post(
        f"/api/v1/projects/{project_id}/dataset/upload",
        files={"files": ("sample.png", encoded.tobytes(), "image/png")},
    )
    listed = client.get(f"/api/v1/projects/{project_id}/dataset/assets")

    assert uploaded.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["kind"] == "image"
    assert listed.json()[0]["status"] == "unassigned"
    assert listed.json()[0]["filename"] == "sample.png"


def test_upload_video_extracts_frames(client, project_id, tmp_path):
    video_path = tmp_path / "sample.avi"
    _write_sample_video(video_path)

    with video_path.open("rb") as video:
        uploaded = client.post(
            f"/api/v1/projects/{project_id}/dataset/upload",
            data={"extract_fps": "2"},
            files={"files": ("sample.avi", video, "video/x-msvideo")},
        )

    assert uploaded.status_code == 201
    body = uploaded.json()
    frames = [asset for asset in body["assets"] if asset["kind"] == "frame"]
    assert len(frames) == 2
    assert all(asset["source_asset_id"] for asset in frames)
    assert all(asset["status"] == "unassigned" for asset in frames)


def test_auto_annotate_marks_unassigned_assets(client, project_id):
    _, encoded = cv2.imencode(".png", np.zeros((8, 8, 3), dtype=np.uint8))
    client.post(
        f"/api/v1/projects/{project_id}/dataset/upload",
        files={"files": ("sample.png", encoded.tobytes(), "image/png")},
    )

    annotated = client.post(f"/api/v1/projects/{project_id}/dataset/auto-annotate")
    listed = client.get(f"/api/v1/projects/{project_id}/dataset/assets?status=annotated")

    assert annotated.status_code == 200
    assert annotated.json()["annotated_count"] == 1
    assert listed.json()[0]["status"] == "annotated"


def test_create_and_list_dataset_versions(client, project_id):
    _, encoded = cv2.imencode(".png", np.zeros((8, 8, 3), dtype=np.uint8))
    client.post(
        f"/api/v1/projects/{project_id}/dataset/upload",
        files={"files": ("sample.png", encoded.tobytes(), "image/png")},
    )
    client.post(f"/api/v1/projects/{project_id}/dataset/auto-annotate")

    created = client.post(
        f"/api/v1/projects/{project_id}/versions",
        json={
            "name": "Version 1",
            "split": {"train": 70, "valid": 20, "test": 10},
            "preprocessing": ["resize"],
            "augmentations": ["flip"],
            "multiplier": 2,
        },
    )
    listed = client.get(f"/api/v1/projects/{project_id}/versions")

    assert created.status_code == 201
    assert created.json()["asset_count"] == 1
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Version 1"


def _write_sample_video(path: Path) -> None:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        4,
        (16, 16),
    )
    assert writer.isOpened()
    for value in (0, 40, 80, 120):
        frame = np.full((16, 16, 3), value, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_serve_image(client, project_id, tmp_path):
    _, encoded = cv2.imencode(".png", np.zeros((8, 8, 3), dtype=np.uint8))
    uploaded = client.post(
        f"/api/v1/projects/{project_id}/dataset/upload",
        files={"files": ("sample.png", encoded.tobytes(), "image/png")},
    )
    asset_id = uploaded.json()["assets"][0]["id"]

    response = client.get(f"/api/v1/projects/{project_id}/dataset/assets/{asset_id}/image")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0

    # Project not found
    response_404_proj = client.get(f"/api/v1/projects/invalid-proj/dataset/assets/{asset_id}/image")
    assert response_404_proj.status_code == 404
    assert response_404_proj.json()["detail"] == "Project not found"

    # Image not found (invalid asset_id)
    response_404_asset = client.get(f"/api/v1/projects/{project_id}/dataset/assets/invalid-asset/image")
    assert response_404_asset.status_code == 404
    assert response_404_asset.json()["detail"] == "Image not found"

    # Image not found (file deleted from disk)
    stored_path = tmp_path / uploaded.json()["assets"][0]["stored_path"]
    stored_path.unlink()
    response_404_disk = client.get(f"/api/v1/projects/{project_id}/dataset/assets/{asset_id}/image")
    assert response_404_disk.status_code == 404
    assert response_404_disk.json()["detail"] == "Image not found"

