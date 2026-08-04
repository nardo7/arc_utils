"""Canonical ARC colour definitions.

The official ARC visualization palette is specified as sRGB hexadecimal
colours. Isaac Lab's preview-surface material expects linear RGB values in the
``[0.0, 1.0]`` range, so the palette is converted between both representations
when this module is loaded.
"""

from enum import Enum


class Colors(Enum):
    BLUE = "blue"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    GREY = "grey"
    FUCHSIA = "fuchsia"
    ORANGE = "orange"
    TEAL = "teal"
    BROWN = "brown"


ARC_COLOR_TO_COLOR = {
    1: Colors.BLUE,
    2: Colors.RED,
    3: Colors.GREEN,
    4: Colors.YELLOW,
    5: Colors.GREY,
    6: Colors.FUCHSIA,
    7: Colors.ORANGE,
    8: Colors.TEAL,
    9: Colors.BROWN,
}
"""Mapping from ARC's integer colour IDs to their canonical colours."""

COLOR_TO_ARC_COLOR = {v: k for k, v in ARC_COLOR_TO_COLOR.items()}
"""Mapping from ARC's integer colour IDs to their canonical colours."""


def _srgb_channel_to_linear(channel: int) -> float:
    """Convert one 8-bit sRGB channel to a linear RGB value."""
    srgb = channel / 255.0
    if srgb <= 0.04045:
        return srgb / 12.92
    return ((srgb + 0.055) / 1.055) ** 2.4


def _srgb_hex_to_linear_rgb(hex_color: str) -> tuple[float, float, float]:
    """Convert an sRGB hex colour to a linear RGB triple."""
    hex_color = hex_color.removeprefix("#")
    if len(hex_color) != 6:
        raise ValueError(f"Expected a six-digit hex colour, got {hex_color!r}")

    channels = (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
    return tuple(_srgb_channel_to_linear(channel) for channel in channels)


COLOR_RGB = {
    Colors.BLUE: _srgb_hex_to_linear_rgb("#0074D9"),
    Colors.RED: _srgb_hex_to_linear_rgb("#FF4136"),
    Colors.GREEN: _srgb_hex_to_linear_rgb("#2ECC40"),
    Colors.YELLOW: _srgb_hex_to_linear_rgb("#FFDC00"),
    Colors.GREY: _srgb_hex_to_linear_rgb("#AAAAAA"),
    Colors.FUCHSIA: _srgb_hex_to_linear_rgb("#F012BE"),
    Colors.ORANGE: _srgb_hex_to_linear_rgb("#FF851B"),
    Colors.TEAL: _srgb_hex_to_linear_rgb("#7FDBFF"),
    Colors.BROWN: _srgb_hex_to_linear_rgb("#870C25"),
}
"""Canonical ARC palette as linear RGB triples."""


DEFAULT_COLORS = [Colors.RED, Colors.BLUE, Colors.GREEN, Colors.YELLOW]
"""Default movable-cube colours retained for the embodied ARC environment."""
