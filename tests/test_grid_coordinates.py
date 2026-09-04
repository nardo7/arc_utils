import pytest

from arc_utils import GridPair


def test_to_continuous_coordinates_maps_input_grid_to_centered_positions() -> None:
    pair = GridPair(input=[[1, 2], [3, 4]], output=[[0, 0], [0, 0]])

    objects = pair.to_continuous_coordinates(object_size=2.0, min_separation=1.0)

    assert [(obj.color, obj.x, obj.y) for obj in objects] == [
        (1, -2.5, -2.5),
        (2, -2.5, 0.5),
        (3, 0.5, -2.5),
        (4, 0.5, 0.5),
    ]
    assert all(obj.width == 2.0 and obj.height == 2.0 for obj in objects)


def test_to_continuous_coordinates_skips_background_zeros() -> None:
    pair = GridPair(input=[[0, 1], [0, 0]], output=[[0, 0], [0, 0]])

    objects = pair.to_continuous_coordinates(object_size=1.0, min_separation=1.0)

    assert len(objects) == 1
    assert objects[0].color == 1
    assert objects[0].x == -1.5
    assert objects[0].y == 0.5


def test_to_continuous_coordinates_can_use_output_grid() -> None:
    pair = GridPair(input=[[1, 1]], output=[[7, 8]])

    objects = pair.to_continuous_coordinates(
        object_size=1.0,
        min_separation=1.0,
        grid="output",
    )

    assert [(obj.color, obj.x, obj.y) for obj in objects] == [
        (7, -0.5, -1.5),
        (8, -0.5, 0.5),
    ]

    assert pair.to_grid_coordinates(
        objects[1].x, objects[1].y, 1.0, 1.0, grid="output"
    ) == (0, 1)


def test_to_continuous_coordinates_handles_1x1_grid() -> None:
    pair = GridPair(input=[[9]], output=[[0]])

    objects = pair.to_continuous_coordinates(object_size=0.4, min_separation=0.2)

    assert len(objects) == 1
    assert objects[0].color == 9
    assert objects[0].x == pytest.approx(-0.2)
    assert objects[0].y == pytest.approx(-0.2)
    assert objects[0].width == pytest.approx(0.4)
    assert objects[0].height == pytest.approx(0.4)


def test_to_continuous_coordinates_handles_8x8_grid_edges_and_spacing() -> None:
    grid = [[0] * 8 for _ in range(8)]
    grid[0][0] = 1
    grid[0][7] = 2
    grid[7][0] = 3
    grid[7][7] = 4
    pair = GridPair(input=grid, output=[[0] * 8 for _ in range(8)])

    objects = pair.to_continuous_coordinates(object_size=0.05, min_separation=0.05)

    assert [(obj.color, obj.x, obj.y) for obj in objects] == [
        (1, pytest.approx(-0.375), pytest.approx(-0.375)),
        (2, pytest.approx(-0.375), pytest.approx(0.325)),
        (3, pytest.approx(0.325), pytest.approx(-0.375)),
        (4, pytest.approx(0.325), pytest.approx(0.325)),
    ]
    assert all(obj.width == pytest.approx(0.05) for obj in objects)
    assert all(obj.height == pytest.approx(0.05) for obj in objects)


@pytest.mark.parametrize(
    ("object_size", "min_separation", "message"),
    [
        (0.0, 0.0, "Object size must be positive"),
        (-1.0, 0.0, "Object size must be positive"),
        (1.0, -0.1, "Minimum separation must be non-negative"),
    ],
)
def test_to_continuous_coordinates_rejects_invalid_layout_parameters(
    object_size: float,
    min_separation: float,
    message: str,
) -> None:
    pair = GridPair(input=[[1]], output=[[0]])

    with pytest.raises(ValueError, match=message):
        pair.to_continuous_coordinates(
            object_size=object_size,
            min_separation=min_separation,
        )


def test_to_continuous_coordinates_rejects_invalid_grid_selector() -> None:
    pair = GridPair(input=[[1]], output=[[2]])

    with pytest.raises(ValueError, match="grid must be either"):
        pair.to_continuous_coordinates(
            object_size=1.0,
            min_separation=0.0,
            grid="foo",
        )
