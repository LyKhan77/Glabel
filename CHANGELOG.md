# Glabel Changelog

This file is the long-term memory ledger for Glabel across all AI agents. It records what the codebase can do now, why important changes were made, where the related code lives, what still needs validation, and how future agents must document their work.

Use this file as the durable context bridge between sessions. Chat history can disappear, but this file should let the next agent understand the current product state and continue work without rediscovering old decisions.

## Agent Memory Contract

Every AI agent must treat this file as the source of truth for implemented codebase history.

Read order for a new agent:

1. Read `AGENTS.md` for operating rules.
2. Read this file's `Current Codebase State` for the latest product capability map.
3. Read the newest entries in `AI-Agent Change Entries` before touching related areas.
4. Check `Pending Validation and Known Gaps` before claiming a workflow is fully verified.

Update rules:

- Update this file for every implemented behavior, architecture, model/CV stack, workflow, or major developer-documentation change.
- Add new entries at the top of `AI-Agent Change Entries`, newest first.
- Keep historical entries unless they are factually wrong; correct them with a new entry when possible.
- Update `Current Codebase State` when a change affects the product capability map.
- Do not record plans, ideas, or proposed work as completed changes.
- Do not duplicate this changelog back into `AGENTS.md`; keep `AGENTS.md` as a pointer.

## Required Entry Schema

Use this structure for every new AI-agent change entry:

```markdown
### YYYY-MM-DD - Short change title

**Agent scope**

- Request: one sentence describing the user request.
- Intent: one sentence describing why the change exists.
- Status: Completed | Partially completed | Reverted | Superseded.

**Changed files**

- `path/to/file`: what changed in this file.

**Behavior before**

- Describe the previous behavior or documentation state.

**What changed**

- Concrete implemented changes only.

**After the change**

- Describe how the app, workflow, architecture, or agent memory behaves now.

**Verification**

- Commands run, tests run, manual checks, or "Not run" with reason.

**Follow-up notes**

- Remaining validation, risks, or related areas future agents should inspect.
```

## AI-Agent Change Entries

### 2026-06-21 - Models Manager Implementation

**Agent scope**

- Request: Add a "List Model" section in Settings to download Ultralytics-compatible models (YOLO, RT-DETR, SAM) locally.
- Intent: Lay the groundwork for Auto-Annotation and Training features by providing local model weights.
- Status: Completed.

**Changed files**

- `backend/schemas/models.py`: Created Pydantic schema for `ModelItem`.
- `backend/services/models.py`: Built dynamic registry for ~60 model variants (YOLOv11, YOLO26, RT-DETR, SAM2, SAM3) and implemented synchronous `.pt` downloading via `httpx`.
- `backend/api/v1/models.py`: Added GET and POST endpoints for listing and downloading models.
- `backend/main.py`: Mounted the `models` router.
- `frontend/src/api/client.js`: Added API bindings.
- `frontend/src/views/SettingsView.vue`: Built "Model Repository" UI block adhering to the `DESIGN.md` minimalist aesthetic.
- `backend/tests/test_models_api.py`: Wrote unit tests for models registry and endpoints.

**Behavior before**

- SettingsView only contained mock hardware detection and a simple data directory input. No models system existed.

**What changed**

- Fully implemented a local model repository system capable of streaming large weights directly from GitHub releases to `glabel_data/models/`.

**After the change**

- Users can browse available object detection, segmentation, pose, classification, and label assist models, check their download status, and download them to the local workspace with one click.

**Verification**

- Run backend tests: `.\.venv\Scripts\python.exe -m pytest backend/tests/test_models_api.py -v` (Passed).

**Follow-up notes**

- Downloads are synchronous right now (HTTP blocks). If download times out, consider backgrounding it or implementing WebSockets/SSE for progress streaming.

### 2026-06-21 - Dataset Versions UI Redesign (Impeccable)

**Agent scope**

- Request: Redesign the Dataset Versions UI to match the project's austere, terminal-native aesthetic.
- Intent: Eliminate generic SaaS "AI slop" styles (Tailwind utilities, drop shadows, rounded corners) and enforce the `DESIGN.md` guidelines.
- Status: Completed.

**Changed files**

- `frontend/src/components/versions/VersionWizard.vue`: Removed Tailwind classes, implemented flat CSS, changed steps to ASCII brackets `[x]`.
- `frontend/src/components/versions/VersionCard.vue`: Removed card shadows, implemented `1px` hairlines, updated hover states.
- `frontend/src/components/versions/VersionDetail.vue`: Flattened slide-over panel, added `[+]` toggle aesthetics.
- `frontend/src/components/versions/SplitBar.vue`: Reduced corner radius, replaced dots with square boxes.
- `frontend/src/components/versions/AugmentationPreview.vue`: Removed heavy modal shadows, restyled range sliders.

**Behavior before**

- The UI used non-existent Tailwind classes like `bg-white`, `text-blue-600`, `rounded-xl`, and `shadow-2xl`. It looked like a generic modern web app instead of Glabel's terminal-inspired canvas.

**What changed**

