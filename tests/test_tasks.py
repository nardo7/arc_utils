from arc_utils import (
    GridPair,
    available_task_ids,
    get_different_output_pixels,
    get_tasks_smaller_than,
    get_tasks_outputs_with_max_colors,
    load_task,
    load_tasks,
    sort_key_by_max_pair_area,
    task_path,
)
from arc_utils.analysis import filter_max_output_pixels_per_color
from arc_utils.models import Split, Task


def test_task_path_points_to_existing_evaluation_file() -> None:
    assert task_path("00576224", split="evaluation").exists()


def test_load_task_returns_arc_shape() -> None:
    task = load_task("00576224", split="evaluation")

    assert task.task_id == "00576224"
    assert task.train
    assert task.test


def test_available_task_ids_lists_known_task() -> None:
    assert "00576224" in available_task_ids(split="evaluation")


def test_load_tasks_returns_typed_tasks() -> None:
    tasks = load_tasks(split="evaluation")

    assert tasks
    assert tasks[0].task_id


def test_different_output_pixels_detects_new_or_changed_pixels() -> None:
    pair = GridPair(input=[[0, 1], [0, 0]], output=[[0, 2], [3, 0]])

    assert get_different_output_pixels(pair) == [(0, 1, 1, 2), (1, 0, 0, 3)]


def test_notebook_filters_can_select_tasks() -> None:
    tasks = load_tasks(split="evaluation")

    smaller_than_eight = get_tasks_smaller_than(tasks, 8)
    max_four_colors = get_tasks_outputs_with_max_colors(smaller_than_eight, 4)

    assert smaller_than_eight
    assert max_four_colors


def test_sort_key_uses_largest_grid_area_in_task() -> None:
    task = Task(
        task_id="area",
        train=[GridPair(input=[[0, 0]], output=[[0], [0], [0]])],
        test=[GridPair(input=[[0]], output=[[0, 0], [0, 0]])],
        split=Split.TRAIN,
    )

    assert sort_key_by_max_pair_area(task) == 4


def test_filter_max_output_pixels_per_color_requires_every_color_to_fit() -> None:
    within_limit = Task(
        task_id="within-limit",
        train=[GridPair(input=[[0]], output=[[1, 1, 2]])],
        test=[],
        split=Split.TRAIN,
    )
    over_limit = Task(
        task_id="over-limit",
        train=[GridPair(input=[[0]], output=[[1, 1, 1]])],
        test=[],
        split=Split.TRAIN,
    )

    assert filter_max_output_pixels_per_color(
        [within_limit, over_limit], max_pixels=2
    ) == [within_limit]