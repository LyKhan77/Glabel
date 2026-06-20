from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Query
from fastapi.responses import FileResponse, Response, StreamingResponse
import cv2
import random

from backend.schemas.dataset import (
    AssignAssetsRequest,
    AutoAnnotateResponse,
    DatasetAsset,
    DatasetUploadResponse,
    DatasetVersion,
    VersionCreate,
    AssetAnnotationsUpdate,
    AugmentationPreviewRequest,
)
from backend.services import datasets as svc
from backend.services.augmentation import apply_augmentation

router = APIRouter(prefix="/api/v1/projects/{project_id}", tags=["datasets"])

@router.get("/dataset/assets/{asset_id}/image")
def get_asset_image(project_id: str, asset_id: str):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    asset = svc.get_asset(project_id, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Image not found")
        
    full_path = svc.get_asset_path(asset)
    if not full_path:
        raise HTTPException(status_code=404, detail="Image not found")
        
    return FileResponse(full_path, media_type=asset["content_type"])


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


@router.patch("/dataset/assets/assign", response_model=list[DatasetAsset])
def assign_assets(project_id: str, payload: AssignAssetsRequest):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return svc.assign_assets(project_id, payload.asset_ids)


@router.patch("/dataset/assets/unassign", response_model=list[DatasetAsset])
def unassign_assets(project_id: str, payload: AssignAssetsRequest):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return svc.unassign_assets(project_id, payload.asset_ids)


@router.delete("/dataset/assets", response_model=list[DatasetAsset])
def delete_assets(project_id: str, payload: AssignAssetsRequest):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return svc.delete_assets(project_id, payload.asset_ids)


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
    try:
        version = svc.create_version(project_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if version is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return version

@router.get("/versions/{version_id}", response_model=DatasetVersion)
def get_version(project_id: str, version_id: str):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    version = svc.get_version(project_id, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.delete("/versions/{version_id}")
def delete_version(project_id: str, version_id: str):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    version = svc.delete_version(project_id, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"status": "deleted", "id": version_id}

@router.put("/dataset/assets/{asset_id}/annotations", response_model=DatasetAsset)
def update_asset_annotations(project_id: str, asset_id: str, payload: AssetAnnotationsUpdate):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    asset = svc.update_annotations(project_id, asset_id, payload.annotations, payload.status)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset


@router.post("/dataset/preview-augmentation")
def preview_augmentation(project_id: str, payload: AugmentationPreviewRequest):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
        
    assets = svc.list_assets(project_id)
    if not assets:
        raise HTTPException(status_code=400, detail="No assets available for preview")
        
    if payload.asset_id:
        target_asset = next((a for a in assets if a["id"] == payload.asset_id), None)
        if not target_asset:
            raise HTTPException(status_code=404, detail="Asset not found")
    else:
        annotated = [a for a in assets if a["status"] == "annotated"]
        if annotated:
            target_asset = random.choice(annotated)
        else:
            target_asset = random.choice(assets)
            
    full_path = svc.get_asset_path(target_asset)
    if not full_path:
        raise HTTPException(status_code=404, detail="Image file missing")
        
    image = cv2.imread(full_path)
    if image is None:
        raise HTTPException(status_code=500, detail="Failed to read image")
        
    try:
        augmented = apply_augmentation(image, payload.augmentation_key, payload.params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    success, encoded = cv2.imencode(".jpg", augmented)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode image")
        
    return Response(content=encoded.tobytes(), media_type="image/jpeg")

@router.post("/versions/{version_id}/export")
def export_version(
    project_id: str, 
    version_id: str, 
    format: str = Query(..., pattern="^(yolo|coco)$")
):
    if not svc.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        buffer = svc.export_version(project_id, version_id, format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not buffer:
        raise HTTPException(status_code=404, detail="Version not found")
        
    return StreamingResponse(
        iter([buffer.getvalue()]), 
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=version_{version_id}_{format}.zip"}
    )
