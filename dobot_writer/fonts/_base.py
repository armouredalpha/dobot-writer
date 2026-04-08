"""
Abstract base class for all dobot-writer fonts.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

# Type aliases
Point    = Tuple[float, float]        # (font_x, font_y)  – both in [0, 1]
Polyline = List[Point]                # one continuous pen-down stroke
Glyph    = List[Polyline]             # a character = one or more strokes


class Font(ABC):
    """
    Base class every dobot-writer font must inherit from.

    Coordinate system (font space)
    ──────────────────────────────
      font_x ∈ [0, 1]   left  →  right   (maps to robot +Y direction)
      font_y ∈ [0, 1]   bottom →  top    (maps to robot +X direction)

    A Glyph is a list of Polylines.  Each Polyline is a list of (x, y) points.
    The pen is lifted automatically between Polylines.

    Returning an *empty list* ( [] ) is valid and means "no strokes" (e.g. a space).
    Returning ``None`` means the character is not supported.
    """

    #: Human-readable name shown in ``list_fonts()``
    name: str = "unnamed"
    #: One-line description
    description: str = ""

    @abstractmethod
    def get_glyph(self, char: str) -> Optional[Glyph]:
        """
        Return the glyph for *char*, or ``None`` if unsupported.

        The caller always passes a single character.  Case handling
        (e.g. mapping lowercase to uppercase data) is the font's responsibility.
        """

    def supported_chars(self) -> frozenset:
        """Return the set of characters this font can render."""
        return frozenset()

    # ── dunder helpers ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<Font '{self.name}'>"

    def __str__(self) -> str:
        return self.name
