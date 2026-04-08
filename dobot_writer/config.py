"""
dobot_writer.config
~~~~~~~~~~~~~~~~~~~
All tunable parameters for the Dobot Writer, bundled in one dataclass
so users can override only what they need.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class WritingConfig:
    """
    Parameters controlling writing geometry and motion speed.

    All dimensions are in millimetres (mm) and all velocities/
    accelerations are in the units accepted by pydobotplus.

    Example
    -------
    >>> cfg = WritingConfig(char_height_mm=15, write_vel=100)
    """

    # ── Geometry ──────────────────────────────────────────────────────────────
    char_height_mm: float = 20.0
    """Stroke height of a single character cell (mm)."""

    char_width_mm: float = 14.0
    """Horizontal width of a single character cell (mm)."""

    char_gap_mm: float = 4.0
    """Extra gap inserted between adjacent characters (mm)."""

    word_gap_mm: float = 12.0
    """Extra gap inserted for a space character (mm)."""

    line_spacing_mm: float = 32.0
    """Vertical distance between baselines when '\\n' is used (mm)."""

    lift_mm: float = 5.0
    """How far the pen lifts during travel moves (mm)."""

    z_step_mm: float = 0.5
    """Step size used during the interactive auto-Z calibration (mm)."""

    z_safety_margin_mm: float = 40.0
    """
    Maximum distance the pen will descend below the recorded start-Z
    during auto-Z calibration before aborting (mm).
    """

    # ── Motion speeds ─────────────────────────────────────────────────────────
    write_vel: int = 150
    """Pen-down (writing) velocity."""

    write_acc: int = 150
    """Pen-down (writing) acceleration."""

    travel_vel: int = 500
    """Pen-up (travel) velocity."""

    travel_acc: int = 500
    """Pen-up (travel) acceleration."""

    z_cal_vel: int = 80
    """Velocity used during auto-Z calibration descent."""

    z_cal_acc: int = 80
    """Acceleration used during auto-Z calibration descent."""

    # ── Stencil-font specific ─────────────────────────────────────────────────
    stencil_offset: float = 0.065
    """
    Half-gap for stencil/outline fonts, expressed in *font units* [0–1].
    The rendered gap between the two parallel strokes will be
    ``2 × stencil_offset × char_height_mm`` millimetres.
    Default 0.065 → ~2.6 mm gap on a 20 mm character.
    """
