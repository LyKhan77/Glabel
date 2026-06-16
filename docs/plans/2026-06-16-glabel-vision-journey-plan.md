# Glabel Vision Solution (E2E Journey) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the "Open Vision Solution" End-to-End MLOps frontend journey using Vue 3 and mock data for E2E testing.

**Architecture:** Murni frontend Vue 3. Terdapat urutan layar (Wizard) yang dipisahkan oleh *routes* atau *state component* (Task Definition -> Ingestion & Annotation -> Versioning -> Training -> Playground).

**Tech Stack:** Vue 3, Vue Router. Desain menggunakan *austere styling* (kaku, cream bg, monospace font).

---

### Task 1: Setup Journey Routing & Wizard Container

**Files:**
- Create: `frontend/src/views/VisionJourney.vue`
- Modify: `frontend/src/main.js`
- Modify: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: Add Route**
Di `frontend/src/main.js`, tambahkan route `/journey` yang mengarah ke `VisionJourney.vue`.

- [ ] **Step 2: Connect Dashboard Button**
Ubah tombol `[Folder] Open Vision Solution` di `Dashboard.vue` untuk melakukan navigasi ke `/journey`. Hapus alert mock sebelumnya.

- [ ] **Step 3: Create Journey Shell Container**
Buat `VisionJourney.vue` yang menggunakan *state* `currentStep` (dimulai dari 1 hingga 4). Layout memiliki *Header* sederhana "Vision Solution Journey" dan tombol `[X] Cancel` untuk kembali ke Dashboard.

- [ ] **Step 4: Commit**
`git add frontend/src/`
`git commit -m "feat: setup vision journey routing and shell"`

### Task 2: Step 1 - Task Definition Wizard

**Files:**
- Modify: `frontend/src/views/VisionJourney.vue`

- [ ] **Step 1: Create Task Input UI**
Tampilkan UI sederhana dengan 1px border. Terdapat input `[Task Name]` dan *dropdown* `[Use Case / Task Type]` (Object Detection, Instance Segmentation, OCR).

- [ ] **Step 2: Next Button**
Sediakan tombol `[>] Start Journey` yang akan memindahkan `currentStep` ke 2.

- [ ] **Step 3: Commit**
`git commit -am "feat: implement task definition step"`

### Task 3: Step 2 & 3 - Data Ingestion & Dataset Versioning

**Files:**
- Modify: `frontend/src/views/VisionJourney.vue`

- [ ] **Step 1: Data Ingestion & Label Assist UI (Step 2)**
Jika `currentStep === 2`, tampilkan dua kolom: Kiri adalah daftar gambar (*mock array*), Kanan adalah area "Label Assist (SAM3)".
Tambahkan tombol `[Auto-Annotate via SAM3]`. Saat ditekan, muncul *mock alert* "Annotating 100 images...".
Tambahkan tombol `[>] Next: Versioning`.

- [ ] **Step 2: Dataset Versioning UI (Step 3)**
Jika `currentStep === 3`, tampilkan *checkboxes* untuk Pre-Processing (Resize 640x640, Grayscale) dan Augmentation (Flip, Rotate, Brightness).
Tambahkan *input multiplier* (misal: "Generate 3x images").
Tambahkan tombol `[>] Create Version & Train`.

- [ ] **Step 3: Commit**
`git commit -am "feat: implement ingestion and versioning steps"`

### Task 4: Step 4 - Local Training Dashboard

**Files:**
- Modify: `frontend/src/views/VisionJourney.vue`

- [ ] **Step 1: Training Dashboard UI**
Jika `currentStep === 4`, tampilkan layar "Training Model...".
Gunakan `setInterval` secara *mock* untuk menaikkan persentase `Epoch: 1/100` hingga `100/100` dan `mAP` naik dari `0.1` ke `0.85`.

- [ ] **Step 2: Redirect to Playground**
Setelah mencapai 100%, tampilkan tombol `[🚀] Open in Playground` yang akan memicu `router.push('/workspace')`.

- [ ] **Step 3: Commit**
`git commit -am "feat: implement mock training dashboard"`
