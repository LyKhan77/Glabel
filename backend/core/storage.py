import copy
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Callable, TypeVar

from filelock import FileLock

from backend.core.config import get_data_dir

logger = logging.getLogger(__name__)
T = TypeVar("T")


def _path(filename: str) -> Path:
    return get_data_dir() / filename


def _lock(filename: str) -> FileLock:
    return FileLock(str((get_data_dir() / f"{filename}.lock").resolve()))


def _atomic_write(path: Path, data) -> None:
    """Write to a temp file in the same dir, then atomically replace."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)  # atomic on same filesystem, incl. Windows
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _ensure_dir() -> None:
    get_data_dir().mkdir(parents=True, exist_ok=True)


def read_json(filename: str, default=None):
    _ensure_dir()
    try:
        with _lock(filename):
            path = _path(filename)
            if not path.exists():
                return copy.deepcopy(default)
            with open(path, "r", encoding="utf-8") as f:
                return copy.deepcopy(json.load(f))
    except json.JSONDecodeError:
        logger.error("Corrupt JSON file: %s — returning default", filename)
        return copy.deepcopy(default)


def write_json(filename: str, data) -> None:
    _ensure_dir()
    with _lock(filename):
        _atomic_write(_path(filename), data)


def update_json(filename: str, default, mutator: Callable[[T], T]):
    """Atomic read-modify-write under a single lock.

    `mutator(data)` MUST mutate `data` in place and may return a value to the
    caller. The mutated `data` is persisted; the return value is passed back.
    """
    _ensure_dir()
    with _lock(filename):
        path = _path(filename)
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = copy.deepcopy(default)
        except json.JSONDecodeError:
            logger.error("Corrupt JSON file: %s — resetting to default", filename)
            data = copy.deepcopy(default)
        result = mutator(data)
        _atomic_write(path, data)
        return result
