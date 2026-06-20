# Glabel

> Open-source, locally-hosted **visual pipeline builder for Computer Vision**. Design and train vision models (detection, segmentation, classification, pose) by wiring nodes on a canvas — no cloud, no SQL database, no deployment ceremony. Think ComfyUI / Jupyter, but for CV model pipelines.

<!-- ====================================================================== -->
<!-- LIVING DOCUMENT — this README is maintained by humans and AI agents.     -->
<!-- Update the sections marked [KEEP UPDATED] whenever the codebase changes. -->
<!-- See "Documentation Maintenance" at the bottom for what triggers an update.-->
<!-- ====================================================================== -->

## Project Overview  ·  `[KEEP UPDATED]`

Glabel is a **local-first** studio for building Computer Vision pipelines. The frontend is a node-based canvas (VueFlow) where users compose a DAG of input → inference → output nodes ("Playgrounds"). The backend is a Python FastAPI service that persists state as flat JSON files and will host the ML engine (PyTorch + Ultralytics) for training and real-time inference, streaming progress back over WebSockets.

The project intentionally avoids heavy infrastructure: no SQL database, no Docker requirement, no remote services. Everything runs on `localhost`, mirroring the ergonomics of ComfyUI and Jupyter.

**Two halves:**
- **Frontend** — Vue 3 + Vite + VueFlow. Visual canvas, dashboard, model/playground/project/settings views. *(built)*
- **Backend** — Python + FastAPI. JSON storage engine, REST CRUD, future ML + WebSocket layer. *(scaffolded — see Current State)*

## Tech Stack  ·  `[KEEP UPDATED]`

| Layer | Technology | Version target |
|---|---|---|
| Frontend framework | Vue 3 (`<script>` / SFC) | ^3.3 |
| Frontend build | Vite | ^4.4 |
| Canvas / DAG | `@vue-flow/core` | ^1.29 |
| Routing | `vue-router` | ^4.2 |
| Icons | `lucide-vue-next` | ^0.x |
| Backend framework | FastAPI | >=0.110 |
| ASGI server | Uvicorn (`[standard]`) | >=0.27 |
| Validation | Pydantic v2 | >=2.6 |
| Concurrency / file lock | `filelock` | >=3.13 |
| Video frame extraction | `opencv-python-headless` | >=4.10 |
| ML (planned) | PyTorch, `ultralytics` (YOLOv11, RT-DETR) | future |
| Storage | Flat JSON files (local `./glabel_data`) | — |
| Tests | pytest + httpx | >=8.0 / >=0.27 |
| Runtimes | Node v22, Python 3.10+ (developed on 3.12) | — |

## Key Features  ·  `[KEEP UPDATED]`

**Implemented:**
- Visual node canvas with input / inference / output nodes (VueFlow).
- App shell: Dashboard, Models, Playgrounds, Project, Settings, Vision Journey, Workspace views.
- Backend: atomic, lock-protected JSON storage engine (crash-safe, race-free).
- Backend: full Projects CRUD REST API + `/health`.
- Frontend/backend integration for project list, create, and detail flows.
- Backend dataset upload API with image/video ingestion and OpenCV frame extraction.
- Backend dataset auto-annotation state transition.
- Dataset versions management with 4-step wizard, interactive augmentation preview (OpenCV), and train/valid/test split generation.
- Full dataset export support for YOLO and COCO format in ZIP archives.
- Dataset page with 50-image pagination for Unassigned/Annotating panes and page-scoped selection.
- Dataset annotation studio with task-aware classification, bounding box, polygon, COCO pose tools, compact image queue, and long-filename handling.
| **2026-06-16** | Backend scaffold | Kosong | FastAPI package, atomic JSON `storage.py`, Projects CRUD, `/health`, CORS, `lifespan` placeholder. |
| **2026-06-16** | Frontend app shell | Kosong | Vue 3 + VueFlow canvas + app shell (prior work). |
| **2026-06-17** | Documentation | Hanya `AGENTS.md` sederhana | `README.md` lengkap dan ekstensi seksi proyek di `AGENTS.md`. |
| **2026-06-17** | Dataset APIs & Scripts | Upload belum didukung | API *upload* OpenCV, *video frame extraction*, *PowerShell scripts*, dan integrasi API *frontend*. |
| **2026-06-17** | Annotation Workspace | Tampilan *Project* kosong | UI Assignment & *scaffold* Workspace di `ProjectView.vue`. |
| **2026-06-17** | Interactive Canvas Editor | *Mock overlays* statis (HTML biasa) | *Native SVG overlay* untuk *Pan/Zoom*, *Classes CRUD*, *BBox*, *Polygon*, dan *COCO Skeleton Template*. Tersedia *Save API*. |
| **2026-06-18** | Annotation Studio | Canvas dan toolbar anotasi belum proper | Studio anotasi task-aware untuk classification, box, polygon, dan COCO pose; koordinat natural-image, undo/redo, mock AI assist, dan coverage round-trip anotasi. |
| **2026-06-19** | Dataset Unassigned Actions | Asset unassigned harus dipilih satu-satu dan tidak bisa dihapus | Tambah Select all dan Delete untuk asset unassigned; backend menghapus record dan file asset yang masih unassigned. |
| **2026-06-19** | Dataset Annotating Actions | Asset annotating tidak bisa dipilih untuk dikembalikan | Tambah select di pane Annotating, Return to Unassigned, dan cursor guide horizontal/vertical di canvas anotasi. |
| **2026-06-20** | Annotation UX Polish | Anotasi perlu tombol Save dan delete ada di toolbar | Anotasi autosave, delete annotation pindah ke list Annotations, dan image di queue annotation bisa dihapus langsung. |
| **2026-06-21** | Dataset Browsing UX | Dataset panes merender semua asset dan queue annotation boros ruang untuk filename panjang | Tambah pagination 50 image/page, Select page, filename clamp/ellipsis, dan queue annotation compact. |
| **2026-06-21** | Dataset Versions Overhaul | Fitur Dataset Versions berupa list statis dan form kosong | Implementasi 4-step Version Wizard, OpenCV augmentation preview, VersionCard, VersionDetail slide-over, split logic, dan full YOLO/COCO export ke ZIP. |

**In development / next:**
- WebSocket layer (training progress, playground inference).
- Real SAM/YOLO auto-annotation output integration, image serving, Ultralytics training lifecycle execution.

---

## Documentation Maintenance

This README and `AGENTS.md` are **living documents**. Keep them accurate:

| When you change… | Update this section |
|---|---|
| Dependencies / runtimes | Tech Stack |
| New feature shipped | Key Features, Current State & Changelog (add dated entry) |
| Files / folders added or moved | Project Structure |
| Commands or ports | Perintah Project (test before changing) |
| New API endpoint | API Reference |
| Architectural rules / patterns | Coding Conventions |
| Dev process change | Workflow |

Rules:
- The **Perintah Project** command list is **canonical** — only change after verifying it runs.
- **Changelog** entries are dated (`YYYY-MM-DD`) and append-only.
- Do **not** commit files under `docs/` (plans/specs are working artifacts).
