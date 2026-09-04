# ARC Utils

`arc_utils` is the shared ARC-AGI data and geometry library for the ERA Bench
repositories in this workspace. Its main purpose is to provide one canonical
representation of the bundled ARC tasks and the small set of helpers needed to
turn those tasks into embodied ERA Bench scenes and evaluation task views.

It is not a general ARC solver. The package keeps task loading, palette
definitions, coordinate conversion, and benchmark selection in one place so
that the simulator and its data-preparation tooling agree on the same source
data and conventions.

## ERA Bench role

| Consumer | How it uses `arc_utils` |
| --- | --- |
| `era_bench` | Defines the embodied benchmark membership with `get_era_bench_tasks()`, loads typed ARC tasks, converts non-background cells into scene coordinates, and maps ARC color IDs to material colors. |
| `era_bench_evaluation` | Uses typed task data while `scripts/create_task_views.py` builds task-centric HDF5 views from recorded episodes. |


## Contents

- `data/training/` and `data/evaluation/`: bundled ARC-AGI task JSON files.
- `arc_utils.tasks`: split-aware task discovery and loading.
- `arc_utils.models`: validated `Task` and `GridPair` models, plus conversion
  from ARC grid cells to centered continuous coordinates.
- `arc_utils.colors`: canonical ARC color IDs, names, and linear-RGB material
  values.
- `arc_utils.analysis`: grid statistics and filters, including the ERA Bench
  task-selection function.

## Install

From the workspace root:

```bash
pip install -e ./arc_utils
```

For development dependencies:

```bash
pip install -e ./arc_utils[dev]
```

The task corpus is included in built wheels, so `load_task()` works from both a
source checkout and an installed package.

## Load ARC tasks

Task IDs are file stems. Splits may be supplied as `"training"` or
`"evaluation"` (or as `Split` enum members).

```python
from arc_utils import available_task_ids, load_task, load_tasks, task_path

task = load_task("00576224", split="evaluation")
all_evaluation_tasks = load_tasks(split="evaluation")
path = task_path("00576224", split="evaluation")
ids = available_task_ids(split="evaluation")
```

Each `Task` has a task ID, split, training `GridPair` objects, and test
`GridPair` objects. A grid pair validates that its input and output grids are
non-empty, rectangular, and made of non-negative integer color IDs.

## ERA Bench task set

`get_era_bench_tasks()` is the canonical definition of the embodied ERA Bench
task set. It loads both bundled splits and retains tasks only when every input
and output grid is at most `8 × 8`, every output has at most four
non-background colors, and no non-background color occupies more than 12
output cells. It also explicitly excludes task `e872b94a`.

```python
from arc_utils import get_era_bench_tasks

benchmark_tasks = get_era_bench_tasks()
```

Changes to this function change benchmark membership.

## Scene geometry and colors

`GridPair.to_continuous_coordinates()` turns non-background ARC cells into
centered `Pixel` objects for the embodied scene. Coordinates follow ARC grid
order: the row controls `x`, the column controls `y`, and zero-valued cells are
not emitted. `to_grid_coordinates()` performs the reverse conversion.

```python
from arc_utils import load_task

pair = load_task("00576224", split="evaluation").train[0]
pixels = pair.to_continuous_coordinates(
    object_size=0.05,
    min_separation=0.05,
)
```

`ARC_COLOR_TO_COLOR` maps ARC IDs 1–9 to canonical color names, while
`COLOR_RGB` supplies the equivalent linear-RGB values expected by the scene
materials. ARC ID 0 is the background and has no physical pixel or palette
entry.

