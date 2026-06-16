# Glabel UI/UX Refactor & Architecture Design (PRD)

## 1. Project Context & Vision Pivot
Glabel sedang bertransformasi dari sekadar alat *Node-based Evaluator* menjadi sebuah **End-to-End Local Computer Vision Studio** yang setara dengan platform *enterprise* seperti Roboflow atau Ultralytics Hub. Perombakan (*refactoring*) ini memisahkan secara jelas alur "Data Ingestion & Training" dengan alur "Inference & Logic Orchestration". 

Semua operasi bersifat lokal, privat, dan dirancang untuk alur kerja AI Engineer profesional.

## 2. Design System & Aesthetics
Berpedoman pada *strict guidelines* di `DESIGN.md` (mengadopsi pendekatan `frontend-design` & `ui-ux-pro-max`):
- **Tipografi**: Eksklusif `Berkeley Mono` (atau *monospace* setara).
- **Warna**: Latar belakang krem (`#fdfcfc`), teks abu-abu gelap/hitam pudar (`#201d1d`).
- **Komponen UI**: Desain "Austere" (kaku, industrial, ala terminal GUI). Tanpa *drop-shadow*, menggunakan *hairline borders* 1px (`#646262`), *border-radius* maksimal 4px untuk tombol.
- **Ikonografi**: Berbasis teks ASCII (contoh: `[+]`, `[x]`, `[>]`) dan tanpa elemen *flashy*.

## 3. Global Information Architecture (Navigation)
Aplikasi membuang pendekatan *Launcher* lama dan beralih ke struktur **Global Side Panel**. Layar aplikasi terbagi menjadi dua: **Side Panel** statis di sisi kiri (lebar ~250px) dan **Main Content Area** di sisi kanan.

### Menu Side Panel:
1. **Open Vision**: Pusat pengelolaan dataset dan training model.
2. **Playgrounds**: Kanvas *VueFlow* untuk merangkai *node inference* secara interaktif.
3. **Models**: Gudang/Repositori *weights* AI (lokal `.pt` / `.onnx`) yang telah dilatih.
4. **Settings**: Konfigurasi global (Pemilihan Target Hardware GPU/CPU, direktori *default*).

---

## 4. Feature Specifications

### 4.1. Open Vision (Dashboard & Project Creation)
**Dashboard View**: Menampilkan *grid* atau *list* proyek-proyek *Computer Vision* yang sedang aktif.

**Project Creation (Split-Panel Modal)**:
Saat *user* menekan tombol `[+] New Project`, muncul *modal* yang terbagi dua kolom:
- **Kolom Kiri (AI Assistant / Prompt-to-Pipeline)**: Input teks besar (*textarea*) di mana pengguna mendeskripsikan *use case* mereka (misal: *"Deteksi retak pada mesin pabrik"*). Aplikasi akan memilihkan tipe *task* secara cerdas.
- **Kolom Kanan (Manual Task Selection)**: *Grid* tombol untuk *AI Engineer* (*Classification, Object Detection, Instance Segmentation, Pose, OCR*).

### 4.2. Open Vision (Project Workspace Details)
Masuk ke dalam spesifik proyek, layar utama *Main Content* memuat navigasi sub-tab horizontal yang mewakili siklus MLOps:

#### Tab A: Dataset
Tempat mengatur unggahan dan anotasi data.
- **Upload Media**: *User* dapat mengunggah gambar statis atau video. Jika video, *modal* khusus akan meminta pengaturan ekstraksi *frame* (misal: "Extract 2 frames per second").
- **Two-Card Workflow**: Layar dipecah menjadi dua *Tab Card* internal:
  1. **[Unannotated] (Raw)**: Kumpulan gambar mentah hasil unggahan/ekstraksi.
  2. **[Annotated]**: Kumpulan gambar yang sudah memiliki label *bounding-box/polygon*.
- **Annotation Tool & SAM3 Label Assist**: Ketika *user* mengklik gambar di tab *Unannotated*, editor anotasi terbuka. Terdapat tombol `[Auto-Annotate]` yang ditenagai oleh model fondasi SAM3 secara lokal untuk *zero-shot labeling*. Setiap gambar yang selesai dianotasi otomatis berpindah ke tab *Annotated*.

#### Tab B: Versions
Manajemen pembuatan rilis dataset yang dikunci (*read-only*).
- **Generate Version Wizard (3-Steps)**: Mengikuti standar kejelasan Roboflow.
  1. **Split**: Pengaturan porsi porsi Train / Valid / Test menggunakan *slider* (default: 70/20/10).
  2. **Preprocessing**: *Checkboxes* untuk Auto-Orient, Resize (pilihan resolusi statis), Grayscale.
  3. **Augmentations**: *Checkboxes* untuk Flip, Rotate, Noise, Bounding Box Crop. Terdapat input `Multiplier` (contoh: 3x, artinya 100 gambar asli diubah menjadi 300 variasi).
- **Version List**: Menampilkan rilis (e.g. `Version 1: 300 imgs`, `Version 2: 900 imgs`).

#### Tab C: Train Model
Dashboard pengawasan pelatihan model lokal.
- **Konfigurasi**: Memilih `Version` yang akan dilatih dan memilih arsitektur dasar (misal `YOLOv8n` atau `YOLO11s`).
- **Live Monitoring**: Saat tombol `[Start Training]` ditekan, UI menampilkan dua grafik *real-time*: **Loss Chart** dan **mAP Chart**, bersama dengan estimasi waktu selesai.

### 4.3. Models & Playgrounds Handoff
Siklus tidak berhenti pada model yang berhasil dilatih.
- **Models View**: Menampilkan daftar semua model kustom yang dihasilkan dari *Open Vision*.
- **Seamless Handoff**: Terdapat tombol `[Test in Playground]` pada setiap model. Mengklik tombol ini akan **langsung** melempar *user* ke modul **Playgrounds**, memuat antarmuka *VueFlow Node Canvas*, dan meletakkan model kustom tersebut di dalam blok `Inference Node`, siap dihubungkan dengan kamera dan fungsi logika lanjutan (*Zone Polygon*, dsb).
