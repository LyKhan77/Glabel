from fastapi import APIRouter, HTTPException

from backend.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from backend.services import projects as svc

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectResponse])
def list_projects():
    return svc.list_projects()


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(payload: ProjectCreate):
    return svc.create_project(payload)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    project = svc.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, payload: ProjectUpdate):
    project = svc.update_project(project_id, payload)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str):
    if not svc.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted", "id": project_id}
