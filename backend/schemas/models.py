from pydantic import BaseModel

class ModelItem(BaseModel):
    id: str
    name: str
    architecture: str
    task_type: str
    size_mb: float
    url: str
    is_downloaded: bool = False
