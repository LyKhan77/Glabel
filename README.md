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
- Backend dataset auto-annotation state transition and dataset version metadata.
- Dataset annotation studio with task-aware classification, bounding box, polygon, and COCO pose tools.
- Per-project local data directory (`GLABEL_DATA_DIR`), gitignored.

**Planned (roadmap):**
- WebSocket layer streaming Ultralytics training epochs / playground inference signals.
- Real SAM/YOLO auto-annotation output and image serving.
- Model training lifecycle and Playground DAG execution.
- Training-time export formats for annotated datasets.

## Project Structure  ·  `[KEEP UPDATED]`

```
glabel/
├─ frontend/                  # Vue 3 + Vite + VueFlow app (dev :3000)
│  ├─ src/
│  │  ├─ App.vue, main.js
│  │  ├─ api/client.js        # fetch client for FastAPI
│  │  ├─ utils/               # annotation geometry + task helpers
│  │  ├─ views/               # Dashboard, ModelsView, PlaygroundsDashboard,
│  │  │                       # ProjectView, SettingsView, VisionJourney, Workspace
│  │  ├─ components/layout/   # Sidebar
│  │  └─ components/nodes/    # InputNode, InferenceNode, OutputNode
│  ├─ tests/                  # Node tests for frontend utilities
│  └─ vite.config.js          # dev server port 3000
├─ backend/                   # FastAPI app (run from project root, :8000)
│  ├─ main.py                 # app, lifespan, CORS, router mount, /health
│  ├─ core/
│  │  ├─ config.py            # get_data_dir() (env GLABEL_DATA_DIR)
│  │  └─ storage.py           # atomic + locked JSON read/write/update
│  ├─ api/v1/                 # thin REST routes → services
│  ├─ services/               # CRUD, dataset ingestion, version logic
│  ├─ schemas/                # Pydantic models
│  ├─ tests/                  # pytest backend API/storage tests
│  └─ requirements.txt
├─ docs/            # plans + specs (gitignored — NOT committed)
├─ scripts/         # local dev start/stop helpers
├─ DESIGN.md                  # frontend visual design reference
├─ AGENTS.md                  # agent + project operating manual
└─ README.md                  # this file
```

## Perintah Project (Commands)  ·  `[DO NOT CHANGE — canonical, verified]`

> **These commands are canonical and tested.** Do not alter them without re-verifying they work. (Per AGENTS.md rule: the command section must not be changed.)

**Frontend** (run from `frontend/`):
```bash
cd frontend
npm install
npm run dev        # Vite dev server → http://localhost:3000
npm run build      # production build → frontend/dist
npm run preview    # preview the production build
```

**Backend** (run from the **project root**, package mode):
```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload    # → http://127.0.0.1:8000
.\.venv\Scripts\python.exe -m pytest backend/tests/ -v             # 29 tests, expect all pass
```

**Full local app** (run from the **project root**, Windows PowerShell):
```powershell
.\scripts\start-dev.ps1 # starts backend + frontend after deps are installed manually
.\scripts\stop-dev.ps1  # stops backend + frontend started by the script
```

> Run the backend from the project root (not from inside `backend/`): the app is a package (`uvicorn backend.main:app`), so imports like `from backend.core.storage import ...` resolve correctly.

## API Reference  ·  `[KEEP UPDATED]`

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe → `{"status":"ok"}` |
| GET | `/api/v1/projects/` | List all projects |
| POST | `/api/v1/projects/` | Create (`{"name","description?"}`) → 201 |
| GET | `/api/v1/projects/{id}` | Get project detail |
| PATCH | `/api/v1/projects/{id}` | Partial update (`{"name?","description?"}`) → 200 |
| DELETE | `/api/v1/projects/{id}` | Delete → 200 `{"status":"deleted","id"}` |
| POST | `/api/v1/projects/{id}/dataset/upload` | Upload image/video files; videos extract frames via OpenCV |
| GET | `/api/v1/projects/{id}/dataset/assets` | List dataset assets (`?status=unannotated|annotated`) |
| PATCH | `/api/v1/projects/{id}/dataset/assets/unassign` | Return selected annotating assets to Unassigned |
| DELETE | `/api/v1/projects/{id}/dataset/assets` | Delete selected unassigned dataset assets |
| PUT | `/api/v1/projects/{id}/dataset/assets/{asset_id}/annotations` | Save asset annotations and status |
| POST | `/api/v1/projects/{id}/dataset/auto-annotate` | Mark non-video dataset assets as annotated |
| GET | `/api/v1/projects/{id}/versions` | List dataset versions |
| POST | `/api/v1/projects/{id}/versions` | Create dataset version metadata |

