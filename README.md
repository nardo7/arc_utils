# arc_utils

Installable Python package for ARC-AGI utilities used in this thesis workspace.
The package expects ARC task files under `arc_utils/data/`.
It now includes reusable code promoted from the analysis notebook: typed task models, loaders, and task-filtering helpers.

## Install

```bash
pip install -e ./arc_utils
```

For development extras:

```bash
pip install -e ./arc_utils[dev]
```

## Example

```python
from arc_utils import get_tasks_smaller_than, load_task, load_tasks, task_path

task = load_task("00576224", split="evaluation")
path = task_path("00576224", split="evaluation")
small_tasks = get_tasks_smaller_than(load_tasks(split="evaluation"), 8)
```
