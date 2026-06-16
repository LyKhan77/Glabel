# Glabel Backend Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a FastAPI application to serve as the Glabel Web Backend, establishing the fundamental JSON storage engine and basic Workspace CRUD API.

**Architecture:** Python FastAPI modular application using `APIRouter`. A custom `storage.py` utility will manage JSON file read/writes for state persistency.

**Tech Stack:** Python 3.10+, FastAPI, Uvicorn, JSON.

---

### Task 1: Scaffold Backend Project & Core Storage Utility

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/core/storage.py`

- [ ] **Step 1: Define Dependencies**
Create `backend/requirements.txt`:
```txt
fastapi==0.103.2
uvicorn==0.23.2
pydantic==2.4.2
python-multipart==0.0.6
```

- [ ] **Step 2: Create Core JSON Storage Utility**
Create `backend/core/storage.py` to handle generic JSON file reads and writes.
```python
import json
import os
from pathlib import Path

DATA_DIR = Path("./glabel_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def _get_path(filename: str) -> Path:
    return DATA_DIR / filename

def read_json(filename: str, default_val=None):
    if default_val is None:
        default_val = []
    path = _get_path(filename)
    if not path.exists():
        return default_val
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_val

def write_json(filename: str, data):
    path = _get_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
```

- [ ] **Step 3: Setup FastAPI Main Entry Point**
Create `backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Glabel Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Glabel Backend Running"}
```

- [ ] **Step 4: Verify Server Starts**
Run: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload &`
(Or simply run `python -m uvicorn main:app &` and check if it boots successfully without crashing).

- [ ] **Step 5: Commit**
```bash
git add backend/
git commit -m "chore: scaffold fastapi backend and json storage core"
```

---

### Task 2: Implement Workspace CRUD API

**Files:**
- Create: `backend/api/routes_projects.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create Projects API Router**
Create `backend/api/routes_projects.py`:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from backend.core.storage import read_json, write_json

router = APIRouter(prefix="/api/projects", tags=["projects"])
FILE_NAME = "workspaces.json"

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class ProjectResponse(ProjectCreate):
    id: str

@router.get("/", response_model=List[ProjectResponse])
def get_projects():
    return read_json(FILE_NAME, default_val=[])

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate):
    projects = read_json(FILE_NAME, default_val=[])
    new_project = {
        "id": f"proj-{uuid.uuid4().hex[:8]}",
        "name": project.name,
        "description": project.description
    }
    projects.append(new_project)
    write_json(FILE_NAME, projects)
    return new_project

@router.delete("/{project_id}")
def delete_project(project_id: str):
    projects = read_json(FILE_NAME, default_val=[])
    new_projects = [p for p in projects if p.get("id") != project_id]
    if len(projects) == len(new_projects):
        raise HTTPException(status_code=404, detail="Project not found")
    write_json(FILE_NAME, new_projects)
    return {"status": "deleted", "id": project_id}
```

- [ ] **Step 2: Mount Router in main.py**
Modify `backend/main.py` to include the router:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import routes_projects

app = FastAPI(title="Glabel Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_projects.router)

@app.get("/")
def read_root():
    return {"status": "Glabel Backend Running"}
```

- [ ] **Step 3: Verify API Logic**
Wait for auto-reload or run tests. We can simulate a `curl -X GET http://127.0.0.1:8000/api/projects/` to verify empty list output.

- [ ] **Step 4: Commit**
```bash
git add backend/
git commit -m "feat: implement workspace projects json crud api"
```
