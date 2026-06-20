from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.models import ModelItem
from backend.services.models import list_models, download_model

router = APIRouter(prefix="/models", tags=["Models"])

@router.get("", response_model=List[ModelItem])
def get_all_models():
    """List all supported models and their download status."""
    try:
        return list_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{model_id}/download")
def download_model_endpoint(model_id: str):
    """Download a specific model by ID."""
    try:
        result = download_model(model_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Download failed: {str(e)}")
