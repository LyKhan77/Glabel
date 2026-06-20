from fastapi import APIRouter
from backend.schemas.system import HardwareInfoResponse
from backend.services.system import detect_hardware

router = APIRouter(prefix="/api/v1/system", tags=["System"])

@router.get("/hardware", response_model=HardwareInfoResponse)
def get_hardware_info():
    return detect_hardware()
