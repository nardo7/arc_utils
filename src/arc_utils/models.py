from __future__ import annotations
from enum import Enum

from pydantic import BaseModel, field_validator

from .colors import ARC_COLOR_TO_COLOR


class Split(Enum):
    TRAIN = "training"
    EVALUATION = "evaluation"


class GridPair(BaseModel):
    input: list[list[int]]
    output: list[list[int]]

    def __repr__(self):
        def format_grid(grid: list[list[int]]) -> str:
            return "\n".join(" ".join(str(cell) for cell in row) for row in grid)

        return "GridPair(\n" f"input:\n{format_grid(self.input)}\n" f"output:\n{format_grid(self.output)}\n" ")"

    def to_continuous_coordinates(
        self,
        object_size: float,
        min_separation: float,
        grid: str = "input",
    ) -> list[Pixel]:
        if object_size <= 0:
            raise ValueError("Object size must be positive.")
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

        plane_width = row_count * object_size + (row_count - 1) * min_separation
        plane_height = col_count * object_size + (col_count - 1) * min_separation
        object_width, object_height = object_size, object_size
        center = (0.0, 0.0)
        min_x = center[0] - plane_width / 2
        min_y = center[1] - plane_height / 2

        x0 = min_x
        y0 = min_y

        step_x = object_width + min_separation
        step_y = object_height + min_separation

        objects: list[Pixel] = []
        for row_index, row in enumerate(grid_data):
            for col_index, color in enumerate(row):
                if color == 0:
                    continue
                x = x0 + row_index * step_x
                y = y0 + col_index * step_y
                objects.append(
                    Pixel(
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


class Pixel(BaseModel):
    color: int
    x: float
    y: float
    width: float
    height: float

    def get_color(self) -> str:
        color = ARC_COLOR_TO_COLOR.get(self.color)
        return "unknown" if color is None else color.value
