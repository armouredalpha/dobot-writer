"""
examples/custom_font.py
~~~~~~~~~~~~~~~~~~~~~~~~
Demonstrates creating your own font variant using the transform helpers,
and writing with the non-interactive API (if you already know the
robot's coordinates).

Change the coordinates below to match your setup before running.
"""

from dobot_writer import DobotWriter, WritingConfig
from dobot_writer.fonts import CLASSIC, CURSIVE
from dobot_writer.fonts import make_stencil, make_italic, make_bold

# ── Build a custom font: italic BOLD ──────────────────────────────────────────
BOLD_ITALIC = make_italic(make_bold(CLASSIC, spread=0.05), slant=0.3)

# ── Build a stencil-cursive with a wider gap ──────────────────────────────────
WIDE_STENCIL = make_stencil(CURSIVE, offset=0.10)

# ── Non-interactive usage (known coordinates) ─────────────────────────────────
KNOWN_X      = 200.0   # mm  — change to your robot's start X
KNOWN_Y      = 0.0     # mm  — change to your robot's start Y
KNOWN_Z_PEN  = -50.0   # mm  — change to your pen-contact Z

cfg = WritingConfig(char_height_mm=22, write_vel=120)

writer = DobotWriter(port="COM3", config=cfg)  # change port
writer.connect()
writer.set_origin(x=KNOWN_X, y=KNOWN_Y)
writer.set_z(z_write=KNOWN_Z_PEN)

try:
    print("Writing BOLD ITALIC …")
    writer.write("BOLD ITALIC", font=BOLD_ITALIC)

    print("Writing WIDE STENCIL …")
    writer.write("STENCIL", font=WIDE_STENCIL, start_x_offset=-35)

    # Estimate width before committing
    est = writer.estimate_width("HELLO WORLD")
    print(f"\nEstimated width of 'HELLO WORLD': {est:.1f} mm")

finally:
    writer.close()
