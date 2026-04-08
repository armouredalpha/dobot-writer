# 🤖 dobot-writer

> A multi-font text-writing library for the **Dobot Magician** robotic arm.

Write text on paper with your Dobot Magician using a choice of built-in fonts — from clean geometric strokes to flowing cursive, hollow stencil outlines, and heavy bold — all without any external font library.

---

## ✨ Features

| Font | Style | Description |
|---|---|---|
| `CLASSIC` | Single-stroke | Clean, geometric — one stroke per segment |
| `CURSIVE` | Single-stroke | Rounded, arc-based, flowing letterforms |
| `ITALIC` | Single-stroke | CLASSIC sheared ~15° to the right |
| `STENCIL` | **Double-line** | Two parallel strokes with a hollow gap — stencil/outline look |
| `BOLD` | Multi-pass | Triple overdraw for a heavier, thicker appearance |
| `CURSIVE_ITALIC` | Single-stroke | CURSIVE with additional right-lean shear |
| `STENCIL_CURSIVE` | **Double-line** | CURSIVE rendered as hollow stencil outlines |

You can also **combine any transforms** to create your own font on the fly:

```python
from dobot_writer.fonts import CLASSIC, make_stencil, make_italic
MY_FONT = make_italic(make_stencil(CLASSIC), slant=0.35)
```

---

## 📦 Installation

### From PyPI *(once published)*
```bash
pip install dobot-writer
```

### From source *(for development / this repo)*
```bash
git clone https://github.com/armouredalpha/dobot-writer.git
cd dobot-writer
pip install -e ".[dev]"
```

**Requirements:** Python ≥ 3.8 · `pydobotplus` · `pyserial`

---

## 🚀 Quick Start

### Interactive mode (guided setup)

```python
from dobot_writer import DobotWriter, WritingConfig
from dobot_writer.fonts import CURSIVE

cfg = WritingConfig(
    char_height_mm=20,   # letter height in mm
    char_width_mm=14,    # letter width in mm
    write_vel=150,       # mm/s pen-down speed
)

with DobotWriter(config=cfg) as writer:
    writer.setup()                        # ① pick port  ② teach origin  ③ auto-Z
    writer.write("HELLO WORLD", font=CURSIVE)
```

Running `writer.setup()` walks you through three interactive steps:

1. **Port selection** — lists available COM/USB ports; you pick one.
2. **Teach mode** — jog the arm to the top-left corner of your writing area, press ENTER.
3. **Auto-Z calibration** — the arm steps down by `z_step_mm` until you type `stop` when the pen just touches the paper.

### Non-interactive mode (known coordinates)

If you already know the robot's Cartesian coordinates for your writing area:

```python
from dobot_writer import DobotWriter, WritingConfig
from dobot_writer.fonts import STENCIL

writer = DobotWriter(port="COM3", config=WritingConfig())
writer.connect()
writer.set_origin(x=200.0, y=0.0)   # pen tip start position (mm)
writer.set_z(z_write=-50.0)          # pen-contact Z (mm)

writer.write("DOBOT", font=STENCIL)
writer.close()
```

---

## 🎨 All Fonts Demo

```python
from dobot_writer import DobotWriter, WritingConfig
from dobot_writer.fonts import list_fonts, get_font

cfg = WritingConfig(char_height_mm=18, line_spacing_mm=30)

with DobotWriter(config=cfg) as writer:
    writer.setup()
    for i, name in enumerate(list_fonts()):
        writer.write(
            f"{name}",
            font=get_font(name),
            start_x_offset=-(i * cfg.line_spacing_mm),
        )
```

---

## 🛠️ API Reference

### `DobotWriter`

```python
DobotWriter(port=None, config=None, verbose=True)
```

| Method | Description |
|---|---|
| `connect()` | Open serial connection |
| `close()` | Close serial connection |
| `setup()` | Interactive port → teach → auto-Z calibration |
| `set_origin(x, y)` | Set writing origin programmatically (mm) |
| `set_z(z_write, lift_mm=None)` | Set pen-contact Z programmatically (mm) |
| `write(text, font=None, ...)` | Write text on paper |
| `estimate_width(text)` | Estimate writing width in mm |
| `get_pose()` | Return current arm pose |
| `list_ports()` | Static — list available serial ports |

### `WritingConfig`

All fields have sensible defaults. Override only what you need:

