import os
import httpx
from backend.core.config import get_data_dir

REGISTRY = []
ULTRALYTICS_RELEASE_URL = "https://github.com/ultralytics/assets/releases/download/v8.3.0"

# Generate YOLO models
for arch, arch_prefix in [("YOLOv11", "yolo11"), ("YOLO26", "yolo26")]:
    for variant in ["n", "s", "m", "l", "x"]:
        # Detection
        REGISTRY.append({
            "id": f"{arch_prefix}{variant}",
            "name": f"{arch} {variant.upper()}",
            "architecture": arch,
            "task_type": "Object Detection",
            "size_mb": 0.0,
            "url": f"{ULTRALYTICS_RELEASE_URL}/{arch_prefix}{variant}.pt"
        })
        # Segmentation
        REGISTRY.append({
            "id": f"{arch_prefix}{variant}-seg",
            "name": f"{arch} {variant.upper()} Seg",
            "architecture": arch,
            "task_type": "Segmentation",
            "size_mb": 0.0,
            "url": f"{ULTRALYTICS_RELEASE_URL}/{arch_prefix}{variant}-seg.pt"
        })
        # Classification
        REGISTRY.append({
            "id": f"{arch_prefix}{variant}-cls",
            "name": f"{arch} {variant.upper()} Cls",
            "architecture": arch,
            "task_type": "Classification",
            "size_mb": 0.0,
            "url": f"{ULTRALYTICS_RELEASE_URL}/{arch_prefix}{variant}-cls.pt"
        })
        # Pose
        REGISTRY.append({
            "id": f"{arch_prefix}{variant}-pose",
            "name": f"{arch} {variant.upper()} Pose",
            "architecture": arch,
            "task_type": "Pose",
            "size_mb": 0.0,
            "url": f"{ULTRALYTICS_RELEASE_URL}/{arch_prefix}{variant}-pose.pt"
        })

# Generate RT-DETR
for variant in ["l", "x"]:
    REGISTRY.append({
        "id": f"rtdetr-{variant}",
        "name": f"RT-DETR {variant.upper()}",
        "architecture": "RT-DETR",
        "task_type": "Object Detection",
        "size_mb": 0.0,
        "url": f"{ULTRALYTICS_RELEASE_URL}/rtdetr-{variant}.pt"
    })

# Generate SAM 2 and SAM 3
for arch, arch_prefix in [("SAM 2", "sam2"), ("SAM 3", "sam3")]:
    for variant in ["t", "s", "b", "l"]:
        REGISTRY.append({
            "id": f"{arch_prefix}_{variant}",
            "name": f"{arch} {variant.upper()}",
            "architecture": arch,
            "task_type": "Label Assist",
            "size_mb": 0.0,
            "url": f"{ULTRALYTICS_RELEASE_URL}/{arch_prefix}_{variant}.pt"
        })

def get_models_dir():
    d = get_data_dir() / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d

def list_models():
    models_dir = get_models_dir()
    for m in REGISTRY:
        m["is_downloaded"] = (models_dir / f"{m['id']}.pt").exists()
    return REGISTRY

def download_model(model_id: str):
    model = next((m for m in REGISTRY if m["id"] == model_id), None)
    if not model: 
        raise ValueError("Model not found")
    
    target_path = get_models_dir() / f"{model_id}.pt"
    tmp_path = get_models_dir() / f"{model_id}.pt.tmp"
    
    if target_path.exists():
        return {"message": "Already downloaded", "id": model_id}

    with httpx.Client(timeout=300.0) as client:
        with client.stream("GET", model["url"], follow_redirects=True) as response:
            if response.status_code != 200:
                raise RuntimeError(f"Download failed with status {response.status_code}")
            with open(tmp_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
    os.rename(tmp_path, target_path)
    return {"message": "Download complete", "id": model_id}
