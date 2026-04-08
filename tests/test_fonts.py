"""
tests/test_fonts.py
~~~~~~~~~~~~~~~~~~~~
Unit tests for font data and transforms.
Run with:  pytest tests/
"""

import pytest
from dobot_writer.fonts import (
    CLASSIC, CURSIVE, ITALIC, STENCIL, BOLD,
    CURSIVE_ITALIC, STENCIL_CURSIVE,
    list_fonts, get_font, supported_chars,
    make_italic, make_stencil, make_bold, make_mirror,
)


# ── Registry ──────────────────────────────────────────────────────────────────

def test_list_fonts_returns_sorted():
    fonts = list_fonts()
    assert fonts == sorted(fonts)
    assert len(fonts) >= 7


def test_get_font_case_insensitive():
    assert get_font("classic") is CLASSIC
    assert get_font("CURSIVE") is CURSIVE
    assert get_font("Stencil") is STENCIL


def test_get_font_missing_raises():
    with pytest.raises(KeyError):
        get_font("NONEXISTENT_FONT_XYZ")


# ── Font completeness ─────────────────────────────────────────────────────────

ALPHA = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITS = list("0123456789")

@pytest.mark.parametrize("font,name", [
    (CLASSIC, "CLASSIC"),
    (CURSIVE, "CURSIVE"),
])
def test_all_alpha_present(font, name):
    missing = [c for c in ALPHA if c not in font]
    assert not missing, f"{name} is missing letters: {missing}"

@pytest.mark.parametrize("font,name", [
    (CLASSIC, "CLASSIC"),
    (CURSIVE, "CURSIVE"),
])
def test_all_digits_present(font, name):
    missing = [c for c in DIGITS if c not in font]
    assert not missing, f"{name} is missing digits: {missing}"


def test_space_is_empty_list():
    assert CLASSIC[" "] == []
    assert CURSIVE[" "] == []


# ── Glyph coordinate validity ─────────────────────────────────────────────────

def _validate_font_coords(font, name, lo=-0.2, hi=1.3):
    for char, polys in font.items():
        for poly in polys:
            for x, y in poly:
                assert lo <= x <= hi, f"{name}[{char!r}] x={x} out of range [{lo},{hi}]"
                assert lo <= y <= hi, f"{name}[{char!r}] y={y} out of range [{lo},{hi}]"


def test_classic_coords():  _validate_font_coords(CLASSIC, "CLASSIC")
def test_cursive_coords():  _validate_font_coords(CURSIVE, "CURSIVE")


# ── Transforms ────────────────────────────────────────────────────────────────

def test_make_italic_does_not_mutate_source():
    orig_A = [list(pt) for pt in CLASSIC["A"][0]]
    make_italic(CLASSIC)
    assert CLASSIC["A"][0][0] == tuple(orig_A[0])


def test_italic_shifts_top_points():
    italic = make_italic(CLASSIC, slant=0.5)
    for char, polys in italic.items():
        for poly in polys:
            for (ix, iy), (cx, cy) in zip(poly, CLASSIC.get(char, [polys[0]])[0]):
                # Top of glyph (y≈1) should have x shifted by ~slant
                if abs(iy - 1.0) < 0.01:
                    assert abs(ix - (cx + 0.5 * iy)) < 1e-6
                break
        break


def test_stencil_doubles_stroke_count():
    stencil = make_stencil(CLASSIC)
    for char in CLASSIC:
        orig_count = len(CLASSIC[char])
        sten_count = len(stencil[char])
        # Each non-trivial polyline should be doubled
        non_trivial = sum(1 for p in CLASSIC[char] if len(p) >= 2)
        trivial     = orig_count - non_trivial
        assert sten_count == non_trivial * 2 + trivial


def test_bold_triples_stroke_count():
    bold = make_bold(CLASSIC)
    for char in CLASSIC:
        assert len(bold[char]) == len(CLASSIC[char]) * 3


def test_mirror_flips_x():
    mirrored = make_mirror(CLASSIC)
    for char, polys in CLASSIC.items():
        for poly, mpoly in zip(polys, mirrored[char]):
            for (x, y), (mx, my) in zip(poly, mpoly):
                assert abs(mx - (1.0 - x)) < 1e-9
                assert my == y


# ── Stencil offset geometry ───────────────────────────────────────────────────

def test_stencil_offsets_are_symmetric():
    """Left and right offset polylines should be equidistant from centre."""
    import math
    stencil = make_stencil(CLASSIC, offset=0.05)
    # Check a simple two-point stroke: the horizontal '-' dash
    orig_dash  = CLASSIC["-"][0]
    sten_dash  = stencil["-"]
    assert len(sten_dash) == 2
    left_poly, right_poly = sten_dash
    for (lx, ly), (rx, ry), (ox, oy) in zip(left_poly, right_poly, orig_dash):
        dl = math.hypot(lx - ox, ly - oy)
        dr = math.hypot(rx - ox, ry - oy)
        assert abs(dl - 0.05) < 1e-6, f"left offset error: {dl}"
        assert abs(dr - 0.05) < 1e-6, f"right offset error: {dr}"


# ── supported_chars ───────────────────────────────────────────────────────────

def test_supported_chars_excludes_space():
    chars = supported_chars(CLASSIC)
    assert " " not in chars


def test_supported_chars_includes_all_alpha():
    chars = supported_chars(CLASSIC)
    for c in ALPHA:
        assert c in chars, f"Missing {c!r}"