Interactive docs: `http://127.0.0.1:8000/docs` (Swagger UI, FastAPI default).

## Coding Conventions  ·  `[KEEP UPDATED]`

- **Backend layered architecture:** `api/v1/` (thin HTTP routes) → `services/` (business logic) → `core/storage.py` (generic persistence) → `schemas/` (Pydantic shapes). Routes contain no business logic.
- **Package mode:** backend runs as `uvicorn backend.main:app` from project root. Use absolute imports `from backend.core.storage import ...`.
- **All state mutations go through `storage.update_json`** (atomic read-modify-write under a single lock) — never `read_json` + manual `write_json`.
- **TDD:** write the failing test first, implement, then green. pytest + httpx `TestClient`.
- **Config via env at call time** (`GLABEL_DATA_DIR`) so tests isolate with `monkeypatch` + `tmp_path`.
- **Surgical, minimal changes**; match existing style; no speculative abstraction (see AGENTS.md §Simplicity / §Surgical).
- **Commit per logical change**; never commit `docs/` plans.

## Workflow  ·  `[KEEP UPDATED]`

1. **Brainstorm** the feature (superpowers:brainstorming) → write a spec in `docs/superpowers/specs/`.
2. **Plan** step-by-step (superpowers:writing-plans) → save to `docs/plans/`. *(Plans are NOT committed.)*
3. **Execute** task-by-task (superpowers:subagent-driven-development): implementer → spec review → quality review → commit.
4. **Finish** the branch (superpowers:finishing-a-development-branch) → push + PR.
5. **Update docs** (README + AGENTS "Current State") as part of the change.

## Current State & Changelog  ·  `[KEEP UPDATED]`

**Status:** Frontend and backend are integrated for project CRUD, dataset upload, video frame extraction, annotation state, dataset version metadata, and interactive canvas annotation tools (Classes, BBox, Polygon, Pose Skeleton). Real model training remains intentionally out of scope for this branch.

**Active branch:** `feat/enhance-openvision`.

### Changelog
| Date | Feature | Before | After |
|---|---|---|---|
| **2026-06-16** | Backend scaffold | Kosong | FastAPI package, atomic JSON `storage.py`, Projects CRUD, `/health`, CORS, `lifespan` placeholder. |
| **2026-06-16** | Frontend app shell | Kosong | Vue 3 + VueFlow canvas + app shell (prior work). |
| **2026-06-17** | Documentation | Hanya `AGENTS.md` sederhana | `README.md` lengkap dan ekstensi seksi proyek di `AGENTS.md`. |
| **2026-06-17** | Dataset APIs & Scripts | Upload belum didukung | API *upload* OpenCV, *video frame extraction*, *PowerShell scripts*, dan integrasi API *frontend*. |
| **2026-06-17** | Annotation Workspace | Tampilan *Project* kosong | UI Assignment & *scaffold* Workspace di `ProjectView.vue`. |
| **2026-06-17** | Interactive Canvas Editor | *Mock overlays* statis (HTML biasa) | *Native SVG overlay* untuk *Pan/Zoom*, *Classes CRUD*, *BBox*, *Polygon*, dan *COCO Skeleton Template*. Tersedia *Save API*. |
| **2026-06-18** | Annotation Studio | Canvas dan toolbar anotasi belum proper | Studio anotasi task-aware untuk classification, box, polygon, dan COCO pose; koordinat natural-image, undo/redo, mock AI assist, dan coverage round-trip anotasi. |
| **2026-06-19** | Dataset Unassigned Actions | Asset unassigned harus dipilih satu-satu dan tidak bisa dihapus | Tambah Select all dan Delete untuk asset unassigned; backend menghapus record dan file asset yang masih unassigned. |
| **2026-06-19** | Dataset Annotating Actions | Asset annotating tidak bisa dipilih untuk dikembalikan | Tambah select di pane Annotating, Return to Unassigned, dan cursor guide horizontal/vertical di canvas anotasi. |

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
