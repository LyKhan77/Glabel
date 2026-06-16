from pydantic import BaseModel, Field


class DatasetAsset(BaseModel):
    id: str
    project_id: str
    kind: str
    filename: str
    stored_path: str
    content_type: str = ""
    status: str = "unannotated"
    source_asset_id: str | None = None
    created_at: str
    updated_at: str


class DatasetUploadResponse(BaseModel):
    assets: list[DatasetAsset]


class AutoAnnotateResponse(BaseModel):
    annotated_count: int
    assets: list[DatasetAsset]


class VersionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    split: dict[str, int] = Field(default_factory=lambda: {"train": 70, "valid": 20, "test": 10})
    preprocessing: list[str] = Field(default_factory=list)
    augmentations: list[str] = Field(default_factory=list)
    multiplier: int = Field(default=1, ge=1)


class DatasetVersion(BaseModel):
    id: str
    project_id: str
    name: str
    split: dict[str, int]
    preprocessing: list[str]
    augmentations: list[str]
    multiplier: int
    asset_count: int
    created_at: str
