import json
from pathlib import Path
import cv2
import yaml

def generate_yolo_labels(version_dir: Path, version_meta: dict, class_list: list):
    class_name_to_id = {c["name"]: i for i, c in enumerate(class_list)}
    
    for asset_id, info in version_meta.items():
        split = info["split"]
        filename = info["filename"]
        annotations = info.get("annotations", {})
        
        image_path = version_dir / split / "images" / filename
        if not image_path.exists():
            continue
            
        img = cv2.imread(str(image_path))
        if img is None:
            continue
        h, w = img.shape[:2]
        
        label_file = version_dir / split / "labels" / f"{Path(filename).stem}.txt"
        with label_file.open("w") as f:
            for ann in annotations.get("objects", []):
                cls_name = ann.get("class")
                if cls_name not in class_name_to_id:
                    continue
                cls_id = class_name_to_id[cls_name]
                bbox = ann.get("bbox")
                if not bbox or len(bbox) != 4:
                    continue
                
                # Assume bbox is [x, y, width, height] in pixels
                x_center = (bbox[0] + bbox[2] / 2) / w
                y_center = (bbox[1] + bbox[3] / 2) / h
                b_width = bbox[2] / w
                b_height = bbox[3] / h
                
                f.write(f"{cls_id} {x_center:.6f} {y_center:.6f} {b_width:.6f} {b_height:.6f}\n")


def generate_data_yaml(version_dir: Path, version_name: str, class_list: list):
    data = {
        "path": ".",
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": len(class_list),
        "names": [c["name"] for c in class_list]
    }
    
    with (version_dir / "data.yaml").open("w") as f:
        yaml.dump(data, f, sort_keys=False)
