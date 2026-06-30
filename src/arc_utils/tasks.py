from __future__ import annotations

import json
from pathlib import Path
from arc_utils.models import Task
from arc_utils.models import Split


def _normalize_split(split: Split | str) -> Split:
    if isinstance(split, Split):
        return split
    try:
        return Split(split)
    except ValueError as error:
        allowed = ", ".join(member.value for member in Split)
        raise ValueError(f"Invalid split '{split}'. Expected one of: {allowed}.") from error


def package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_root() -> Path:
    return package_root() / "data"


def task_path(task_id: str, split: Split | str = Split.TRAIN) -> Path:
    split = _normalize_split(split)
    normalized_id = task_id.removesuffix(".json")
    return data_root() / split.value / f"{normalized_id}.json"


def available_task_ids(split: Split | str = Split.TRAIN) -> list[str]:
    split = _normalize_split(split)
    split_dir = data_root() / split.value
    return sorted(path.stem for path in split_dir.glob("*.json"))


def load_task_from_path(file_path: Path, split: Split = Split.TRAIN) -> Task:
    task_id = file_path.stem
    with file_path.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)

    data["task_id"] = task_id
    data["split"] = split.value
    return Task.model_validate(data)


def load_task(task_id: str, split: Split | str = Split.TRAIN) -> Task:
    split = _normalize_split(split)
    path = task_path(task_id=task_id, split=split)
    if not path.exists():
        raise FileNotFoundError(f"Task '{task_id}' not found in split '{split}': {path}")

    return load_task_from_path(path, split=split)


def load_tasks(split: Split | str = Split.TRAIN) -> list[Task]:
    split = _normalize_split(split)
    return [load_task(task_id, split=split) for task_id in available_task_ids(split=split)]
