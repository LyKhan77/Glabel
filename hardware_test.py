import platform
import psutil
try:
    import torch
except ImportError:
    torch = None

def detect_hardware():
    info = {
        "os": platform.system() + " " + platform.release(),
        "cpu": platform.processor(),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpu": None,
        "vram_gb": None,
        "cuda_available": False
    }
    
    if torch and torch.cuda.is_available():
        info["cuda_available"] = True
        info["gpu"] = torch.cuda.get_device_name(0)
        info["vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        
    # Mac MPS
    if torch and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        info["gpu"] = "Apple Silicon"
        info["vram_gb"] = info["ram_gb"] # Shared memory
        
    return info

print(detect_hardware())
