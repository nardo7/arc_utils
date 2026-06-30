from __future__ import annotations
from enum import Enum

from pydantic import BaseModel, field_validator

class Split(Enum):
    TRAIN = "training"
    EVALUATION = "evaluation"

class GridPair(BaseModel):
    input: list[list[int]]
    output: list[list[int]]

    def __repr__(self):
        def format_grid(grid: list[list[int]]) -> str:
            return "\n".join(" ".join(str(cell) for cell in row) for row in grid)

        return (
            "GridPair(\n"
            f"input:\n{format_grid(self.input)}\n"
            f"output:\n{format_grid(self.output)}\n"
            ")"
        )


    @staticmethod
    def from_continuous_coordinates(
        objects: list[Object],
        grid_size: tuple[int, int],
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float,
        object_size: tuple[float, float],
        min_separation: float,
        grid: str = "output",
    ) -> GridPair:
        rows, cols = grid_size
        if rows <= 0 or cols <= 0:
            raise ValueError("grid_size must contain positive row and column counts.")
        if grid not in {"input", "output"}:
            raise ValueError("grid must be either 'input' or 'output'.")

        object_width, object_height = object_size
        plane_width = max_x - min_x
        plane_height = max_y - min_y
        required_width = rows * object_width + (rows - 1) * min_separation
        required_height = cols * object_height + (cols - 1) * min_separation
        x0 = min_x + (plane_width - required_width) / 2
        y0 = min_y + (plane_height - required_height) / 2
        step_x = object_width + min_separation
        step_y = object_height + min_separation

        reconstructed_grid = [[0] * cols for _ in range(rows)]
        for obj in objects:
            row_index = round((obj.x - x0) / step_x)
            col_index = round((obj.y - y0) / step_y)
            if not (0 <= row_index < rows and 0 <= col_index < cols):
                raise ValueError(
                    f"Object at ({obj.x}, {obj.y}) maps outside the grid bounds."
                )
            reconstructed_grid[row_index][col_index] = obj.color

        zero_grid = [[0] * cols for _ in range(rows)]
        if grid == "input":
            return GridPair(input=reconstructed_grid, output=zero_grid)
        return GridPair(input=zero_grid, output=reconstructed_grid)

    def to_continuous_coordinates(
        self,
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float,
        object_size: tuple[float, float],
        min_separation: float,
        grid: str = "input",
    ) -> list[Object]:
        if min_x >= max_x:
            raise ValueError("Expected min_x < max_x.")
        if min_y >= max_y:
            raise ValueError("Expected min_y < max_y.")

        object_width, object_height = object_size
        if object_width <= 0 or object_height <= 0:
            raise ValueError("Object width and height must be positive.")
        if min_separation < 0:
            raise ValueError("Minimum separation must be non-negative.")

        if grid == "input":
            grid_data = self.input
        elif grid == "output":
            grid_data = self.output
        else:
            raise ValueError("grid must be either 'input' or 'output'.")

        row_count = len(grid_data)
        col_count = len(grid_data[0])

        plane_width = max_x - min_x
        plane_height = max_y - min_y

        required_width = row_count * object_width + (row_count - 1) * min_separation
        required_height = col_count * object_height + (col_count - 1) * min_separation

        if required_width > plane_width:
            raise ValueError(
                "Grid does not fit horizontally in the provided bounds with the given "
                "object size and minimum separation."
            )
        if required_height > plane_height:
            raise ValueError(
                "Grid does not fit vertically in the provided bounds with the given "
                "object size and minimum separation."
            )

        horizontal_margin = (plane_width - required_width) / 2
        vertical_margin = (plane_height - required_height) / 2

        x0 = min_x + horizontal_margin
        y0 = min_y + vertical_margin

        step_x = object_width + min_separation
        step_y = object_height + min_separation

        objects: list[Object] = []
        for row_index, row in enumerate(grid_data):
            for col_index, color in enumerate(row):
                if color == 0:
                    continue
                x = x0 + row_index * step_x
                y = y0 + col_index * step_y
                objects.append(
                    Object(
                        color=color,
                        x=x,
                        y=y,
                        width=object_width,
                        height=object_height,
                    )
                )

        return objects

    @field_validator("input")
    def validate_input_grid(cls, value: list[list[int]]) -> list[list[int]]:
        if not value:
            raise ValueError("Input grid cannot be empty.")
        row_length = len(value[0])
        for row in value:
            if len(row) != row_length:
                raise ValueError("All rows in the input grid must have the same length.")
            for color in row:
                if not isinstance(color, int) or color < 0:
                    raise ValueError("All colors in the input grid must be non-negative integers.")
        return value
    
    @field_validator("output")
    def validate_output_grid(cls, value: list[list[int]]) -> list[list[int]]:
        if not value:
            raise ValueError("Output grid cannot be empty.")
        row_length = len(value[0])
        for row in value:
            if len(row) != row_length:
                raise ValueError("All rows in the output grid must have the same length.")
            for color in row:
                if not isinstance(color, int) or color < 0:
                    raise ValueError("All colors in the output grid must be non-negative integers.")
        return value
    


class Task(BaseModel):
    task_id: str
    train: list[GridPair]
    test: list[GridPair]
    split: Split
    rules: list[str] = []


class Object(BaseModel):
    color: int
    x: float
    y: float
    width: float
    height: float

    def get_color(self) -> str:
        match self.color:
            case 1:
                return "blue"
            case 2:
                return "red"
            case 3:
                return "green"
            case 4:
                return "yellow"
            case 5:
                return "grey"
            case 6:
                return "fuschia"
            case 7:
                return "orange"
            case 8:
                return "teal"
            case 9:
                return "brown"
            case _:
                return "unknown"