```python
WritingConfig(
    char_height_mm  = 20.0,   # letter height (mm)
    char_width_mm   = 14.0,   # letter width  (mm)
    char_gap_mm     = 4.0,    # gap between characters
    word_gap_mm     = 12.0,   # gap for a space character
    line_spacing_mm = 32.0,   # baseline-to-baseline for \n
    lift_mm         = 5.0,    # pen lift height during travel
    z_step_mm       = 0.5,    # auto-Z step size
    write_vel       = 150,    # pen-down speed
    travel_vel      = 500,    # pen-up speed
    stencil_offset  = 0.065,  # half-gap for stencil fonts [0–1]
)
```

### Font Utilities

```python
from dobot_writer.fonts import list_fonts, get_font, supported_chars

list_fonts()              # ['BOLD', 'CLASSIC', 'CURSIVE', ...]
get_font("stencil")       # returns the STENCIL font dict
supported_chars(CLASSIC)  # '!"#%&\'()*+,-./0123456789:;?@ABCDE...'
```

### Transform Factories

```python
from dobot_writer.fonts import make_italic, make_stencil, make_bold, make_mirror

make_italic(font, slant=0.28)    # right-lean shear (~15°)
make_stencil(font, offset=0.065) # double-outline / hollow
make_bold(font, spread=0.04)     # triple-pass thickening
make_mirror(font)                # horizontal flip
```

---

## 🔤 Writing Coordinate System

```
Robot arm base
│
│  start_x (X axis, −X = new lines)
│  ◄──────────────────────────
│  [H]  [E]  [L]  [L]  [O]     ← each cell is char_width_mm wide
│  ───────────────────────────► start_y (Y axis, writing direction)
│
│  Font coords inside each cell:
│    x: 0.0 (left) → 1.0 (right)   maps to robot +Y
│    y: 0.0 (bottom) → 1.0 (top)   maps to robot +X
```

- Text advances in the **+Y** direction.
- New lines step in the **−X** direction.
- The pen lifts to `z_travel = z_write + lift_mm` between strokes.

---

## ✏️ Creating Your Own Font

A font is a plain Python `dict[str, list[list[tuple[float, float]]]]`:

```python
MY_FONT = {
    'A': [
        [(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)],   # two legs
        [(0.2, 0.4), (0.8, 0.4)],                 # crossbar  ← separate polyline = pen lift
    ],
    'B': [ ... ],
    ' ': [],   # space — just advance the cursor
}

writer.write("AAB", font=MY_FONT)
```

Rules:
- `x` and `y` are in **[0, 1]** (font units).  Values just outside [0,1] are fine for descenders/serifs.
- Each item in the outer list is one **polyline** (continuous pen stroke).  The pen lifts between polylines.
- The pen always lifts after the last polyline in a glyph.
- Lowercase chars are automatically looked up as uppercase.

---

## 🖥️ Supported Characters (CLASSIC / CURSIVE)

```
! " # % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7 8 9
: ; ? @ A B C D E F G H I J K L M N O P Q R S T
U V W X Y Z [ \ ] _
```

---

## 🧪 Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## 📁 Project Structure

```
dobot-writer/
├── dobot_writer/
│   ├── __init__.py         ← public API
│   ├── writer.py           ← DobotWriter class
│   ├── config.py           ← WritingConfig dataclass
│   └── fonts/
│       ├── __init__.py     ← font registry, list_fonts(), get_font()
│       ├── _classic.py     ← CLASSIC font data
│       ├── _cursive.py     ← CURSIVE font data + _make_italic helper
│       └── _transforms.py  ← make_stencil, make_italic, make_bold, make_mirror
├── examples/
│   ├── hello_world.py
│   ├── multi_font.py
│   └── custom_font.py
├── tests/
│   └── test_fonts.py
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Contributions are very welcome! Ideas for contribution:

- Add new glyphs or improve existing ones (PR to `_classic.py` or `_cursive.py`)
- Add a new base font (e.g. `_block.py`, `_retro.py`)
- Add a new transform (e.g. `make_wavy`, `make_condensed`)
- Improve auto-Z calibration (e.g. force-sensor support)
- Add a dry-run / preview mode that plots the strokes without the robot

**To contribute:**

1. Fork the repo and create a branch: `git checkout -b feat/my-font`
2. Make your changes and add tests in `tests/`
3. Run `pytest tests/ -v` and make sure everything passes
4. Open a Pull Request with a description of what you changed

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 🙏 Acknowledgements

Built on top of [pydobotplus](https://github.com/AlexGLiu/pydobotplus) for Dobot Magician serial communication.

Font design inspired by single-stroke Hershey fonts used in CNC and pen-plotter communities.
