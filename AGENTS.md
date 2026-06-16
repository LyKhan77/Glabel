# Glabel — Agent & Project Operating Manual

<!-- LIVING DOCUMENT: Sections marked `[KEEP UPDATED]` are editable and MUST be -->
<!-- kept accurate as the codebase changes. See "Documentation Maintenance".    -->
<!-- The RULES section and the behavioral guidelines below the `====` dividers   -->
<!-- are generic agent rules and should not be edited.                           -->

README.md is the canonical, detailed project doc. AGENTS.md orients an agent fast — most sections below summarize README and link to it.

## Project Overview · `[KEEP UPDATED]`

Open-source, **local-first** visual pipeline builder for Computer Vision (ComfyUI/Jupyter-style). Frontend = Vue 3 + VueFlow node canvas; Backend = Python FastAPI with flat-JSON storage; planned ML engine = PyTorch + Ultralytics (YOLOv11, RT-DETR) with WebSocket progress streaming. Runs entirely on localhost — no SQL DB, no Docker required. See README §Project Overview for detail.

## Project Guidelines · `[KEEP UPDATED]`

- **Local-first philosophy:** no remote services, no SQL database. State = flat JSON files under `./glabel_data`.
- **Simplicity & surgical changes** are mandatory (see RULES + behavioral guidelines below).
- **Plan before code:** brainstorm → spec → plan → execute. Save plans to `docs/plans/` (never commit them).
- **Atomic persistence:** all state mutations go through `storage.update_json` — never read+manual-write.
- **Commit per logical change**; roll back via git history.
- **Keep docs in sync:** update README + AGENTS "Current State" as part of every change.

## Tech Stack · `[KEEP UPDATED]`

- Frontend: Vue 3, Vite 4, `@vue-flow/core`, `vue-router` (Node v22).
- Backend: FastAPI, Uvicorn, Pydantic v2, `filelock`, OpenCV headless, pytest + httpx (Python 3.10+).
- Storage: flat JSON files (local `./glabel_data`, gitignored).
- Planned: PyTorch, `ultralytics` (YOLOv11, RT-DETR), WebSockets.

## Key Features · `[KEEP UPDATED]`

- Done: VueFlow node canvas, app shell, frontend/backend project integration, atomic JSON storage, Projects CRUD API, dataset upload/video frame extraction, annotation state, dataset versions, `/health`.
- Planned: WebSocket streaming, real SAM/YOLO annotation output, Ultralytics training lifecycle, image serving, Playground DAG execution.

## Project Structure · `[KEEP UPDATED]`

```
glabel/
├─ frontend/                      # Vue 3 + Vite + VueFlow app (dev :3000)
│  ├─ index.html
│  ├─ package.json                # deps: vue, vue-router, @vue-flow/core
│  ├─ vite.config.js              # dev server port 3000
│  ├─ public/
│  │  └─ platypus-glabel.png
│  └─ src/
│     ├─ main.js                  # app entry
│     ├─ App.vue                  # root component + router outlet
│     ├─ components/
│     │  ├─ layout/Sidebar.vue
│     │  └─ nodes/                # VueFlow canvas nodes
│     │     ├─ InputNode.vue
│     │     ├─ InferenceNode.vue
│     │     └─ OutputNode.vue
│     └─ views/                   # routed pages
│        ├─ Dashboard.vue
│        ├─ Workspace.vue         # node canvas (VueFlow)
│        ├─ ProjectView.vue
│        ├─ ModelsView.vue
│        ├─ PlaygroundsDashboard.vue
│        ├─ VisionJourney.vue
│        └─ SettingsView.vue
├─ backend/                       # FastAPI app (run from project root, :8000)
│  ├─ main.py                     # app, lifespan, CORS, router mount, /health
│  ├─ requirements.txt
│  ├─ core/
│  │  ├─ config.py                # get_data_dir() (env GLABEL_DATA_DIR)
│  │  └─ storage.py               # atomic + locked JSON read/write/update
│  ├─ schemas/
│  │  ├─ project.py
│  │  └─ dataset.py               # Dataset asset/version models
│  ├─ services/
│  │  ├─ projects.py              # CRUD logic via update_json
│  │  └─ datasets.py              # Upload, frame extraction, versions
│  ├─ api/v1/
│  │  ├─ projects.py              # thin REST routes (/api/v1/projects)
│  │  └─ datasets.py              # dataset + version routes
│  └─ tests/
│     ├─ test_storage.py
│     ├─ test_projects_api.py
│     └─ test_dataset_api.py
│     # (each backend/ subpackage also has an empty __init__.py — not shown)
├─ docs/                          # gitignored — plans/specs/assets, NOT committed
│  ├─ plans/                      # implementation plans (working artifacts)
│  └─ superpowers/{specs,assets}/ # design specs + logos
├─ scripts/                       # local dev start/stop helpers
├─ glabel_data/                   # runtime JSON storage (gitignored, created on run)
├─ AGENTS.md                      # this file
├─ CLAUDE.md
├─ DESIGN.md                      # frontend visual design reference
├─ README.md                      # canonical project doc
└─ .gitignore
```

