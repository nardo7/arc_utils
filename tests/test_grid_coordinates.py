import pytest
from arc_utils import GridPair


def test_to_continuous_coordinates_maps_input_grid_to_expected_positions() -> None:
    pair = GridPair(input=[[1, 2], [3, 4]], output=[[0, 0], [0, 0]])

    objects = pair.to_continuous_coordinates(
        min_x=0,
        min_y=0,
        max_x=5,
        max_y=5,
        object_size=(2, 2),
        min_separation=1,
    )

    assert [(obj.color, obj.x, obj.y) for obj in objects] == [
        (1, 0, 0),
        (2, 0, 3),
        (3, 3, 0),
        (4, 3, 3),
    ]
    assert all(obj.width == 2 and obj.height == 2 for obj in objects)



def test_to_continuous_coordinates_skips_background_zeros() -> None:
    pair = GridPair(input=[[0, 1], [0, 0]], output=[[0, 0], [0, 0]])

    objects = pair.to_continuous_coordinates(
        min_x=0,
        min_y=0,
        max_x=3,
        max_y=3,
        object_size=(1, 1),
        min_separation=1,
    )

    assert len(objects) == 1
    assert objects[0].color == 1


def test_to_continuous_coordinates_can_use_output_grid() -> None:
    pair = GridPair(input=[[1, 1]], output=[[7, 8]])

    objects = pair.to_continuous_coordinates(
        min_x=0,
        min_y=0,
        max_x=1,
        max_y=3,
        object_size=(1, 1),
        min_separation=1,
        grid="output",
    )

    assert [(obj.color, obj.x, obj.y) for obj in objects] == [(7, 0, 0), (8, 0, 2)]


def test_to_continuous_coordinates_raises_when_grid_does_not_fit() -> None:
    pair = GridPair(input=[[1, 2]], output=[[0, 0]])

    with pytest.raises(ValueError, match="fit vertically"):
        pair.to_continuous_coordinates(
            min_x=0,
            min_y=0,
            max_x=2,
            max_y=1,
            object_size=(1, 1),
            min_separation=1,
        )


def test_to_continuous_coordinates_raises_for_invalid_grid_selector() -> None:
    pair = GridPair(input=[[1]], output=[[2]])

    with pytest.raises(ValueError, match="grid must be either"):
        pair.to_continuous_coordinates(
            min_x=0,
            min_y=0,
            max_x=1,
            max_y=1,
            object_size=(1, 1),
            min_separation=0,
            grid="foo",
        )


PLANE = dict(min_x=10.0, min_y=20.0, max_x=16.0, max_y=26.0, object_size=(2.0, 2.0), min_separation=1.0)


def test_from_continuous_coordinates_round_trip_for_output_grid() -> None:
    original = GridPair(input=[[0, 0], [0, 0]], output=[[9, 8], [7, 6]])

    objects = original.to_continuous_coordinates(**PLANE, grid="output")

    reconstructed = GridPair.from_continuous_coordinates(
        objects=objects,
        grid_size=(2, 2),
        **PLANE,
        grid="output",
    )

    assert reconstructed.output == [[9, 8], [7, 6]]


def test_from_continuous_coordinates_round_trip_with_sparse_grid() -> None:
    original = GridPair(input=[[0, 0], [0, 0]], output=[[0, 3], [0, 0]])

    objects = original.to_continuous_coordinates(**PLANE, grid="output")

    assert len(objects) == 1

    reconstructed = GridPair.from_continuous_coordinates(
        objects=objects,
        grid_size=(2, 2),
        **PLANE,
        grid="output",
    )

    assert reconstructed.output == [[0, 3], [0, 0]]


def test_8x8_grid_fits_exactly_and_round_trips() -> None:
    # 8 cells × 0.05 + 7 gaps × 0.05 = 0.75 → zero margins, step = 0.10
    plane_8x8 = dict(min_x=0.0, min_y=0.0, max_x=0.75, max_y=0.75, object_size=(0.05, 0.05), min_separation=0.05)

    grid = [
        [1, 0, 0, 0, 0, 0, 0, 2],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 4, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 0, 0, 0, 0, 0, 0, 6],
    ]
    pair = GridPair(input=[[0] * 8 for _ in range(8)], output=grid)

    objects = pair.to_continuous_coordinates(**plane_8x8, grid="output")

    assert len(objects) == 6
    assert pytest.approx(objects[0].x) == 0.00   # row 0
    assert pytest.approx(objects[0].y) == 0.00   # col 0
    assert pytest.approx(objects[1].x) == 0.00   # row 0
    assert pytest.approx(objects[1].y) == 0.70   # col 7
    assert pytest.approx(objects[2].x) == 0.20   # row 2
    assert pytest.approx(objects[2].y) == 0.20   # col 2
    assert pytest.approx(objects[3].x) == 0.50   # row 5
    assert pytest.approx(objects[3].y) == 0.50   # col 5
    assert pytest.approx(objects[4].x) == 0.70   # row 7
    assert pytest.approx(objects[4].y) == 0.00   # col 0
    assert pytest.approx(objects[5].x) == 0.70   # row 7
    assert pytest.approx(objects[5].y) == 0.70   # col 7

    reconstructed = GridPair.from_continuous_coordinates(
        objects=objects,
        grid_size=(8, 8),
        **plane_8x8,
        grid="output",
    )
    assert reconstructed.output == grid


def test_from_continuous_coordinates_raises_for_invalid_grid_selector() -> None:
    pair = GridPair(input=[[5]], output=[[0]])
    objects = pair.to_continuous_coordinates(
        min_x=0, min_y=0, max_x=1, max_y=1, object_size=(1, 1), min_separation=0
    )

    with pytest.raises(ValueError, match="grid must be either"):
        GridPair.from_continuous_coordinates(
            objects=objects,
            grid_size=(1, 1),
            min_x=0, min_y=0, max_x=1, max_y=1, object_size=(1, 1), min_separation=0,
            grid="foo",
        )
