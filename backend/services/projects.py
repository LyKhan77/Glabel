import uuid
from datetime import datetime, timezone

from backend.core.storage import read_json, update_json
from backend.schemas.project import ProjectCreate, ProjectUpdate

FILE_NAME = "projects.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def list_projects() -> list[dict]:
    return read_json(FILE_NAME, default=[])


def get_project(project_id: str):
    for project in list_projects():
        if project["id"] == project_id:
            return project
    return None


def create_project(data: ProjectCreate) -> dict:
    def mut(projects):
        project = {
            "id": str(uuid.uuid4()),
            "name": data.name,
            "description": data.description,
            "task_type": data.task_type,
            "classes": [c.model_dump() for c in data.classes] if data.classes else [],
            "created_at": _now(),
            "updated_at": _now(),
        }
        projects.append(project)
        return project

    return update_json(FILE_NAME, [], mut)


def update_project(project_id: str, data: ProjectUpdate):
    def mut(projects):
        for p in projects:
            if p["id"] == project_id:
                if data.name is not None:
                    p["name"] = data.name
                if data.description is not None:
                    p["description"] = data.description
                if data.classes is not None:
                    p["classes"] = [c.model_dump() for c in data.classes]
                p["updated_at"] = _now()
                return p
        return None

    return update_json(FILE_NAME, [], mut)


def delete_project(project_id: str) -> bool:
    def mut(projects):
        before = len(projects)
        projects[:] = [p for p in projects if p["id"] != project_id]
        return len(projects) != before

    return update_json(FILE_NAME, [], mut)
