"""
dobot_writer.fonts
~~~~~~~~~~~~~~~~~~
Font registry for the Dobot Writer library.

Built-in fonts
--------------
CLASSIC     Clean, geometric single-stroke font  (directly from glyphs)
CURSIVE     Rounded, arc-based flowing font       (directly from glyphs)
ITALIC      Slanted version of CLASSIC            (transform of CLASSIC)
STENCIL     Double-outline / hollow stencil font  (transform of CLASSIC)
BOLD        Heavy multi-pass version of CLASSIC   (transform of CLASSIC)
CURSIVE_ITALIC  Slanted version of CURSIVE        (transform of CURSIVE)
STENCIL_CURSIVE Stencil version of CURSIVE        (transform of CURSIVE)

Usage
-----
>>> from dobot_writer.fonts import CURSIVE, STENCIL, list_fonts
>>> print(list_fonts())
['BOLD', 'CLASSIC', 'CURSIVE', 'CURSIVE_ITALIC', 'ITALIC', 'STENCIL', 'STENCIL_CURSIVE']

You can also create your own font variants:

>>> from dobot_writer.fonts import CLASSIC
>>> from dobot_writer.fonts.transforms import make_stencil, make_italic
>>> MY_FONT = make_italic(make_stencil(CLASSIC), slant=0.35)

Extending with your own font
-----------------------------
A font is just a ``dict[str, list[list[tuple[float, float]]]]``.
Add glyphs and pass the dict to ``DobotWriter.write()``.
"""

from __future__ import annotations
from typing import Dict, List, Optional

from ._classic import CLASSIC
from ._cursive import CURSIVE
from ._transforms import make_italic, make_stencil, make_bold, make_mirror

# ── Derived fonts (computed once at import time) ──────────────────────────────

ITALIC: dict = make_italic(CLASSIC, slant=0.28)
"""CLASSIC font sheared ~15° to the right."""

STENCIL: dict = make_stencil(CLASSIC, offset=0.065)
"""CLASSIC font rendered as double-outline / hollow stencil strokes."""

BOLD: dict = make_bold(CLASSIC, spread=0.04)
"""CLASSIC font with triple-pass lateral overdraw for a heavier look."""

CURSIVE_ITALIC: dict = make_italic(CURSIVE, slant=0.22)
"""CURSIVE font with an additional right-lean shear."""

STENCIL_CURSIVE: dict = make_stencil(CURSIVE, offset=0.06)
"""CURSIVE font rendered as double-outline / hollow stencil strokes."""

# ── Re-export transforms so users can import from one place ──────────────────

from ._transforms import make_italic, make_stencil, make_bold, make_mirror  # noqa: F401, F811

# ── Font registry ─────────────────────────────────────────────────────────────

_REGISTRY: Dict[str, dict] = {
    "CLASSIC":         CLASSIC,
    "ITALIC":          ITALIC,
    "STENCIL":         STENCIL,
    "BOLD":            BOLD,
    "CURSIVE":         CURSIVE,
    "CURSIVE_ITALIC":  CURSIVE_ITALIC,
    "STENCIL_CURSIVE": STENCIL_CURSIVE,
}


def list_fonts() -> List[str]:
    """Return a sorted list of all built-in font names."""
    return sorted(_REGISTRY.keys())


def get_font(name: str) -> dict:
    """
    Retrieve a built-in font by name (case-insensitive).

    Parameters
    ----------
    name :
        One of the names returned by :func:`list_fonts`.

    Raises
    ------
    KeyError
        If the font name is not found in the registry.
    """
    key = name.upper()
    if key not in _REGISTRY:
        available = ", ".join(list_fonts())
        raise KeyError(
            f"Font '{name}' not found.  Available fonts: {available}"
        )
    return _REGISTRY[key]


def supported_chars(font: Optional[dict] = None) -> str:
    """
    Return a string of all characters supported by *font*.
    Defaults to CLASSIC if no font is supplied.
    """
    f = font if font is not None else CLASSIC
    return "".join(sorted(k for k in f if k != " "))


__all__ = [
    "CLASSIC",
    "ITALIC",
    "STENCIL",
    "BOLD",
    "CURSIVE",
    "CURSIVE_ITALIC",
    "STENCIL_CURSIVE",
    "list_fonts",
    "get_font",
    "supported_chars",
    "make_italic",
    "make_stencil",
    "make_bold",
    "make_mirror",
]
