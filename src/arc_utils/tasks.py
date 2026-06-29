from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from arc_utils.models import Task

Split = Literal["training", "evaluation"]


def package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_root() -> Path:
    return package_root() / "data"


def task_path(task_id: str, split: Split = "training") -> Path:
    normalized_id = task_id.removesuffix(".json")
    return data_root() / split / f"{normalized_id}.json"


def available_task_ids(split: Split = "training") -> list[str]:
    split_dir = data_root() / split
    return sorted(path.stem for path in split_dir.glob("*.json"))


def load_task_from_path(file_path: Path) -> Task:
    task_id = file_path.stem
    with file_path.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)

    data["task_id"] = task_id
    return Task.model_validate(data)


def load_task(task_id: str, split: Split = "training") -> Task:
    path = task_path(task_id=task_id, split=split)
    if not path.exists():
        raise FileNotFoundError(f"Task '{task_id}' not found in split '{split}': {path}")

    return load_task_from_path(path)


def load_tasks(split: Split = "training") -> list[Task]:
    return [load_task(task_id, split=split) for task_id in available_task_ids(split=split)]
