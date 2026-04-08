"""
dobot_writer.fonts._transforms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Programmatic font transformations that can be applied to *any* base font
to produce new visual styles without redefining every glyph.

Available transforms
--------------------
make_stencil(font)  →  double-outline / stencil font
make_italic(font)   →  right-leaning shear transform
make_bold(font)     →  multi-pass thickening

All transforms return a new font dict; the original is not modified.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple

Polyline = List[Tuple[float, float]]
GlyphData = List[Polyline]
FontDict = Dict[str, GlyphData]


# ─────────────────────────────────────────────────────────────────────────────
#  STENCIL  —  double-outline / stencil / hollow font
# ─────────────────────────────────────────────────────────────────────────────

def _normal_at(poly: Polyline, i: int) -> Tuple[float, float]:
    """
    Return the unit normal vector at vertex *i* of *poly*.
    Uses the average tangent across the two adjacent segments.
    """
    n = len(poly)
    if n < 2:
        return (0.0, 1.0)

    if n == 2 or i == 0:
        dx = poly[1][0] - poly[0][0]
        dy = poly[1][1] - poly[0][1]
    elif i == n - 1:
        dx = poly[-1][0] - poly[-2][0]
        dy = poly[-1][1] - poly[-2][1]
    else:
        # Average of previous and next tangent directions
        dx = poly[i + 1][0] - poly[i - 1][0]
        dy = poly[i + 1][1] - poly[i - 1][1]

    length = math.hypot(dx, dy)
    if length < 1e-9:
        return (0.0, 1.0)

    # Rotate 90° CCW to get normal
    return (-dy / length, dx / length)


def _offset_polyline(poly: Polyline, d: float) -> Polyline:
    """Shift every vertex of *poly* by distance *d* along its normal."""
    result: Polyline = []
    for i, (x, y) in enumerate(poly):
        nx, ny = _normal_at(poly, i)
        result.append((x + nx * d, y + ny * d))
    return result


def make_stencil(font: FontDict, offset: float = 0.065) -> FontDict:
    """
    Transform *font* into a stencil / double-outline style.

    Each stroke is rendered as **two parallel lines** separated by a gap
    of ``2 × offset`` font-units.  The space between the lines is left
    blank, producing the hollow, stencil-cut look.

    Parameters
    ----------
    font :
        Any ``FontDict`` (CLASSIC, CURSIVE, …).
    offset :
        Half-gap in font coordinates [0–1].  At the default 0.065 and
        a 20 mm character height the outer edges are ~1.3 mm from the
        stroke centre on each side (2.6 mm total hollow width).

    Returns
    -------
    FontDict
        New font where every polyline is replaced by two offset copies.
    """
    result: FontDict = {}
    for char, polylines in font.items():
        new_polys: GlyphData = []
        for poly in polylines:
            if len(poly) < 2:
                new_polys.append(poly)
                continue
            new_polys.append(_offset_polyline(poly, +offset))
            new_polys.append(_offset_polyline(poly, -offset))
        result[char] = new_polys
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  ITALIC  —  right-leaning shear
# ─────────────────────────────────────────────────────────────────────────────

def make_italic(font: FontDict, slant: float = 0.28) -> FontDict:
    """
    Shear every glyph in *font* to lean to the right.

    The transform applied per-point is:
        x' = x + slant × y,   y' = y

    A slant of 0.28 corresponds to roughly 15 ° of inclination.

    Parameters
    ----------
    font :
        Any ``FontDict``.
    slant :
        Shear coefficient.  Positive = lean right, negative = lean left.

    Returns
    -------
    FontDict
        New font with all x-coordinates sheared.
    """
    result: FontDict = {}
    for char, polylines in font.items():
        result[char] = [
            [(x + slant * y, y) for x, y in poly]
            for poly in polylines
        ]
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  BOLD  —  multi-pass thickening
# ─────────────────────────────────────────────────────────────────────────────

def make_bold(font: FontDict, spread: float = 0.04) -> FontDict:
    """
    Produce a heavier-looking font by tripling each stroke with tiny
    lateral offsets so the arm overdraws slightly to the left and right.

    Parameters
    ----------
    font :
        Any ``FontDict``.
    spread :
        Lateral offset for the two extra passes in font units.
        Default 0.04 → ~0.8 mm at 20 mm char height.

    Returns
    -------
    FontDict
        New font with three copies of each stroke (centre, left, right).
    """
    result: FontDict = {}
    for char, polylines in font.items():
        new_polys: GlyphData = []
        for poly in polylines:
            new_polys.append(poly)                                    # centre
            new_polys.append(_offset_polyline(poly, +spread))        # left
            new_polys.append(_offset_polyline(poly, -spread))        # right
        result[char] = new_polys
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  MIRROR  —  horizontal flip (for fun / mirrored writing)
# ─────────────────────────────────────────────────────────────────────────────

def make_mirror(font: FontDict) -> FontDict:
    """
    Horizontally mirror every glyph (x → 1 − x).

    Useful if the robot is writing from right to left, or just for a
    quirky "mirror text" effect.
    """
    result: FontDict = {}
    for char, polylines in font.items():
        result[char] = [
            [(1.0 - x, y) for x, y in poly]
            for poly in polylines
        ]
    return result
