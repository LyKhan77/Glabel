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
- **Kondisi Awal (Pre-built Templates)**: Sistem memuat konfigurasi Pipeline dari file JSON (*Template-Driven*). Template Blueprint (misal: *PPE Detection*, *OCR*) di-*bundle* secara statis (100% *offline*) di dalam instalasi aplikasi untuk menjamin privasi data tanpa perlu koneksi ke *cloud*.
- **Penyimpanan Lokal & Data Relinking**: File `.glabel` murni menyimpan arsitektur Node dan **Absolute Path** ke folder gambar/video di hardisk pengguna. Jika folder dataset dipindahkan, sistem akan mendeteksi path yang *broken* dan memunculkan fitur **"Relink Dataset Folder"**. Aplikasi **tidak** merubah gambar menjadi *Base64* untuk menghemat ukuran file dan memori RAM.
- **Workflow & Active Learning (Hard Negative Mining)**: Load Blueprint ➔ Hubungkan Dataset ➔ Evaluasi Model ➔ Cek *Metrics Panel*.
  - Jika ada *failure cases* (kesalahan deteksi), sistem masuk ke **Fase Active Learning**.
  - **Mekanisme Flagging (Hybrid)**: 
    1. **Otomatis**: Sistem akan men-*flag* dan mengekstrak *frame* yang memiliki *confidence score* meragukan (misal: 15% - 40%).
    2. **Manual**: *User* dapat menekan *shortcut* (misal: Spasi/F) saat melihat *frame* yang salah pada *live preview*.
  - *Frame* yang ter-*flag* akan dianotasi ulang (*auto-annotate*) menggunakan model *zero-shot* terkuat (seperti SAM2) dan disimpan ke folder `Dataset/Flagged` beserta file `.txt` YOLO-nya, siap untuk *re-training* model.

## 6. Deployment & Environment Strategy
Untuk kompatibilitas maksimal di berbagai perangkat (Windows/Linux/Mac), Backend Glabel akan menggunakan arsitektur **Isolated Virtual Environment (`.venv`)** yang dibangun menggunakan `install.bat` (Windows) atau `install.sh` (Unix). Skrip instalasi cerdas ini akan mendeteksi OS pengguna dan mengunduh index PyTorch yang sesuai.

## 7. UI/UX Considerations
- Sesuai `DESIGN.md`: font *Berkeley Mono*, desain kaku (*austere*), tanpa elemen *drop shadow*, latar *cream* (`#fdfcfc`), border *hairline*, tombol kotak radius 4px (`rounded.sm`).
- **Logo**: Menggunakan konsep *Block-Pixel Eye* tanpa teks.
- **Infinite Canvas**: Dibangun di atas library `VueFlow` yang sudah dikustomisasi sesuai pedoman *DESIGN.md*.

## 8. Information Architecture (IA) & Navigation Flow

### 8.1. App Map / Wireflow (Launcher-to-Fullscreen)
Glabel menggunakan pendekatan **Launcher-to-Fullscreen**. Dashboard bertindak sebagai titik awal (Launcher) yang steril. Saat pengguna memasuki *Workspace* (baik baru maupun *load*), *Workspace* akan mengambil alih seluruh layar (*fullscreen*) tanpa interupsi navigasi dari Dashboard.

```text
[ DASHBOARD (Home) ]
  ├── Section: New Project
  │    └── Button: [+] New Inference Playground  ──(Klik)──>  Membuka WORKSPACE (Blank)
  ├── Section: Load Project
  │    └── Button: [Folder] Open Vision Solution ──(Klik)──>  Membuka WORKSPACE (Loaded)
  └── Section: Recent Workspaces
       └── List of .glabel files                 ──(Klik)──>  Membuka WORKSPACE (Loaded)

[ FULLSCREEN WORKSPACE (Canvas) ]
  ├── Top Toolbar
  │    ├── Tombol "Back to Home"                 ──(Klik)──>  Kembali ke DASHBOARD
  │    ├── Hardware Target Dropdown (CPU/GPU)
  │    ├── Workspace Name & Save State (.glabel)
  │    └── Export Button
  ├── Left Sidebar: Node Palette (Draggable)
  │    └── Input, Preprocessing, Inference, Logic, Output Nodes
  ├── Center: Infinite Canvas (VueFlow)
  │    └── Tempat merangkai Node (Mendukung Hybrid Wire: Manual & Auto-connect)
  └── Right Sidebar: Properties Panel
       └── (Muncul saat Node diklik) Menampilkan detail parameter dan metrik latensi
```

### 8.2. Task Flow: Inference Playground (Sandbox Mode)
1. **Launch & Setup**: Buka aplikasi ➔ Tampil Dashboard ➔ Klik `[+] New Inference Playground`.
2. **Hardware Target Selection**: Secara *default*, sistem mendeteksi GPU. Jika perlu, *user* dapat menggantinya (CPU/MPS) lewat Toolbar.
3. **Node Construction (Hybrid Wire)**:
   - *User* men-drag Node dari Palette (Kiri) ke Canvas (Tengah).
   - **Koneksi Manual (Default)**: *User* menarik kabel dari ujung (*port*) Node ke Node lain.
   - **Koneksi Auto-connect**: Memungkinkan *user* untuk menggunakan *shortcut* (misal: tekan `Shift` sambil men-drop Node baru) untuk menyambungkan Node secara otomatis ke Node terdekat/sebelumnya. Hal ini mempercepat pembuatan *linear pipeline*.
4. **Real-time Tuning**: Parameter diubah di Properties Panel (Kanan), *output* video/gambar dan metrik latensi pada Node akan ter-update secara *real-time*.

## 9. Advanced Computer Vision Features (Expert Additions)
Sebagai platform skala *Enterprise/Expert*, Glabel dilengkapi dengan fitur validasi dan optimasi tingkat lanjut yang menjadi standar industri:

1. **Interactive ROI & Zone Definition**:
   *User* dapat menggambar Polygon (Area) atau Garis (*Line Crossing*) secara langsung pada *Output Node Preview* untuk membatasi area deteksi. Node ini akan secara cerdas memfilter objek yang hanya berada di dalam zona tersebut (menggunakan `supervision.PolygonZone`).
2. **DAG Execution Optimization & Node Caching**:
   Setiap *output* dari sebuah Node akan di-*cache* sementara (di RAM/VRAM). Jika *user* hanya menggeser *slider* *Confidence Threshold* di Logic Node, sistem tidak akan melakukan inferensi ulang pada *YOLO Node* sebelumnya. Hal ini membuat latensi *tuning* turun menjadi 0ms.
3. **Batch Evaluation & Metrics Aggregation**:
   Selain memproses satu video secara *real-time*, pengguna dapat menghubungkan folder (berisi ratusan gambar) ke *pipeline*, lalu melihat agregat akurasi, grafik *confusion matrix*, dan daftar *False Positives* (jika menggunakan gambar yang sudah memiliki *ground truth* XML/YOLO txt).
4. **Code / Pipeline Export**:
   Setelah selesai meracik kanvas, *user* dapat mengeklik tombol **"Export to Python"**. Glabel akan men-*generate* skrip Python utuh yang mereplikasi *pipeline* tersebut, siap untuk di-*deploy* di server produksi tanpa UI (sebagai *headless runner* atau *Docker container*).

*(Catatan: Desain antarmuka (UI) final akan mengacu pada kaidah premium dan fungsional seperti yang direkomendasikan pada skill `ui-ux-pro-max` / `impeccable`)*
