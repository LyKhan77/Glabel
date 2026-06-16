from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.schemas.dataset import (
    AutoAnnotateResponse,
    DatasetAsset,
    DatasetUploadResponse,
    DatasetVersion,
    VersionCreate,
)
from backend.services import datasets as svc

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["datasets"])


@router.post("/dataset/upload", response_model=DatasetUploadResponse, status_code=201)
def upload_dataset_assets(
    project_id: str,
    files: list[UploadFile] = File(...),
    extract_fps: int = Form(2),
):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    assets = svc.save_uploads(project_id, files, extract_fps)
    return {"assets": assets}


@router.get("/dataset/assets", response_model=list[DatasetAsset])
def list_dataset_assets(project_id: str, status: str | None = None):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return svc.list_assets(project_id, status)


@router.post("/dataset/auto-annotate", response_model=AutoAnnotateResponse)
def auto_annotate_dataset(project_id: str):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    count, assets = svc.auto_annotate(project_id)
    return {"annotated_count": count, "assets": assets}


@router.get("/versions", response_model=list[DatasetVersion])
def list_versions(project_id: str):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return svc.list_versions(project_id)


@router.post("/versions", response_model=DatasetVersion, status_code=201)
def create_version(project_id: str, payload: VersionCreate):
    version = svc.create_version(project_id, payload)
    if version is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return version
