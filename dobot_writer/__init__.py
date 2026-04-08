"""
dobot_writer
~~~~~~~~~~~~
A multi-font text-writing library for the Dobot Magician robotic arm.

Quick start
-----------
>>> from dobot_writer import DobotWriter, WritingConfig
>>> from dobot_writer.fonts import CURSIVE, STENCIL, list_fonts
>>>
>>> print("Available fonts:", list_fonts())
>>>
>>> cfg = WritingConfig(char_height_mm=20, char_width_mm=14)
>>>
>>> with DobotWriter(config=cfg) as writer:
...     writer.setup()                    # interactive teach + Z-cal
...     writer.write("HELLO", font=CURSIVE)

Non-interactive usage (known coordinates):
>>> writer = DobotWriter(port="/dev/ttyUSB0", config=cfg)
>>> writer.connect()
>>> writer.set_origin(x=200.0, y=0.0)
>>> writer.set_z(z_write=-50.0)
>>> writer.write("DOBOT", font=STENCIL)
>>> writer.close()
"""

from .writer import DobotWriter
from .config import WritingConfig
from .fonts import (
    CLASSIC,
    ITALIC,
    STENCIL,
    BOLD,
    CURSIVE,
    CURSIVE_ITALIC,
    STENCIL_CURSIVE,
    list_fonts,
    get_font,
    supported_chars,
    make_italic,
    make_stencil,
    make_bold,
    make_mirror,
)

__version__ = "0.1.0"
__author__  = "Akash Kanagala"
__email__   = "kangalaakash11@gmail.com"
__license__ = "MIT"

__all__ = [
    # Core
    "DobotWriter",
    "WritingConfig",
    # Built-in fonts
    "CLASSIC",
    "ITALIC",
    "STENCIL",
    "BOLD",
    "CURSIVE",
    "CURSIVE_ITALIC",
    "STENCIL_CURSIVE",
    # Font utilities
    "list_fonts",
    "get_font",
    "supported_chars",
    # Transform factories
    "make_italic",
    "make_stencil",
    "make_bold",
    "make_mirror",
]
