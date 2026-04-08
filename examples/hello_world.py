"""
examples/hello_world.py
~~~~~~~~~~~~~~~~~~~~~~~
Minimal example – write "HELLO WORLD" in the default CLASSIC font.
"""

from dobot_writer import DobotWriter, WritingConfig

cfg = WritingConfig(
    char_height_mm=20,
    char_width_mm=14,
    char_gap_mm=4,
    write_vel=150,
    travel_vel=500,
)

with DobotWriter(config=cfg) as writer:
    writer.setup()                          # interactive teach + Z-cal
    writer.write("HELLO WORLD")             # uses CLASSIC font by default
