from __future__ import annotations

from arc_utils.models import GridPair, Split, Task
from arc_utils.tasks import load_tasks


def grid_size(grid: list[list[int]]) -> tuple[int, int]:
    if not grid:
        return (0, 0)
    return (len(grid), len(grid[0]))


def grid_area(grid: list[list[int]]) -> int:
    rows, cols = grid_size(grid)
    return rows * cols


def color_count(grid: list[list[int]]) -> int:
    return len({color for row in grid for color in row if color > 0})


def non_zero_pixel_count(grid: list[list[int]]) -> int:
    return sum(1 for row in grid for color in row if color != 0)


def get_non_zero_pixels(grid: list[list[int]]) -> dict[tuple[int, int], int]:
    pixels: dict[tuple[int, int], int] = {}
    for row_index, row in enumerate(grid):
        for column_index, color in enumerate(row):
            if color != 0:
                pixels[(row_index, column_index)] = color
    return pixels


def get_different_output_pixels(pair: GridPair) -> list[tuple[int, int, int, int]]:
    input_pixels = get_non_zero_pixels(pair.input)
    output_pixels = get_non_zero_pixels(pair.output)
    different_pixels: list[tuple[int, int, int, int]] = []

    for row_index, column_index in sorted(output_pixels):
        input_color = input_pixels.get((row_index, column_index), 0)
        output_color = output_pixels[(row_index, column_index)]
        if input_color != output_color:
            different_pixels.append((row_index, column_index, input_color, output_color))

    return different_pixels


def sort_key_by_max_pair_area(task: Task) -> int:
    return max(max(grid_area(pair.input), grid_area(pair.output)) for pair in task.train + task.test)


def get_tasks_smaller_than(tasks: list[Task], max_size: int) -> list[Task]:
    """
    Filters tasks where all grids have a size smaller than or equal to max_size.

    Args:
        tasks (list[Task]): The list of tasks to filter.
        max_size (int): The maximum size allowed for the grids.

    Returns:
        list[Task]: The filtered list of tasks.
    """
    filtered_tasks: list[Task] = []
    for task in tasks:
        if all(
            grid_size(pair.input)[0] <= max_size
            and grid_size(pair.input)[1] <= max_size
            and grid_size(pair.output)[0] <= max_size
            and grid_size(pair.output)[1] <= max_size
            for pair in task.train + task.test
        ):
            filtered_tasks.append(task)
    return filtered_tasks


def get_tasks_outputs_with_max_colors(tasks: list[Task], max_colors: int) -> list[Task]:
    """
    Filters tasks where all output grids have a number of colors less than or equal to max_colors.

    Args:
        tasks (list[Task]): The list of tasks to filter.
        max_colors (int): The maximum number of colors allowed in the output grids.

    Returns:
        list[Task]: The filtered list of tasks.
    """
    filtered_tasks: list[Task] = []
    for task in tasks:
        if all(color_count(pair.output) <= max_colors for pair in task.train + task.test):
            filtered_tasks.append(task)
    return filtered_tasks


def get_tasks_with_max_output_pixels(tasks: list[Task], max_pixels: int) -> list[Task]:
    """
    Filters tasks where all output grids have a number of non-zero pixels less than or equal to max_pixels.
    Args:
        tasks (list[Task]): The list of tasks to filter.
        max_pixels (int): The maximum number of non-zero pixels allowed in the output grids.

    Returns:
        list[Task]: The filtered list of tasks.
    """
    filtered_tasks: list[Task] = []
    for task in tasks:
        if all(non_zero_pixel_count(pair.output) <= max_pixels for pair in task.train + task.test):
            filtered_tasks.append(task)
    return filtered_tasks


# def get_tasks_with_max_output_pixels_color(tasks: list[Task], max_pixels: int, color: int) -> list[Task]:
#     """
#     Filters tasks where all output grids have a number of pixels of a specific color less than or equal to max_pixels.
#     Args:
#         tasks (list[Task]): The list of tasks to filter.
#         max_pixels (int): The maximum number of pixels of the specified color allowed in the output grids.
#         color (int): The specific color to check in the output grids.   """
#     filtered_tasks: list[Task] = []
#     # check max pixels in the outputs for the specified color
#     for task in tasks:
#         if all(
#             sum(1 for row in pair.output for c in row if c == color) <= max_pixels
#             for pair in task.train + task.test
#         ):
#             filtered_tasks.append(task)
#     return filtered_tasks


def filter_max_output_pixels_per_color(tasks: list[Task], max_pixels: int) -> list[Task]:
    """
    Filters tasks where all output grids have a number of pixels of each color less than or equal to max_pixels.
    Args:
        tasks (list[Task]): The list of tasks to filter.
        max_pixels (int): The maximum number of pixels of each color allowed in the output grids.

    Returns:
        list[Task]: The filtered list of tasks.
    """
    filtered_tasks: list[Task] = []
    for task in tasks:
        if all(
            sum(1 for row in pair.output for cell in row if cell == color) <= max_pixels
            for pair in task.train + task.test
            for color in range(1, 10)
        ):
            filtered_tasks.append(task)
    return filtered_tasks


def sort_by_amount_of_output_pixels(tasks: list[Task], reverse: bool = False) -> list[Task]:
    """
    Sorts tasks by the total number of non-zero pixels in their output grids in ascending order by default.
    """
    return sorted(
        tasks,
        key=lambda task: max(non_zero_pixel_count(pair.output) for pair in task.train + task.test),
        reverse=reverse,
    )


def get_tasks_with_pixel_amount_difference_less_than(tasks: list[Task], max_difference: int) -> list[Task]:
    filtered_tasks: list[Task] = []
    for task in tasks:
        amount_pixels_input = [non_zero_pixel_count(pair.input) for pair in task.train + task.test]
        amount_pixels_output = [non_zero_pixel_count(pair.output) for pair in task.train + task.test]

        if all(
            input_pixels >= output_pixels or abs(input_pixels - output_pixels) <= max_difference
            for input_pixels, output_pixels in zip(amount_pixels_input, amount_pixels_output, strict=False)
        ):
            filtered_tasks.append(task)
    return filtered_tasks


def get_tasks_with_different_pixels_less_than(tasks: list[Task], max_difference: int) -> list[Task]:
    filtered_tasks: list[Task] = []
    for task in tasks:
        keep_task = True
        for pair in task.train + task.test:
            input_pixel_count = non_zero_pixel_count(pair.input)
            output_pixel_count = non_zero_pixel_count(pair.output)

            if output_pixel_count >= input_pixel_count:
                different_pixels = get_different_output_pixels(pair)
                if len(different_pixels) > max_difference:
                    keep_task = False
                    break

        if keep_task:
            filtered_tasks.append(task)
    return filtered_tasks


def get_era_bench_tasks() -> list[Task]:
    training_tasks = load_tasks(split=Split.TRAIN)
    evaluation_tasks = load_tasks(split=Split.EVALUATION)
    tasks = training_tasks + evaluation_tasks
    tasks = get_tasks_smaller_than(tasks, max_size=8)
    tasks = get_tasks_outputs_with_max_colors(tasks, 4)
    tasks = filter_max_output_pixels_per_color(tasks, 12)
    filtered_tasks = ["e872b94a"]
    tasks = [task for task in tasks if task.task_id not in filtered_tasks]

    return tasks