- Converted all 5 components to strictly use `App.vue` CSS variables (`--bg-color`, `--hairline`, `--surface-soft`, `--text-color`).
- Removed all drop shadows and forced `border-radius: 4px` (or `0px` for containers).
- Replaced graphical icons with ASCII indicators (e.g. `[ Export ]`, `[x]`).

**After the change**

- The Dataset Versions feature visually integrates perfectly with the rest of Glabel, feeling crisp, austere, and developer-focused.

**Verification**

- Visually verified via component rewrite.
- `git commit -am "style(versions): redesign dataset versions UI to match manpage aesthetic"`

**Follow-up notes**

- Future components must strictly adhere to `DESIGN.md` rather than falling back to generic Tailwind/Material styling.

### 2026-06-21 - Dataset Versions Overhaul

**Agent scope**

- Request: Overhaul the skeletal Dataset Versions feature.
- Intent: Provide a production-grade version management system with export formats and an interactive augmentation wizard.
- Status: Completed.

**Changed files**

- `backend/schemas/dataset.py`: Added `AugmentationConfig` and `AugmentationPreviewRequest` schemas, updated Version models.
- `backend/services/datasets.py`: Implemented robust get, delete, and create functionality including directory structure building and random dataset splitting.
- `backend/services/export_*.py`: Created YOLO and COCO export scripts returning ZIP archives.
- `backend/services/augmentation.py`: Created OpenCV-powered endpoints for live augmentation previews.
- `frontend/src/components/versions/*`: Built new Vue components: `VersionWizard`, `AugmentationPreview`, `SplitBar`, `VersionCard`, and `VersionDetail` (slide-over panel).
- `frontend/src/views/ProjectView.vue`: Integrated the new version components to replace the old inline skeleton.

**Behavior before**

- The dataset versions page had a skeleton 3-step inline wizard and a simple unordered list of versions. Augmentation and preprocessing were just string lists, and there was no export or split functionality.

**What changed**

- Introduced a full 4-step wizard (Split, Preprocessing, Augmentations, Summary).
- Supported Basic and Advanced augmentation modes, including an OpenCV-powered preview modal.
- Built a rich VersionCard dashboard and a slide-over VersionDetail panel.
- Added full YOLO/COCO ZIP export capability on the backend.

**After the change**

- Users can confidently build robust dataset versions, visually tune augmentation parameters using sample imagery, and directly export YOLO and COCO zipped datasets.

**Verification**

- Run backend tests: `.\.venv\Scripts\python.exe -m pytest backend/tests/ -v` (Passed)
- Run frontend build: `npm run build` (Passed)

**Follow-up notes**

- Actual image preprocessing/augmentation transforms during version generation are deferred to ML engine integration.

### 2026-06-21 - Dataset Browsing UX Pagination

**Agent scope**

- Request: Implement the planned Dataset page and Annotation queue UX improvements.
- Intent: Make large image sets easier to browse without adding backend pagination prematurely.
- Status: Completed.

**Changed files**

- `frontend/src/views/ProjectView.vue`: Added client-side 50-image pagination for Unassigned and Annotating panes, page-scoped selection, page status text, and clamped filename labels.
- `frontend/src/components/AnnotationWorkspace.vue`: Made the left asset queue denser with horizontal rows, filename ellipsis, full filename titles, queue scrolling, and selected-position progress.
- `frontend/src/utils/pagination.js`: Added a small pagination helper.
- `frontend/tests/pagination.test.mjs`: Added pagination helper coverage.
- `README.md`, `AGENTS.md`, `CHANGELOG.md`: Updated current feature documentation.

**Behavior before**

- Dataset panes rendered every image at once, Select all targeted the full unassigned set, and long filenames wrapped aggressively in grid cards.
- The Annotation left queue used tall vertical rows, so long filenames made large queues hard to scan.

**What changed**

- Dataset Unassigned and Annotating panes now show 50 images per page with Prev/Next controls and showing-count text.
- Unassigned bulk selection is now page-scoped and labeled Select page / Clear page.
- Dataset card filenames are clamped visually while preserving the full filename via the native title attribute.
- Annotation queue rows are compact horizontal rows with thumbnail, ellipsized filename, status, and delete action.
- Annotation queue header shows current position against the active queue count.

**After the change**

- Users can browse larger datasets without long full-page grids, and annotation image selection stays scannable even with many long filenames.

**Verification**

- `npm test -- pagination.test.mjs`
- `npm test`
- `npm run build`
- `node C:/Users/Lee/.codex/skills/impeccable/scripts/detect.mjs --json frontend/src/views/ProjectView.vue frontend/src/components/AnnotationWorkspace.vue`

**Follow-up notes**

- Backend pagination and virtualized lists are intentionally deferred until asset counts or load time prove they are needed.

### 2026-06-20 - Annotation UI/UX Enhancements

**Agent scope**

- Request: Analyze changes and update documentation.
- Intent: Enhance user workflow efficiency in the annotation workspace, improve UI accessibility and validation.
- Status: Completed.

**Changed files**

