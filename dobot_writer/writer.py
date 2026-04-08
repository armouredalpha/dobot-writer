"""
dobot_writer.writer
~~~~~~~~~~~~~~~~~~~~
Core ``DobotWriter`` class — the main public interface of the library.

Typical usage
-------------
>>> from dobot_writer import DobotWriter, WritingConfig
>>> from dobot_writer.fonts import CURSIVE, STENCIL
>>>
>>> cfg = WritingConfig(char_height_mm=20, write_vel=120)
>>> with DobotWriter(port="/dev/ttyUSB0", config=cfg) as w:
...     w.setup()                   # interactive teach + Z-cal
...     w.write("HELLO", font=CURSIVE)
...     w.write("WORLD", font=STENCIL, start_y_offset=0)

For non-interactive / automated use see :meth:`DobotWriter.set_origin`
and :meth:`DobotWriter.set_z`.
"""

from __future__ import annotations

import sys
import time
from typing import Optional

from serial.tools import list_ports
from pydobotplus import Dobot

from .config import WritingConfig
from .fonts import CLASSIC


# ─────────────────────────────────────────────────────────────────────────────

class DobotWriter:
    """
    High-level text-writing controller for the Dobot Magician arm.

    Parameters
    ----------
    port :
        Serial port string, e.g. ``"COM3"`` or ``"/dev/ttyUSB0"``.
        If ``None``, the user will be prompted interactively to choose
        from the available ports.
    config :
        A :class:`~dobot_writer.config.WritingConfig` instance.
        Defaults to the library defaults if not provided.
    verbose :
        Print progress messages to stdout when ``True`` (default).
    """

    def __init__(
        self,
        port: Optional[str] = None,
        config: Optional[WritingConfig] = None,
        verbose: bool = True,
    ) -> None:
        self.config   = config or WritingConfig()
        self.verbose  = verbose
        self._device: Optional[Dobot] = None

        # Origin + Z set by setup() or set_origin() / set_z()
        self._start_x: Optional[float] = None
        self._start_y: Optional[float] = None
        self._z_write: Optional[float] = None
        self._z_travel: Optional[float] = None

        # Resolve port
        self._port = port or self._select_port()

    # ── Context manager ───────────────────────────────────────────────────────

    def __enter__(self) -> "DobotWriter":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Open the serial connection to the Dobot Magician."""
        if self._device is not None:
            return
        self._log(f"Connecting to Dobot on {self._port} …")
        self._device = Dobot(port=self._port)
        self._log("Connected ✓")

    def close(self) -> None:
        """Close the serial connection."""
        if self._device is not None:
            try:
                self._device.close()
                self._log("Connection closed.")
            except Exception:
                pass
            self._device = None

    # ── Origin / Z  (programmatic, non-interactive) ───────────────────────────

    def set_origin(self, x: float, y: float) -> None:
        """
        Set the top-left writing origin without going through the
        interactive teach procedure.

        Parameters
        ----------
        x, y :
            Dobot Cartesian coordinates of the pen tip at the desired
            start position (mm).
        """
        self._start_x = x
        self._start_y = y
        self._log(f"Origin set to X={x:.2f}  Y={y:.2f}")

    def set_z(self, z_write: float, lift_mm: Optional[float] = None) -> None:
        """
        Set the Z writing height directly.

        Parameters
        ----------
        z_write :
            Z coordinate at which the pen touches paper (mm).
        lift_mm :
            How far to raise the pen during travels.  Uses
            ``config.lift_mm`` if not provided.
        """
        lift = lift_mm if lift_mm is not None else self.config.lift_mm
        self._z_write  = z_write
        self._z_travel = z_write + lift
        self._log(f"Z-write={z_write:.2f}  Z-travel={self._z_travel:.2f}")

    def get_pose(self):
        """Return the current arm pose (delegates to pydobotplus)."""
        return self._dev().get_pose()

    # ── Interactive setup ────────────────────────────────────────────────────

    def setup(self) -> None:
        """
        Interactive two-step calibration:

        1. **Teach** – physically jog the arm to the top-left corner of
           the writing area and press ENTER to record the origin.
        2. **Auto-Z** – the arm steps down in
           ``config.z_step_mm`` increments until you type ``stop``.

        After :meth:`setup` completes, the writer is ready to call
        :meth:`write`.
        """
        self.connect()
        sx, sy, sz = self._teach_start()
        self.set_origin(sx, sy)
        z_write, z_travel = self._auto_z(sx, sy, sz)
        self._z_write  = z_write
        self._z_travel = z_travel

    # ── Writing ───────────────────────────────────────────────────────────────

    def write(
        self,
        text: str,
        font: Optional[dict] = None,
        start_x_offset: float = 0.0,
        start_y_offset: float = 0.0,
    ) -> None:
        """
        Write *text* on the paper using the current origin and Z levels.

        Parameters
        ----------
        text :
            The string to write.  Supports ``\\n`` for newlines.
            Lowercase is silently converted to uppercase glyph lookups.
        font :
            A font dict.  Any of the built-in fonts from
            :mod:`dobot_writer.fonts` or a custom dict.
            Defaults to :data:`~dobot_writer.fonts.CLASSIC`.
        start_x_offset :
            Shift the writing origin in the X direction (mm).  Positive
            moves the start *further* from the base.
        start_y_offset :
            Shift the writing origin in the Y direction (mm).  Positive
            advances the start to the right.

        Raises
        ------
        RuntimeError
            If :meth:`setup` (or :meth:`set_origin` + :meth:`set_z`)
            has not been called yet.
        """
        self._require_calibration()
        f = font if font is not None else CLASSIC

        ox = self._start_x + start_x_offset  # type: ignore[operator]
        oy = self._start_y + start_y_offset   # type: ignore[operator]

        self._write_text(text, f, ox, oy)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _dev(self) -> Dobot:
        if self._device is None:
            raise RuntimeError(
                "Not connected.  Call connect() or use DobotWriter as a context manager."
            )
        return self._device

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def _require_calibration(self) -> None:
        if self._start_x is None or self._z_write is None:
            raise RuntimeError(
                "Origin / Z not set.  Call setup() or set_origin() + set_z() first."
            )

    # ── teach / auto-Z (interactive) ─────────────────────────────────────────

    @staticmethod
    def _select_port() -> str:
        ports = list_ports.comports()
        if not ports:
            print("ERROR: No serial ports found.  Is the Dobot connected?")
            sys.exit(1)
        print("\nAvailable serial ports:")
        for i, p in enumerate(ports):
            print(f"  [{i}]  {p.device:20s}  {p.description}")
        while True:
            try:
                idx = int(input("\nEnter port number: "))
                return ports[idx].device
            except (ValueError, IndexError):
                print("  Invalid choice, try again.")

    def _teach_start(self):
        cfg = self.config
        print("\n" + "═" * 60)
        print("  STEP 1 — SET START POSITION (TEACH MODE)")
        print("═" * 60)
        print("""
  1. Hold the TEACH button to unlock joints.
  2. Physically guide the pen tip to the TOP-LEFT corner of
     the writing area.
  3. Release the TEACH button.
  4. Press ENTER to record the position.
