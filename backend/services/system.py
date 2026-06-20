import platform
import psutil

try:
    import torch
except ImportError:
    torch = None

def detect_hardware() -> dict:
    info = {
        "os": f"{platform.system()} {platform.release()}",
        "cpu": platform.processor() or "Unknown CPU",
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpu": None,
        "vram_gb": None,
        "cuda_available": False,
        "mps_available": False,
        "recommended_models": []
    }
    
    if torch:
        if torch.cuda.is_available():
            info["cuda_available"] = True
            info["gpu"] = torch.cuda.get_device_name(0)
            info["vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            info["mps_available"] = True
            info["gpu"] = "Apple Silicon GPU"
            info["vram_gb"] = info["ram_gb"]  # Unified memory
            
    # Recommendations
    recs = []
    if info["cuda_available"] or info["mps_available"]:
        vram = info.get("vram_gb", 0)
        if vram >= 8:
            recs.extend(["YOLO26x", "YOLO26l", "RT-DETR X", "SAM 3"])
        elif vram >= 4:
            recs.extend(["YOLO26m", "YOLO11m", "SAM 2 Base"])
        else:
            recs.extend(["YOLO26s", "YOLO26n", "SAM 2 Small"])
    else:
        # CPU Only
        recs.extend(["YOLO26n", "YOLO11n", "SAM 2 Tiny"])
        
    info["recommended_models"] = recs
    return info
