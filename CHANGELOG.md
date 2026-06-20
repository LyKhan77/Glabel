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
