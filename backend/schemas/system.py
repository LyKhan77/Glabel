from pydantic import BaseModel
from typing import List, Optional

class HardwareInfoResponse(BaseModel):
    os: str
    cpu: str
    ram_gb: float
    gpu: Optional[str] = None
    vram_gb: Optional[float] = None
    cuda_available: bool = False
    mps_available: bool = False
    recommended_models: List[str]
