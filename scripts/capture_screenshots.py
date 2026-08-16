#!/usr/bin/env python3
"""
Screenshot-Aufnahme für Dota 2 - Wayland & X11 kompatibel.

Funktioniert sowohl auf X11 als auch auf Wayland:
- wmctrl: Fenster-Suche (funktioniert auf beiden)
- PIL ImageGrab: Nimmt Bildschirmbereich auf

Benötigt:
    sudo pacman -S --needed wmctrl xdotool
    pip install Pillow
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageGrab
from scripts.utils.logging_config import get_logger

logger = get_logger(__name__)


class ScreenshotCapture:
    """Nimmt Screenshots eines Fensters oder des gesamten Bildschirms auf."""

    def __init__(
        self,
        output_dir: str = "screenshots",
        interval: float = 2.0,
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        window_name: Optional[str] = None,
        use_fullscreen: bool = False,
    ):
        self.output_dir = Path(output_dir)
        self.interval = max(0.1, interval)
        self.quality = max(1, min(95, quality))
        self.max_width = max_width
        self.max_height = max_height
        self.window_name = window_name
        self.use_fullscreen = use_fullscreen
        self.window_bounds: Optional[tuple] = None
        self.session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Screenshot-Verzeichnis: {self.output_dir.absolute()}")
        logger.info(f"Session-Typ: {self.session_type}")

        if not self.use_fullscreen:
            if not self.window_name:
                raise ValueError(
                    "Im Fenstermodus muss --window-name angegeben werden."
                )

            self._check_window_dependencies()
            self._find_window()
            if self.window_bounds:
                logger.info(
                    f"Zielfenster gefunden: '{self.window_name}' "
                    f"bei {self.window_bounds}"
                )
            else:
                raise RuntimeError(
                    f"Fenster '{self.window_name}' konnte nicht lokalisiert werden."
                )
        else:
            logger.info("Expliziter Fullscreen-Modus aktiviert")

    def _check_window_dependencies(self) -> None:
        """Prüft die Programme für die Fenster-Suche."""
        if shutil.which("wmctrl") is None:
            raise RuntimeError(
                "wmctrl wurde nicht gefunden. Installation:\n"
                "sudo pacman -S --needed wmctrl"
            )

        logger.debug("wmctrl ist verfügbar")

    def _find_window_wmctrl(self) -> Optional[tuple]:
        """
        Sucht Fenster mit wmctrl (funktioniert auf X11 und Wayland).
        
        Gibt (x, y, x2, y2) als bbox zurück.
        """
        try:
            result = subprocess.run(
                ["wmctrl", "-l", "-G"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                logger.debug("wmctrl -l -G fehlgeschlagen")
                return None

            logger.debug(f"wmctrl Output:\n{result.stdout}")

            for line in result.stdout.split("\n"):
                if not line.strip():
                    continue
                if self.window_name not in line:
                    continue

                logger.debug(f"Matching line: {repr(line)}")
                
                # Format: ID DESK X Y W H HOSTNAME NAME
                # Beispiel: "0x02600013  0 308 184 1920 1200 pwnk Dota 2"
                parts = line.split()
                if len(parts) < 6:
                    continue

                try:
                    x = int(parts[2])
                    y = int(parts[3])
                    w = int(parts[4])
                    h = int(parts[5])
                    
                    bbox = (x, y, x + w, y + h)
                    logger.debug(
                        f"Fenster gefunden (wmctrl): Position=({x},{y}), "
                        f"Größe=({w}x{h}), bbox={bbox}"
                    )
                    return bbox

                except (ValueError, IndexError) as e:
                    logger.debug(f"Fehler beim Parsen: {e}")
                    continue

            logger.debug(f"Fenster '{self.window_name}' nicht in wmctrl output gefunden")
            return None

        except Exception as e:
            logger.debug(f"wmctrl Fehler: {e}")
            return None

    def _find_window(self) -> None:
        """Sucht das Fenster und speichert die Bounds."""
        # Versuche wmctrl (funktioniert auf Wayland und X11)
        self.window_bounds = self._find_window_wmctrl()
        
        if self.window_bounds:
            return
        
        # Falls wmctrl nicht funktioniert, vollständiger Fehler
        logger.error(
            f"Fenster '{self.window_name}' konnte nicht gefunden werden.\n"
            f"Session-Typ: {self.session_type}\n"
            f"Tipps:\n"
            f"  - Stelle sicher dass Dota 2 läuft\n"
            f"  - Versuche mit --fullscreen als Workaround\n"
            f"  - Prüfe: wmctrl -l (sollte Dota 2 zeigen)"
        )
        raise RuntimeError(
            f"Fenster '{self.window_name}' nicht gefunden. "
            "Siehe logs für Details."
        )

    def _update_window_bounds(self) -> None:
        """Aktualisiere Fenster-Bounds (Position kann sich ändern)."""
        if not self.window_name:
            return

        new_bounds = self._find_window_wmctrl()
        
        if new_bounds:
            if new_bounds != self.window_bounds:
                logger.debug(
                    f"Fenster-Position aktualisiert: "
                    f"{self.window_bounds} -> {new_bounds}"
                )
            self.window_bounds = new_bounds
        else:
            logger.warning("Fenster konnte nicht mehr lokalisiert werden")

    def _prepare_image(self, image: Image.Image) -> Image.Image:
        """Konvertiert und skaliert das Bild bei Bedarf."""
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (0, 0, 0))
            background.paste(image, mask=image.getchannel("A"))
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        if self.max_width or self.max_height:
            width, height = image.size
            maximum_width = self.max_width or width
            maximum_height = self.max_height or height

            if width > maximum_width or height > maximum_height:
                image.thumbnail(
                    (maximum_width, maximum_height),
                    Image.Resampling.LANCZOS,
                )
                logger.debug(f"Bild skaliert auf: {image.size}")

        return image

    def capture_screenshot(self) -> Optional[Path]:
        """Nimmt einen Screenshot auf und speichert ihn als JPEG."""
        try:
            # Aktualisiere Position vor jedem Screenshot
            if not self.use_fullscreen and self.window_name:
                self._update_window_bounds()

            # Nimm Screenshot auf
            if self.use_fullscreen or not self.window_bounds:
                screenshot = ImageGrab.grab()
                logger.debug(f"Fullscreen-Screenshot: {screenshot.size}")
            else:
                logger.debug(f"Fenster-bbox: {self.window_bounds}")
                screenshot = ImageGrab.grab(bbox=self.window_bounds)
                logger.debug(
                    f"Fenster-Screenshot: {screenshot.size} "
                    f"bei {self.window_bounds}"
                )

            screenshot = self._prepare_image(screenshot)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filepath = (
                self.output_dir / f"screenshot_{timestamp}.jpg"
            )

            screenshot.save(
                filepath,
                format="JPEG",
                quality=self.quality,
                optimize=False,
            )

            return filepath

        except Exception as error:
            logger.error(
                f"Fehler bei Screenshot-Aufnahme: {error}",
                exc_info=True,
            )
            return None

    def capture_continuous(
        self,
        duration: Optional[float] = None,
        max_screenshots: Optional[int] = None,
    ) -> int:
        """Nimmt in regelmäßigen Abständen Screenshots auf."""
        count = 0
        start_time = time.monotonic()
        next_capture = start_time

        logger.info(
            f"Starte Aufnahme: Intervall={self.interval}s, "
            f"Dauer={duration}s, Maximum={max_screenshots}"
        )

        try:
            while True:
                current_time = time.monotonic()

                if (
                    duration is not None
                    and current_time - start_time >= duration
                ):
                    logger.info("Dauer-Limit erreicht")
                    break

                if (
                    max_screenshots is not None
                    and count >= max_screenshots
                ):
                    logger.info("Screenshot-Limit erreicht")
                    break

                remaining = next_capture - current_time

                if remaining > 0:
                    time.sleep(remaining)

                filepath = self.capture_screenshot()

                if filepath is not None:
                    count += 1
                    elapsed = time.monotonic() - start_time
                    logger.info(
                        f"[{count}] Screenshot nach {elapsed:.1f}s: "
                        f"{filepath.name}"
                    )

                next_capture += self.interval
                current_time = time.monotonic()

                if next_capture < current_time:
                    next_capture = current_time

        except KeyboardInterrupt:
            logger.info("Aufnahme durch Benutzer beendet")

        elapsed = time.monotonic() - start_time
        logger.info(
            f"Aufnahme beendet: {count} Screenshots in {elapsed:.1f}s"
        )

        return count


def main() -> int:
    """Programmeinstieg."""
    parser = argparse.ArgumentParser(
        description="Nimmt Screenshots des Dota-2-Fensters auf (X11/Wayland)"
    )

    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--quality", type=int, default=85)
    parser.add_argument("--max-width", type=int, default=None)
    parser.add_argument("--max-height", type=int, default=None)
    parser.add_argument("--window-name", type=str, default="Dota 2")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--output-dir", default="screenshots")

    args = parser.parse_args()

    try:
        capture = ScreenshotCapture(
            output_dir=args.output_dir,
            interval=args.interval,
            quality=args.quality,
            max_width=args.max_width,
            max_height=args.max_height,
            window_name=args.window_name,
            use_fullscreen=args.fullscreen,
        )

        count = capture.capture_continuous(
            duration=args.duration,
            max_screenshots=args.count,
        )

        return 0 if count > 0 else 1

    except Exception as error:
        logger.error(f"Kritischer Fehler: {error}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