""")
        device = self._dev()
        while True:
            input("Press ENTER to record position …")
            pose = device.get_pose()
            sx, sy, sz = pose.position.x, pose.position.y, pose.position.z
            p = pose.position
            print(f"\n  Recorded:  X={p.x:.2f}  Y={p.y:.2f}  Z={p.z:.2f}")
            ans = input("  Correct? (y / n / q=quit): ").strip().lower()
            if ans == "y":
                return sx, sy, sz
            if ans == "q":
                self.close()
                sys.exit(0)

    def _auto_z(self, sx: float, sy: float, sz: float):
        cfg = self.config
        print("\n" + "═" * 60)
        print("  STEP 2 — AUTO-Z CALIBRATION")
        print("═" * 60)
        print(f"""
  The arm will move to the start XY and step down {cfg.z_step_mm} mm
  at a time.  Press ENTER to step; type 'stop' when the pen
  just touches the paper; type 'q' to abort.
""")
        device = self._dev()
        safe_z = sz + 30.0
        device.speed(cfg.travel_vel, cfg.travel_acc)
        device.move_to(x=sx, y=sy, z=safe_z)

        current_z = safe_z
        while True:
            current_z -= cfg.z_step_mm
            device.speed(cfg.z_cal_vel, cfg.z_cal_acc)
            device.move_to(z=current_z)

            resp = input(
                f"  Z = {current_z:7.2f} mm  [ENTER=step | stop=use this | q=abort]: "
            ).strip().lower()

            if resp in ("stop", "s"):
                break
            if resp in ("q", "quit"):
                self.close()
                sys.exit(0)
            if current_z < sz - cfg.z_safety_margin_mm:
                print(f"  Safety limit reached.  Using Z = {current_z:.2f}")
                break

        z_write  = current_z
        z_travel = z_write + cfg.lift_mm
        print(f"\n  ✓  Writing Z : {z_write:.2f} mm")
        print(f"  ✓  Travel  Z : {z_travel:.2f} mm")
        device.speed(cfg.travel_vel, cfg.travel_acc)
        device.move_to(z=z_travel)
        return z_write, z_travel

    # ── Low-level drawing ────────────────────────────────────────────────────

    def _draw_polyline(
        self,
        polyline: list,
        origin_x: float,
        origin_y: float,
    ) -> None:
        """
        Draw one continuous pen-down stroke.

        Font coordinate mapping
        -----------------------
        font-x  (0→1, left→right in the cell)   →   robot +Y axis
        font-y  (0→1, bottom→top of the cell)   →   robot +X axis
        """
        if not polyline:
            return
        cfg     = self.config
        device  = self._dev()
        zw      = self._z_write
        zt      = self._z_travel
        H       = cfg.char_height_mm
        W       = cfg.char_width_mm

        fx0, fy0 = polyline[0]
        rx0 = origin_x + fy0 * H
        ry0 = origin_y + fx0 * W

        # Rapid travel to stroke start
        device.speed(cfg.travel_vel, cfg.travel_acc)
        device.move_to(x=rx0, y=ry0, z=zt)

        # Pen down
        device.speed(cfg.write_vel, cfg.write_acc)
        device.move_to(z=zw)

        # Draw stroke
        for fx, fy in polyline[1:]:
            device.move_to(
                x=origin_x + fy * H,
                y=origin_y + fx * W,
            )

        # Pen up
        device.speed(cfg.travel_vel, cfg.travel_acc)
        device.move_to(z=zt)

    def _write_text(
        self,
        text: str,
        font: dict,
        start_x: float,
        start_y: float,
    ) -> None:
        cfg     = self.config
        device  = self._dev()

        # Normalise: replace literal \n sequences the user may have typed
        text = text.replace("\\n", "\n")

        self._log(f"\n  Writing ({len(text)} chars): {text!r}")

        # Lift pen before we start
        device.speed(cfg.travel_vel, cfg.travel_acc)
        device.move_to(z=self._z_travel)

        line_x   = start_x   # decrements for each new line (−X = further from base)
        cursor_y = start_y   # increments for each character (+Y = rightward)
        total    = len(text)

        for idx, char in enumerate(text):
            # ── newline ──────────────────────────────────────────────────────
            if char == "\n":
                cursor_y  = start_y
                line_x   -= cfg.line_spacing_mm
                continue

            # ── space ────────────────────────────────────────────────────────
            if char == " ":
                cursor_y += cfg.char_width_mm + cfg.word_gap_mm
                continue

            # ── look up glyph ────────────────────────────────────────────────
            glyph_key = char.upper() if char.upper() in font else None
            if glyph_key is None:
                self._log(f"    [!] No glyph for {char!r}, skipping.")
                cursor_y += cfg.char_width_mm + cfg.char_gap_mm
                continue

            if self.verbose:
                print(
                    f"    [{idx + 1:>3}/{total}]  {char!r}  "
                    f"X={line_x:.1f}  Y={cursor_y:.1f}",
                    end="\r",
                )

            for poly in font[glyph_key]:
                self._draw_polyline(poly, line_x, cursor_y)

            cursor_y += cfg.char_width_mm + cfg.char_gap_mm

        if self.verbose:
            print()  # finish the \r line
        self._log("  Done ✓")

        # Park at start
        device.speed(cfg.travel_vel, cfg.travel_acc)
        device.move_to(x=start_x, y=start_y, z=self._z_travel)

    # ── Utility ───────────────────────────────────────────────────────────────

    def estimate_width(self, text: str) -> float:
        """
        Estimate the total writing width of *text* in millimetres.

        Parameters
        ----------
        text :
            The string to estimate (newlines are ignored; each line is
            measured independently and the maximum is returned).

        Returns
        -------
        float
            Maximum line width in mm.
        """
        cfg = self.config
        max_w = 0.0
        for line in text.split("\n"):
            w = 0.0
            for ch in line:
                if ch == " ":
                    w += cfg.char_width_mm + cfg.word_gap_mm
                else:
                    w += cfg.char_width_mm + cfg.char_gap_mm
            max_w = max(max_w, w)
        return max_w

    @staticmethod
    def list_ports() -> list:
        """Return a list of available serial port device strings."""
        return [p.device for p in list_ports.comports()]
