# Backend Product Requirements Document (PRD): Glabel Workspace

## 1. Project Context
**Glabel** adalah platform interaktif lokal (berjalan di perangkat *AI Engineers*) untuk melakukan pengujian model Computer Vision. Dokumen ini berfokus pada arsitektur *Backend*, *Engine Pipeline*, dan fitur-fitur level pakar (*Expert CV Features*).

## 2. Tech Stack & Protocol
- **Framework**: **FastAPI (Python)**. Standar industri untuk *Computer Vision API* berkat kapabilitas *asynchronous*-nya.
- **Communication Protocol**: Menggunakan **WebSockets** (bidirectional) untuk *streaming frame* dan komunikasi JSON secara *real-time* ke Frontend dengan *overhead* minimal (sub-milidetik). HTTP REST API hanya digunakan untuk inisialisasi awal.
- **Core Library**: `roboflow/supervision`, `ultralytics` (YOLO), dan `easyocr`.

## 3. Hardware & GPU Indexing
Backend Glabel mendeteksi kapabilitas *hardware* secara dinamis:
1. Melakukan *hardware probing* saat *startup*:
   - Jika NVIDIA GPU: mendeteksi index (misal `['cuda:0', 'cuda:1', 'cpu']`).
   - Jika Mac (Apple Silicon): mendeteksi MPS (`['mps', 'cpu']`).
2. Menerima instruksi pergantian *hardware* dari Frontend (WebSockets) secara instan.

## 4. Core Engine Architecture (Visual Pipeline)
Sistem memproses antrean (*queue*) node sebagai *Directed Acyclic Graph* (DAG).
1. **Input Nodes**: Camera Stream (Webcam/RTSP), Image/Video Upload, Local Folder.
2. **Preprocessing Nodes**: Crop, Resize, Grayscale, Normalize.
3. **Inference Nodes (Dynamic Model Loading)**:
   - **Object Detection**: `yolov8n.pt`, `yolo11n.pt`, dsb.
   - **Instance Segmentation**: `yolov8n-seg.pt`, keluarga **SAM / SAM2 / SAM3**.
   - **Classification & OCR**: `-cls.pt` dan `EasyOCR`.
   - *Custom model* (`.onnx`/`.pt`) dengan integrasi `data.yaml`.
4. **Logic/Filter Nodes**: Confidence Threshold, Class Filter, NMS, Condition Logic, Zone Filtering (`supervision.PolygonZone`).
5. **Output Nodes**: Mengirimkan *frame* yang sudah di-render beserta metrik performa ke Frontend via WebSockets.

## 5. Storage & Asset Management
- **File `.glabel`**: Menyimpan topologi Node dalam format JSON. **Hanya menyimpan Absolute Path** ke folder dataset/gambar lokal. Tidak melakukan enkoding gambar menjadi Base64 untuk meminimalisasi penggunaan RAM dan ukuran file.
- **Pre-built Templates**: *Blueprint template* (misal: PPE Detection) dibundel statis secara *offline* di dalam *environment* instalasi, menjamin keamanan privasi (tanpa panggilan ke *cloud* eksternal).

## 6. Advanced Computer Vision Features (Expert Additions)
1. **DAG Execution Optimization & Node Caching**:
   Sistem meng-*cache* output Tensor dari setiap eksekusi Node (di RAM/VRAM). Jika *user* hanya menggeser parameter di "Logic Node" hilir (misal *confidence threshold*), backend tidak akan meremote *YOLO Inference Node* hulu. Hal ini membuat latensi *tuning parameter* menjadi 0ms.
2. **Batch Evaluation & Metrics Aggregation**:
   Mampu memproses *batch* direktori secara otomatis untuk menghasilkan matriks evaluasi (mAP, F1-Score, Confusion Matrix, False Positives).
3. **Code / Pipeline Export**:
   Backend mampu mengompilasi representasi JSON (DAG) menjadi skrip Python murni (`.py`) yang *headless*, siap untuk dijalankan di *production / docker container*.
4. **Active Learning (Hard Negative Mining)**:
   Saat terjadi kegagalan deteksi, *frame* akan diekstrak dan masuk ke siklus *Active Learning*. Mekanisme:
   - **Otomatis**: Jika sistem mendeteksi ambiguitas (*confidence score* 15%-40%).
   - **Manual**: Via trigger WebSocket dari *user*.
   *Frame* ini kemudian dianotasi secara otomatis menggunakan model *zero-shot* terkuat (misal SAM2) dan disimpan ke direktori `Dataset/Flagged` berformat YOLO txt untuk *re-training*.

## 7. Deployment Strategy
Menggunakan arsitektur **Isolated Virtual Environment (`.venv`)**. Skrip `install.bat` / `install.sh` akan secara mandiri mendeteksi OS (*Windows/Linux/Mac*) dan mengunduh konfigurasi PyTorch yang sesuai tanpa interferensi dependensi *host*.
