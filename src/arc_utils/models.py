from __future__ import annotations

from pydantic import BaseModel, field_validator


class GridPair(BaseModel):
    input: list[list[int]]
    output: list[list[int]]

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