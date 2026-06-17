from typing import Literal
from pydantic import BaseModel, Field


class ProjectClass(BaseModel):
    id: str
    name: str
    color: str


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = ""
    task_type: Literal[
        "classification", 
        "object_detection", 
        "segmentation", 
        "pose_estimation"
    ] = "object_detection"
    classes: list[ProjectClass] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = None
    classes: list[ProjectClass] | None = None


class ProjectResponse(ProjectBase):
    id: str
    created_at: str
    updated_at: str
