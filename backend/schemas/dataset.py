from typing import Literal

from pydantic import BaseModel, Field


class DatasetAsset(BaseModel):
    id: str
    project_id: str
    kind: str
    filename: str
    stored_path: str
    content_type: str = ""
    status: str = "unassigned"
    annotations: dict = Field(default_factory=dict)
    source_asset_id: str | None = None
    created_at: str
    updated_at: str


class DatasetUploadResponse(BaseModel):
    assets: list[DatasetAsset]


class AutoAnnotateResponse(BaseModel):
    annotated_count: int
    assets: list[DatasetAsset]


class AssignAssetsRequest(BaseModel):
    asset_ids: list[str]


class AugmentationConfig(BaseModel):
    key: str
    enabled: bool = False
    params: dict = Field(default_factory=dict)


class VersionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    split: dict[str, int] = Field(default_factory=lambda: {"train": 70, "valid": 20, "test": 10})
    preprocessing: list[AugmentationConfig] = Field(default_factory=list)
    augmentation_mode: str = Field(default="basic")
    augmentation_preset: str | None = Field(default="medium")
    augmentations: list[AugmentationConfig] = Field(default_factory=list)
    multiplier: int = Field(default=1, ge=1, le=10)


class DatasetVersion(BaseModel):
    id: str
    project_id: str
    name: str
    description: str = ""
    split: dict[str, int]
    preprocessing: list[dict] = Field(default_factory=list)
    augmentation_mode: str = "basic"
    augmentation_preset: str | None = None
    augmentations: list[dict] = Field(default_factory=list)
    multiplier: int
    asset_count: int
    split_counts: dict[str, int] = Field(default_factory=dict)
    created_at: str


class AugmentationPreviewRequest(BaseModel):
    augmentation_key: str
    params: dict = Field(default_factory=dict)
    asset_id: str | None = None


class AssetAnnotationsUpdate(BaseModel):
    annotations: dict
    status: Literal["unassigned", "unannotated", "annotated"]
