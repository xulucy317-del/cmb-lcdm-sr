"""Small shared utilities: device selection and atomic JSON/text output."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import numpy as np


def get_device(prefer: str = "auto") -> str:
    """Return 'cuda', 'mps' or 'cpu'. `prefer` can force a specific device."""
    import torch

    if prefer != "auto":
        return prefer
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(obj: Any, path: str | Path) -> None:
    """Atomically write strict JSON, mapping non-finite numbers to null."""
    text = json.dumps(
        _json_sanitize(obj), indent=2, allow_nan=False,
        default=_json_default,
    ) + "\n"
    save_text(text, path)


def save_text(text: str, path: str | Path) -> None:
    """Atomically replace a UTF-8 text file on its destination filesystem."""
    path = Path(path)
    ensure_dir(path.parent)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with open(temporary, "x") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _json_default(o: Any):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Object of type {type(o)} is not JSON serializable")


def _json_sanitize(obj: Any) -> Any:
    """Recursively convert NumPy values and non-finite floats for JSON.

    Python's JSON encoder emits ``NaN`` and ``Infinity`` by default even
    though neither token is part of the JSON standard.  Sanitising before the
    strict ``allow_nan=False`` write keeps unavailable numerical diagnostics
    explicit as ``null`` while retaining every finite value unchanged.
    """
    if isinstance(obj, np.ndarray):
        return _json_sanitize(obj.tolist())
    if isinstance(obj, np.generic):
        return _json_sanitize(obj.item())
    if isinstance(obj, dict):
        return {key: _json_sanitize(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_sanitize(value) for value in obj]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj
