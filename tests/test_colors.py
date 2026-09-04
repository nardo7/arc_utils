import pytest

from arc_utils import ARC_COLOR_TO_COLOR, COLOR_RGB, Colors, Pixel


def test_arc_palette_converts_official_srgb_values_to_linear_rgb() -> None:
    assert ARC_COLOR_TO_COLOR[1] is Colors.BLUE
    assert COLOR_RGB[Colors.BLUE] == pytest.approx(
        (0.0, 0.174647403656, 0.693871761292)
    )
    assert COLOR_RGB[Colors.FUCHSIA] == pytest.approx(
        (0.871367119199, 0.006048833023, 0.514917665377)
    )
    assert COLOR_RGB[Colors.BROWN] == pytest.approx(
        (0.242281122466, 0.003676507324, 0.018500220128)
    )


def test_pixel_color_name_uses_the_canonical_palette() -> None:
    assert Pixel(color=6, x=0.0, y=0.0, width=1.0, height=1.0).get_color() == "fuchsia"