**Layering (backend):** `api/v1` (thin HTTP routes) → `services` (business logic) → `core/storage` (generic persistence) → `schemas` (Pydantic shapes). See README §Project Structure for the same tree with deeper annotations.

## Perintah Project (Commands) · `[DO NOT CHANGE — canonical, verified]`

<!-- Do NOT change these without re-verifying. See README §Perintah Project. -->
Frontend: `cd frontend && npm install && npm run dev` (Vite → :3000).
Backend (run from project root): `python -m venv .venv`, `.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt`, `.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload` (:8000), `.\.venv\Scripts\python.exe -m pytest backend/tests/ -v`.
Full local app: install dependencies manually first, then `.\scripts\start-dev.ps1` to start backend + frontend, `.\scripts\stop-dev.ps1` to stop them.

## Coding Conventions · `[KEEP UPDATED]`

- Layering: `api/v1` (thin routes) → `services` (logic) → `core/storage` (persistence) → `schemas`. No business logic in routes.
- Backend is a package: run `uvicorn backend.main:app` from project root; absolute imports `from backend.core...`.
- Mutate state only via `storage.update_json` (atomic read-modify-write under one lock).
- TDD: failing test → implement → green (pytest + httpx TestClient).
- Config via env at call time (`GLABEL_DATA_DIR`); tests isolate with `monkeypatch` + `tmp_path`.

## Workflow · `[KEEP UPDATED]`

1. Brainstorm (superpowers:brainstorming) → spec in `docs/superpowers/specs/`.
2. Plan (superpowers:writing-plans) → `docs/plans/` (NOT committed).
3. Execute task-by-task (superpowers:subagent-driven-development): implementer → spec review → quality review → commit.
4. Finish branch (superpowers:finishing-a-development-branch) → push + PR.
5. Update README + this file's Current State.

## Current State (Changelog) · `[KEEP UPDATED]`

**Status:** Frontend/backend integration is wired for project CRUD, dataset upload, video frame extraction, annotation state, and dataset version metadata. Real model training remains out of scope. Active branch `backend/implementation-v1`.

- **2026-06-16** — Backend scaffold: FastAPI package, atomic/locked `storage.py`, Projects CRUD, `/health`, CORS (`:3000`), `lifespan`. 9 tests green.
- **2026-06-16** — Frontend: Vue 3 + VueFlow canvas + app shell (prior work).
- **2026-06-17** — Added README.md; expanded AGENTS.md project sections (this block).
- **2026-06-17** — Added `.venv` workflow, OpenCV-backed dataset upload/video frame extraction APIs, dataset versions, and frontend API client wiring.
- **2026-06-17** — Added Windows PowerShell dev scripts for starting/stopping backend + frontend together.

**Next:** WebSocket layer, real SAM/YOLO annotation output, image serving, Ultralytics training lifecycle.

## Documentation Maintenance

- Sections marked `[KEEP UPDATED]` are living — edit them when the codebase changes.
- `[DO NOT CHANGE]` command list is canonical; only change after verifying it runs.
- README.md is the detailed canonical doc; AGENTS.md is the fast agent orientation.
- Changelog entries are dated `YYYY-MM-DD`, append-only.
- Do **not** commit `docs/`.

===========================

# RULES - DO NOT CHANGE or EDIT this Section

## Important Notes - Project RULES

- Always use relevant skills to help with tasks.
- Always ask the user if there are any plans or discussions that need to be validated.
- Always provide a summary after finishing a task.
- Always update `README.md` whenever there are changes to key features and the app's workflow. Please note the section commands that must not be changed.
- Commit every function change so you can roll back and view the code history in case of a malfunction or a failed change. Also UPDATE the `.gitignore` file whenever a new file is added that needs to be excluded before committing.
- Do not re-read files that have already been read in this session unless necessary.
- Minimize non-essential tool calls.
- Save every plan or specification to the `docs/plans/` folder so you can track which plans have been created or are currently being created. This allows you to resume the session if the AI agent's token expires. USE `Superpowers` skill to provide the plan. REMEMBER This file does not need to be updated unless requested. It is intended solely as a record of past information. Make sure not to DUPLICATE it; if you’ve already created a plan outside of Superpowers, there’s no need to create another one, and vice versa.
- DO NOT commit the Plans.

===========================

# AGENTS.md — DO NOT EDIT BELOW

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
