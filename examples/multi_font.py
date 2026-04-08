"""
examples/multi_font.py
~~~~~~~~~~~~~~~~~~~~~~~
Write the same phrase in every built-in font, each on its own line.

Run with:
    python examples/multi_font.py
"""

from dobot_writer import DobotWriter, WritingConfig
from dobot_writer.fonts import list_fonts, get_font

PHRASE = "DOBOT"

cfg = WritingConfig(
    char_height_mm=18,
    char_width_mm=12,
    char_gap_mm=3,
    line_spacing_mm=30,
    write_vel=130,
)

with DobotWriter(config=cfg) as writer:
    writer.setup()

    fonts = list_fonts()
    print(f"\n  Will write '{PHRASE}' in {len(fonts)} fonts:")
    for name in fonts:
        print(f"    • {name}")

    go = input("\nStart? (y/n): ").strip().lower()
    if go != "y":
        print("Aborted.")
    else:
        for line_idx, name in enumerate(fonts):
            print(f"\n  [{line_idx + 1}/{len(fonts)}]  Font: {name}")
            font = get_font(name)
            writer.write(
                PHRASE,
                font=font,
                start_x_offset=-(line_idx * cfg.line_spacing_mm),
            )
        print("\nAll done!")
