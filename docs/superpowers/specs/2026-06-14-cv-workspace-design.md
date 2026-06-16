# Product Requirements Document (PRD): Computer Vision Workspace (Glabel)

## 1. Project Context
**Glabel** adalah platform interaktif lokal (berjalan di perangkat *AI Engineers*) untuk melakukan pengujian model Computer Vision dan memvalidasi *use case* sebelum mengimplementasikan *pipeline MLOps* skala besar. Aplikasi ditargetkan sebagai *Pre-built Model Sandbox / Validation Tool*.

## 2. Tech Stack & Backend Communication (MVP)
Mempertimbangkan kebutuhan kecepatan inferensi secara lokal, arsitektur *Frontend* dan *Backend* dipisahkan secara tegas:
- **Frontend**: **Vue 3 + Vite** dipadukan dengan **VueFlow** (untuk *Canvas Node Builder*). Pemilihan Vue 3 didasarkan pada keunggulan *Composition API* yang reaktif dan ringan untuk mengatur *state* kanvas yang kompleks tanpa *overhead* re-rendering yang berlebihan.
- **Backend**: **FastAPI (Python)**. Standar industri untuk *Computer Vision API* karena kapabilitas *asynchronous*-nya.
- **Communication Protocol**: Menggunakan **WebSockets** (bidirectional). Penggunaan HTTP REST API hanya untuk *setup*. *Streaming frame* dan respons JSON dikirim secara *real-time* via WebSockets untuk menekan *overhead* hingga level sub-milidetik.
- **Inference & Logic Library**: Menggunakan `roboflow/supervision`. Library ini sangat kuat untuk menangani *Bounding Box/Polygon rendering*, NMS filtering, *confidence filtering*, dan *Zone Counting*.

## 3. Hardware & GPU Indexing (Cross-Platform)
Glabel secara otomatis mendeteksi kapabilitas *hardware* pengguna dan memberikan kontrol manual (index GPU).
1. Saat Backend (FastAPI) berjalan, ia akan melakukan *hardware probing*:
   - Jika NVIDIA GPU: mendeteksi index (misal `['cuda:0', 'cuda:1', 'cpu']`).
   - Jika Mac (Apple Silicon): mendeteksi MPS (`['mps', 'cpu']`).
2. Terdapat **Hardware Target Dropdown** di UI (Toolbar) agar pengguna bisa dengan sadar memaksa model berjalan di CPU, MPS, atau spesifik GPU.

## 4. Core Engine: Visual Pipeline Builder
Sistem ini murni bertindak sebagai *Engine* yang memproses urutan Node secara dinamis, tanpa melakukan *hardcode* terhadap industri tertentu.

**Tipe-Tipe Node yang Didukung:**
1. **Input Nodes**: Camera Stream (Webcam/RTSP), Image/Video Upload, Local Folder.
2. **Preprocessing Nodes**: Crop, Resize, Grayscale, Normalize.
3. **Inference Nodes (Future-Proof Model Loading)**:
   - Aplikasi tidak meng-hardcode satu versi YOLO atau SAM. Backend terintegrasi dengan ekosistem `ultralytics` dan Hub untuk pemuatan model secara dinamis.
   - **Object Detection**: Mendukung *string identifier* apa pun dari `yolov8n.pt`, `yolo11n.pt`, hingga rilis masa depan (misal `yolo26.pt`).
   - **Instance Segmentation**: Mendukung `yolov8n-seg.pt` hingga rilis baru, serta keluarga **SAM (Segment Anything)** termasuk `sam_b.pt`, **SAM2**, hingga **SAM3**.
   - **Image Classification**: Mendukung model berakhiran `-cls.pt` dari berbagai generasi.
   - **OCR**: Menggunakan `EasyOCR` sebagai *default out-of-the-box engine*.
   - Jika *user* menggunakan *custom model* (`.onnx`/`.pt`), node ini menyediakan kolom *upload* `data.yaml` atau input array label manual agar teks *Bounding Box* ter-render dengan benar.
4. **Logic/Filter Nodes**: Confidence Threshold Filter, Class Filter, NMS, Condition Logic.
5. **Output Nodes**: Menampilkan *Metrics Panel* dan hasil visualisasi inferensi secara langsung **di dalam badan node tersebut** (*In-Canvas Preview*), alih-alih menggunakan jendela melayang yang terpisah.

## 5. Core Modes & Architecture

### Navigasi & Homepage (Dashboard)
Saat aplikasi dibuka, pengguna akan disambut oleh sebuah **Dashboard bergaya Terminal statis** yang berisi tombol `[+] New Inference Playground` (membuat kanvas baru) dan `[Folder] Open Vision Solution` (memuat file `.glabel`), beserta daftar proyek yang baru-baru ini diakses (*Recent Workspaces*).

### Mode 1: Inference Playground (Sandbox Mode)
- **Kondisi Awal**: Kanvas Kosong (*Blank Canvas*) yang dibuka dari Dashboard.
- **Workflow**: User menarik *Input Node*, menyambungkannya ke *Inference Node*, memfilter hasil via *Logic Node*, lalu melemparnya ke *Output Node*.
- **State**: *Stateless*.

### Mode 2: Vision Solution / Solution Blueprints (End-to-End Mode)
- **Kondisi Awal**: Sistem memuat konfigurasi Pipeline dari file JSON (*Template-Driven*).
- **Penyimpanan Lokal (Workspace & Asset Management)**: File `.glabel` murni menyimpan arsitektur Node dan **Absolute Path** ke folder gambar/video di hardisk pengguna. Aplikasi **tidak** merubah gambar menjadi *Base64* untuk menghemat ukuran file dan memori RAM. Hal ini menjamin file JSON tetap berukuran kilobyte.
- **Workflow**: Load Blueprint -> Upload Sampel -> Evaluasi Model -> Cek *Metrics Panel* -> Jika ada *failure cases*, lakukan *Flagging* -> *Send to Annotation*.

## 6. Deployment & Environment Strategy
Untuk kompatibilitas maksimal di berbagai perangkat (Windows/Linux/Mac), Backend Glabel akan menggunakan arsitektur **Isolated Virtual Environment (`.venv`)** yang dibangun menggunakan `install.bat` (Windows) atau `install.sh` (Unix). Skrip instalasi cerdas ini akan mendeteksi OS pengguna dan mengunduh index PyTorch yang sesuai.

## 7. UI/UX Considerations
- Sesuai `DESIGN.md`: font *Berkeley Mono*, desain kaku (*austere*), tanpa elemen *drop shadow*, latar *cream* (`#fdfcfc`), border *hairline*, tombol kotak radius 4px (`rounded.sm`).
- **Logo**: Menggunakan konsep *Block-Pixel Eye* tanpa teks.
- **Infinite Canvas**: Dibangun di atas library `VueFlow` yang sudah dikustomisasi sesuai pedoman *DESIGN.md*.
