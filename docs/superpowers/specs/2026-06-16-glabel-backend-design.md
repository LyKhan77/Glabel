# Glabel Backend Architecture Design

## 1. Overview
Glabel is an open-source, locally-hosted visual pipeline builder for Computer Vision tasks. This document outlines the backend architecture, focusing on a lightweight, fast, and local-only ecosystem suitable for MVP deployment without global scaling requirements.

## 2. Core Stack
- **Language**: Python 3.10+
- **Web Framework**: FastAPI (chosen for its asynchronous capabilities and native WebSocket support).
- **Communication**: REST API for standard CRUD operations, WebSockets for real-time model training progress and Playground node inference signals.
- **Task Management**: `asyncio` and FastAPI `BackgroundTasks` for non-blocking ML inference and dataset processing.

## 3. Storage & Database
Given the "Local Studio" philosophy, the application eschews heavy SQL databases in favor of local file management.
- **Metadata Management**: Flat JSON files (`workspaces.json`, `playgrounds.json`, `settings.json`) stored in a user-configurable Data Directory (default: `./glabel_data`).
- **Dataset Storage**: Standard OS file structures. Images and labels will be saved natively in formats directly consumable by Ultralytics (e.g., YOLO `.txt` annotations).

## 4. Machine Learning Engine
- **Base Framework**: PyTorch.
- **Vision Library**: `ultralytics`.
- **Supported Tasks**: Image Classification, Object Detection, Instance Segmentation, Pose Estimation. (OCR deferred for future scope).
- **Supported Architectures**: YOLOv11, YOLO26 (or equivalent YOLO variants), RT-DETR/RF-DETR.

## 5. API Module Structure (Proposed)
The backend logic will be modularized as follows:
- `backend/main.py`: Application entry point and global middleware setup.
- `backend/api/routes_projects.py`: JSON-based CRUD for Workspaces.
- `backend/api/routes_dataset.py`: Media uploading, image serving, and auto-annotation logic.
- `backend/api/routes_training.py`: Ultralytics training lifecycle, versioning, and WebSocket emitters for progress tracking.
- `backend/api/routes_playgrounds.py`: Canvas DAG parsing, executing node-based inference pipelines, and real-time visualization.
- `backend/core/storage.py`: Utilities for reading/writing JSON metadata files and managing the native filesystem.

## 6. Success Criteria
- The backend successfully runs locally without complex Docker or DB server dependencies.
- FastAPI seamlessly serves the Vue 3 frontend while running ML operations in the background.
- WebSockets properly stream Ultralytics training epochs back to the frontend UI.
