import json
from pathlib import Path
import cv2

def generate_coco_annotations(version_dir: Path, version_meta: dict, class_list: list):
    class_name_to_id = {c["name"]: i for i, c in enumerate(class_list)}
    categories = [{"id": i, "name": c["name"]} for i, c in enumerate(class_list)]
    
    splits = ["train", "valid", "test"]
    coco_data = {
        split: {
            "info": {"description": f"Dataset split: {split}"},
            "images": [],
            "annotations": [],
            "categories": categories
        } for split in splits
    }
    
    ann_id_counter = 1
    
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
        
        image_id = len(coco_data[split]["images"]) + 1
        
        coco_data[split]["images"].append({
            "id": image_id,
            "file_name": filename,
            "width": w,
            "height": h
        })
        
        for ann in annotations.get("objects", []):
            cls_name = ann.get("class")
            if cls_name not in class_name_to_id:
                continue
            cls_id = class_name_to_id[cls_name]
            bbox = ann.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            
            # COCO bbox: [x_min, y_min, width, height]
            coco_data[split]["annotations"].append({
                "id": ann_id_counter,
                "image_id": image_id,
                "category_id": cls_id,
                "bbox": bbox,
                "area": bbox[2] * bbox[3],
                "iscrowd": 0
            })
            ann_id_counter += 1
            
    for split in splits:
        with (version_dir / split / "annotations.json").open("w") as f:
            json.dump(coco_data[split], f, indent=2)
