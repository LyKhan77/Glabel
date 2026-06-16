# Frontend Product Requirements Document (PRD): Glabel Workspace

## 1. Project Context
**Glabel** adalah platform interaktif lokal (berjalan di perangkat *AI Engineers*) untuk melakukan pengujian model Computer Vision secara *real-time*. Dokumen ini berfokus pada spesifikasi antarmuka pengguna (Frontend).

## 2. Tech Stack & Architecture
- **Framework**: **Vue 3 + Vite**. Pemilihan Vue 3 didasarkan pada keunggulan *Composition API* yang reaktif dan ringan untuk mengatur *state* kanvas yang kompleks tanpa *overhead* re-rendering yang berlebihan.
- **Canvas Engine**: **VueFlow** (dikustomisasi penuh untuk *Canvas Node Builder*).
- **Styling**: Vanilla CSS atau TailwindCSS (Utility-first) dengan tema khusus.
- **Communication Protocol**: Menggunakan **WebSockets** untuk menerima *streaming frame* dan respons JSON secara *real-time* dari backend.

## 3. UI/UX & Design Guidelines
Desain antarmuka Glabel mengacu pada kaidah premium dan fungsional seperti yang direkomendasikan pada standar desain aplikasi *expert* (referensi: skill `ui-ux-pro-max` / `impeccable`):
- **Tipografi**: Sesuai `DESIGN.md` menggunakan font *Berkeley Mono*.
- **Visual Style**: Desain kaku (*austere*), tanpa elemen *drop shadow*, latar *cream* (`#fdfcfc`), border *hairline*, tombol kotak radius 4px (`rounded.sm`).
- **Logo**: Menggunakan konsep *Block-Pixel Eye* tanpa teks.

## 4. Information Architecture (IA) & Navigation Flow

### 4.1. App Map / Wireflow (Launcher-to-Fullscreen)
Glabel menggunakan pendekatan **Launcher-to-Fullscreen**. Dashboard bertindak sebagai titik awal (Launcher) yang steril. Saat pengguna memasuki *Workspace*, kanvas mengambil alih seluruh layar tanpa interupsi navigasi dari Dashboard.

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
  │    └── Tempat merangkai Node (Mendukung Hybrid Wire)
  └── Right Sidebar: Properties Panel
       └── (Muncul saat Node diklik) Menampilkan detail parameter dan metrik
```

## 5. Core Modes & Task Flow

### 5.1. Inference Playground (Sandbox Mode)
1. **Launch**: Buka aplikasi ➔ Tampil Dashboard ➔ Klik `[+] New Inference Playground`.
2. **Hardware Target Selection**: Pengguna memilih target eksekusi via Toolbar (default: GPU).
3. **Node Construction (Hybrid Wire)**:
   - *User* men-drag Node dari Palette ke Canvas.
   - **Koneksi Manual (Default)**: Menarik kabel dari ujung (*port*) Node ke Node lain.
   - **Koneksi Auto-connect**: Menggunakan *shortcut* (misal: tekan `Shift` sambil men-drop Node baru) untuk menyambungkan Node secara otomatis ke Node terdekat.
4. **Real-time Tuning**: Parameter diubah di Properties Panel, *output* visual di Node dan metrik akan ter-update seketika (menerima *stream* dari WebSocket).

### 5.2. In-Canvas Output Visualization & Interaction
- **Output Nodes**: Menampilkan *Metrics Panel* dan hasil visualisasi inferensi secara langsung **di dalam badan node tersebut** (*In-Canvas Preview*), alih-alih menggunakan jendela melayang yang terpisah.
- **Interactive ROI**: Pengguna dapat menggambar Polygon/Garis di atas video *preview* yang ada di dalam Node untuk membatasi area analitik.

### 5.3. Vision Solution (End-to-End Mode)
- **Data Relinking Alert**: Jika file sumber berpindah (*broken path*), UI akan memunculkan modal peringatan dan tombol "Relink Dataset Folder".
- **Active Learning Feedback**: Menyediakan pintasan (*shortcut* seperti tombol Spasi/F) saat melihat *live preview* untuk memicu instruksi *Flagging* ke backend secara manual.
