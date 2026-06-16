import os
from pathlib import Path


def get_data_dir() -> Path:
    """Data directory, overridable via env for tests/config. Read at call time."""
    return Path(os.getenv("GLABEL_DATA_DIR", "./glabel_data")).resolve()
