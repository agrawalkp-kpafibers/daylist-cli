"""Read and write the user's tasks as JSON."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def default_data_file() -> Path:
    """Return the data file, allowing an override for scripts and tests."""
    override = os.environ.get("DAYLIST_DATA_FILE")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".daylist" / "tasks.json"


def load_tasks(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read {path}: {exc}") from exc
    if not isinstance(data, list) or any(not isinstance(task, dict) for task in data):
        raise ValueError(f"Invalid task data in {path}")
    return data


def save_tasks(path: Path, tasks: list[dict[str, Any]]) -> None:
    """Replace the data file atomically to avoid partial writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".daylist-", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(tasks, temp_file, indent=2, ensure_ascii=False)
            temp_file.write("\n")
        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
