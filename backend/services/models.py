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

# Generate SAM 2
for variant in ["t", "s", "b", "l"]:
    REGISTRY.append({
        "id": f"sam2_{variant}",
        "name": f"SAM 2 {variant.upper()}",
        "architecture": "SAM 2",
        "task_type": "Label Assist",
        "size_mb": 0.0,
        "url": f"{ULTRALYTICS_RELEASE_URL}/sam2_{variant}.pt"
    })

# SAM 3
REGISTRY.append({
    "id": "sam3",
    "name": "SAM 3",
    "architecture": "SAM 3",
    "task_type": "Label Assist",
    "size_mb": 0.0,
    "url": "https://huggingface.co/facebook/sam3/resolve/main/sam3.pt"
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
        
    if "SAM 3" in model["architecture"]:
        raise ValueError("SAM 3 requires manual download from Hugging Face (facebook/sam3) due to Meta's license agreement. Please request access, download the .pt file, and place it in the glabel_data/models folder.")
    
    target_path = get_models_dir() / f"{model_id}.pt"
    
    if target_path.exists():
        return {"message": "Already downloaded", "id": model_id}

    try:
        from ultralytics.utils.downloads import attempt_download_asset
        import shutil
    except ImportError:
        raise ValueError("The 'ultralytics' package is required for downloading models. Please ensure it is installed (pip install -r backend/requirements.txt) and restart the server.")
        
    try:
        downloaded_file = attempt_download_asset(f"{model_id}.pt")
        if str(downloaded_file) != str(target_path):
            shutil.move(str(downloaded_file), str(target_path))
    except Exception as e:
        raise RuntimeError(f"Ultralytics failed to download {model_id}.pt: {e}")

    return {"message": "Download complete", "id": model_id}
