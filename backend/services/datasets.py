import random
import re
import shutil
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
from fastapi import UploadFile

from backend.core.config import get_data_dir
from backend.core.storage import read_json, update_json
from backend.schemas.dataset import VersionCreate
from backend.services.projects import get_project

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTENSIONS = {".avi", ".mov", ".mp4", ".mkv", ".webm"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip() or "upload"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def _project_dir(project_id: str) -> Path:
    return get_data_dir() / "projects" / project_id


def _assets_file(project_id: str) -> str:
    _project_dir(project_id).mkdir(parents=True, exist_ok=True)
    return f"projects/{project_id}/dataset_assets.json"


def _versions_file(project_id: str) -> str:
    _project_dir(project_id).mkdir(parents=True, exist_ok=True)
    return f"projects/{project_id}/versions.json"


def _relative(path: Path) -> str:
    return path.resolve().relative_to(get_data_dir()).as_posix()


def _asset(
    project_id: str,
    kind: str,
    filename: str,
    stored_path: Path,
    content_type: str = "",
    source_asset_id: str | None = None,
) -> dict:
    timestamp = _now()
    return {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "kind": kind,
        "filename": filename,
        "stored_path": _relative(stored_path),
        "content_type": content_type,
        "status": "unassigned",
        "annotations": {},
        "source_asset_id": source_asset_id,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def project_exists(project_id: str) -> bool:
    return get_project(project_id) is not None


def list_assets(project_id: str, status: str | None = None) -> list[dict]:
    assets = read_json(_assets_file(project_id), default=[])
    if status:
        return [asset for asset in assets if asset["status"] == status]
    return assets


def get_asset(project_id: str, asset_id: str) -> dict | None:
    assets = list_assets(project_id)
    for asset in assets:
        if asset["id"] == asset_id:
            return asset
    return None


def get_asset_path(asset: dict) -> Path | None:
    full_path = get_data_dir() / asset["stored_path"]
    if full_path.exists():
        return full_path
    return None


def save_uploads(project_id: str, files: list[UploadFile], extract_fps: int = 2) -> list[dict]:
    if not project_exists(project_id):
        return []

    originals_dir = _project_dir(project_id) / "assets" / "originals"
    originals_dir.mkdir(parents=True, exist_ok=True)
    new_assets = []

    for upload in files:
        filename = _safe_filename(upload.filename or "upload")
        stored_name = f"{uuid.uuid4()}_{filename}"
        stored_path = originals_dir / stored_name
        with stored_path.open("wb") as target:
            shutil.copyfileobj(upload.file, target)

        extension = stored_path.suffix.lower()
        if extension in VIDEO_EXTENSIONS:
            video_asset = _asset(project_id, "video", filename, stored_path, upload.content_type or "")
            new_assets.append(video_asset)
            new_assets.extend(_extract_frames(project_id, stored_path, video_asset["id"], extract_fps))
        else:
            kind = "image" if extension in IMAGE_EXTENSIONS else "file"
            new_assets.append(_asset(project_id, kind, filename, stored_path, upload.content_type or ""))

    def mut(assets):
        assets.extend(new_assets)
        return new_assets

    return update_json(_assets_file(project_id), [], mut)


def auto_annotate(project_id: str) -> tuple[int, list[dict]]:
    timestamp = _now()

    def mut(assets):
        changed = []
        for asset in assets:
            if asset["status"] == "unassigned" and asset["kind"] != "video":
                asset["status"] = "annotated"
                asset["updated_at"] = timestamp
                changed.append(asset)
        return changed

    changed = update_json(_assets_file(project_id), [], mut)
    return len(changed), changed


def assign_assets(project_id: str, asset_ids: list[str]) -> list[dict]:
    if not project_exists(project_id):
        return []

    timestamp = _now()
    asset_ids_set = set(asset_ids)

    def mut(assets):
        changed = []
        for asset in assets:
            if asset["id"] in asset_ids_set and asset["status"] == "unassigned":
                asset["status"] = "unannotated"
                asset["updated_at"] = timestamp
                changed.append(asset)
        return changed

    return update_json(_assets_file(project_id), [], mut)


def unassign_assets(project_id: str, asset_ids: list[str]) -> list[dict]:
    timestamp = _now()
    asset_ids_set = set(asset_ids)

    def mut(assets):
        changed = []
        for asset in assets:
            if asset["id"] in asset_ids_set and asset["status"] in {"unannotated", "annotated"}:
                asset["status"] = "unassigned"
                asset["updated_at"] = timestamp
                changed.append(asset)
        return changed

    return update_json(_assets_file(project_id), [], mut)


def delete_assets(project_id: str, asset_ids: list[str]) -> list[dict]:
    asset_ids_set = set(asset_ids)

    def mut(assets):
        deleted = [asset for asset in assets if asset["id"] in asset_ids_set]
        assets[:] = [asset for asset in assets if asset not in deleted]
        for asset in deleted:
            path = get_asset_path(asset)
            if path:
                path.unlink(missing_ok=True)
        return deleted

    return update_json(_assets_file(project_id), [], mut)


def list_versions(project_id: str) -> list[dict]:
    return read_json(_versions_file(project_id), default=[])


def get_version(project_id: str, version_id: str) -> dict | None:
    versions = list_versions(project_id)
    for version in versions:
        if version["id"] == version_id:
            return version
    return None


def delete_version(project_id: str, version_id: str) -> dict | None:
    def mut(versions):
        for i, version in enumerate(versions):
            if version["id"] == version_id:
                deleted = versions.pop(i)
                # Remove version directory
                version_dir = _project_dir(project_id) / "versions" / version_id
                if version_dir.exists():
                    shutil.rmtree(version_dir)
                return deleted
        return None

    return update_json(_versions_file(project_id), [], mut)


def create_version(project_id: str, payload: VersionCreate):
    if not project_exists(project_id):
        return None

    annotated_assets = list_assets(project_id, status="annotated")
    if not annotated_assets:
        raise ValueError("No annotated assets to version")

    version_id = str(uuid.uuid4())
    version = {
        "id": version_id,
        "project_id": project_id,
        "name": payload.name,
        "description": payload.description,
        "split": payload.split,
        "preprocessing": [p.model_dump() for p in payload.preprocessing],
        "augmentation_mode": payload.augmentation_mode,
        "augmentation_preset": payload.augmentation_preset,
        "augmentations": [a.model_dump() for a in payload.augmentations],
        "multiplier": payload.multiplier,
        "asset_count": len(annotated_assets),
        "split_counts": {},
        "created_at": _now(),
    }

    # Shuffle and split
    random.seed(42)  # For reproducibility, though might want a different strategy
    shuffled_assets = list(annotated_assets)
    random.shuffle(shuffled_assets)

    total_split_weight = sum(payload.split.values())
    if total_split_weight == 0:
        split_ratios = {"train": 1.0, "valid": 0.0, "test": 0.0}
    else:
        split_ratios = {k: v / total_split_weight for k, v in payload.split.items()}

    split_counts = {"train": 0, "valid": 0, "test": 0}
    
    total_assets = len(shuffled_assets)
    train_end = int(total_assets * split_ratios.get("train", 0))
    valid_end = train_end + int(total_assets * split_ratios.get("valid", 0))

    splits = {}
    for i, asset in enumerate(shuffled_assets):
        if i < train_end:
            split_name = "train"
        elif i < valid_end:
            split_name = "valid"
        else:
            split_name = "test"
        splits[asset["id"]] = split_name
        split_counts[split_name] += 1

    version["split_counts"] = split_counts

    # Create directories
    version_dir = _project_dir(project_id) / "versions" / version_id
    for split_name in ["train", "valid", "test"]:
        (version_dir / split_name / "images").mkdir(parents=True, exist_ok=True)
        (version_dir / split_name / "labels").mkdir(parents=True, exist_ok=True)

    # Copy files
    asset_mapping = {}
    for asset in shuffled_assets:
        split_name = splits[asset["id"]]
        dest_images_dir = version_dir / split_name / "images"
        
        src_path = get_asset_path(asset)
        if src_path and src_path.exists():
            dest_path = dest_images_dir / asset["filename"]
            shutil.copy2(src_path, dest_path)
            
        asset_mapping[asset["id"]] = {
            "split": split_name,
            "filename": asset["filename"],
            "annotations": asset.get("annotations", {})
        }

    with (version_dir / "version_meta.json").open("w") as f:
        json.dump(asset_mapping, f, indent=2)

    def mut(versions):
        versions.append(version)
        return version

    return update_json(_versions_file(project_id), [], mut)


def _extract_frames(project_id: str, video_path: Path, source_asset_id: str, extract_fps: int) -> list[dict]:
    frames_dir = _project_dir(project_id) / "assets" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return []

    source_fps = capture.get(cv2.CAP_PROP_FPS) or extract_fps
    step = max(1, round(source_fps / max(1, extract_fps)))
    frame_index = 0
    saved_index = 0
    frame_assets = []

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_index % step == 0:
                frame_name = f"{video_path.stem}_frame_{saved_index:04d}.jpg"
                frame_path = frames_dir / frame_name
                if cv2.imwrite(str(frame_path), frame):
                    frame_assets.append(
                        _asset(
                            project_id,
                            "frame",
                            frame_name,
                            frame_path,
                            "image/jpeg",
                            source_asset_id,
                        )
                    )
                    saved_index += 1
            frame_index += 1
    finally:
        capture.release()

    return frame_assets
def update_annotations(project_id: str, asset_id: str, annotations: dict, status: str) -> dict | None:
    timestamp = _now()
    
    def mut(assets):
        for asset in assets:
            if asset["id"] == asset_id:
                asset["annotations"] = annotations
                asset["status"] = status
                asset["updated_at"] = timestamp
                return asset
        return None
        
    return update_json(_assets_file(project_id), [], mut)