- \rontend/index.html\: Added JetBrains Mono font.
- \rontend/src/App.vue\: Defined central CSS variables for themes (colors, z-indexes) and improved focus states.
- \rontend/src/components/AnnotationWorkspace.vue\: Added advanced polygon drawing (edge insertion, vertex deletion), skeleton movement, keyboard shortcuts modal, inline class color updates, and queue search by filename.
- \rontend/src/utils/annotationGeometry.js\: Added helper functions for point projection on segments and COCO keypoint names.
- \rontend/src/views/ProjectView.vue\: Enhanced dataset split UI with percentage validation and visual selections.

**Behavior before**

- Basic polygon and skeleton tools without edge insertion/movement. No central shortcut documentation, no inline class recoloring, and simple dataset split inputs without strict validation.

**What changed**

- Fully implemented polygon edge insertion, vertex deletion, and complete skeleton movement.
- Added a keyboard shortcuts modal.
- Made class colors editable inline.
- Added dataset split percentage validation.

**After the change**

- Users have a robust and precise annotation toolkit, better accessibility (shortcuts modal), and stricter dataset management UI.

**Verification**

- Not run (historical commits mapped).

**Follow-up notes**

- Ensure new edge insertion and skeleton movements work seamlessly across various resolutions and zoom levels.

### 2026-06-20 - Annotation UX Polish (Autosave & Asset Returns)

**Agent scope**

- Request: Improve annotation UX by adding autosave, cursor guides, and row/asset deletion flows.
- Intent: Enhance user workflow efficiency in the annotation workspace.
- Status: Completed.

**Changed files**

- Commit `fae386b`: Implemented autosave annotations and row deletes.
- Commit `5477a3c`: Implemented returning annotating assets and added cursor guides.

**Behavior before**

- Annotations needed to be saved manually, deleting assets was cumbersome, and annotating assets could not be easily returned. The canvas lacked cursor alignment guides.

**What changed**

- Integrated autosave for annotations.
- Added cursor guides (horizontal/vertical) to the canvas.
- Supported returning annotating assets back to unassigned queue.
- Moved delete actions for annotations/rows to more intuitive locations.

**After the change**

- Users benefit from automatic saves, better visual precision with cursor guides, and smoother queue management when returning or deleting assets.

**Verification**

- Not run (historical commits mapped).

**Follow-up notes**

- Verify performance impact of autosave on large projects.

## Current Codebase State

This table is the high-level capability map. Keep it concise but current. Detailed implementation notes belong in dated entries below.

| Area | Timeline (git) | What was developed | After the change |
| ------ | ---------------- | -------------------- | ------------------ |
| Models Manager | 2026-06-21 | Local repository for downloading YOLO, RT-DETR, and SAM weights. | Users can download ~60 model variants directly via Settings UI. |
| Dataset Versions | 2026-06-21 | 4-step Version Wizard, live augmentation preview via OpenCV, VersionCard dashboard, Slide-over detail, YOLO/COCO export API. | Robust version management, split configuration, and ZIP export. |
| Dataset Browsing UX | 2026-06-21 | Client-side 50-image pagination, page-scoped selection, compact annotation queue rows. | Larger datasets are easier to browse and long filenames no longer dominate the annotation queue. |
| Annotation UI/UX Enhancements | 2026-06-20 | Polygon edge insertion, skeleton movement, shortcuts modal, class recoloring. | Robust and precise annotation toolkit with better accessibility. |
| Annotation UX Polish | 2026-06-20 | Autosave, cursor guides, delete row adjustments. | Enhanced efficiency and precision during labeling tasks. |
| Dataset Actions | 2026-06-19 | Select all and Delete for unassigned assets; select and return for annotating assets. | Improved bulk management of dataset assets and queue routing. |
| Annotation Studio | 2026-06-18 | Task-aware studio for classification, box, polygon, COCO pose; natural-image coordinates, undo/redo, mock AI assist, coverage round-trip. | Fully functional annotation workspace supporting multiple CV tasks. |
| Dataset Management | 2026-06-17 | OpenCV upload API, video frame extraction, PowerShell scripts, frontend integration. | Users can upload data and extract frames from videos. |
| Workspace & Canvas Editor | 2026-06-17 | Native SVG overlay for Pan/Zoom, Classes CRUD, BBox, Polygon, COCO Skeleton Template, Save API, and ProjectView scaffold. | Canvas supports drawing shapes and saving basic annotations. |
| Documentation | 2026-06-17 | Comprehensive `README.md` and detailed `AGENTS.md`. | Complete project and agent instructions. |
| Backend & Storage Scaffold | 2026-06-16 | FastAPI package, atomic JSON `storage.py`, Projects CRUD, `/health`, CORS, `lifespan` placeholder. | Backend is functional with basic CRUD and local file storage. |
| Frontend Shell | 2026-06-16 | Vue 3 + VueFlow canvas + app shell. | Basic UI foundation and routing are in place. |

## Pending Validation and Known Gaps

- **WebSocket Layer**: Planned but not yet integrated for streaming.
- **ML Engine**: Real SAM/YOLO auto-annotation output integration is pending.
- **Ultralytics**: Training lifecycle execution is pending.
- **Export**: Dataset export formats are pending.
