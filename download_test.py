import sys
try:
    from ultralytics.utils.downloads import attempt_download_asset
    print("Testing YOLO26...")
    file1 = attempt_download_asset("yolo26n.pt")
    print(f"Downloaded YOLO26 to {file1}")
    print("Testing SAM3...")
    file2 = attempt_download_asset("sam3_t.pt")
    print(f"Downloaded SAM3 to {file2}")
except Exception as e:
    print(f"Error: {e}")
