#!/usr/bin/env python3
"""
Screenshot-Aufnahme für Dota 2.

Im Fenstermodus wird das echte X11- beziehungsweise XWayland-Fenster
anhand seiner Fenster-ID aufgenommen. Es wird nicht nur ein fester
Bildschirmbereich ausgeschnitten.

Benötigt:
    sudo pacman -S --needed imagemagick xdotool
    pip install Pillow
"""

import argparse
import io
import os
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
    """Nimmt Screenshots eines echten Fensters oder des gesamten Bildschirms auf."""

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
        self.window_id: Optional[str] = None

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Screenshot-Verzeichnis: {self.output_dir.absolute()}")

        if not self.use_fullscreen:
            if not self.window_name:
                raise ValueError(
                    "Im Fenstermodus muss --window-name angegeben werden."
                )

            self._check_window_dependencies()
            self.window_id = self._find_window()
            logger.info(
                f"Zielfenster gefunden: '{self.window_name}', "
                f"Fenster-ID: {self.window_id}"
            )
        else:
            logger.info("Expliziter Fullscreen-Modus aktiviert")

    def _check_window_dependencies(self) -> None:
        """Prüft die Programme für die fensterbezogene Aufnahme."""
        if shutil.which("xdotool") is None:
            raise RuntimeError(
                "xdotool wurde nicht gefunden. Installation:\n"
                "sudo pacman -S --needed xdotool"
            )

        if shutil.which("magick") is None and shutil.which("import") is None:
            raise RuntimeError(
                "ImageMagick wurde nicht gefunden. Installation:\n"
                "sudo pacman -S --needed imagemagick"
            )

    def _run_xdotool(self, *args: str, timeout: float = 5.0) -> str:
        """Führt xdotool aus und gibt dessen Ausgabe zurück."""
        result = subprocess.run(
            ["xdotool", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(
                f"xdotool {' '.join(args)} fehlgeschlagen: {message}"
            )

        return result.stdout.strip()

    def _window_geometry(self, window_id: str) -> tuple:
        """Liest Breite und Höhe eines Fensters aus."""
        output = self._run_xdotool(
            "getwindowgeometry",
            "--shell",
            window_id,
        )

        values = {}
        for line in output.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

        width = int(values.get("WIDTH", "0"))
        height = int(values.get("HEIGHT", "0"))

        return width, height

    def _window_title(self, window_id: str) -> str:
        """Liest den aktuellen Fenstertitel aus."""
        try:
            return self._run_xdotool(
                "getwindowname",
                window_id,
                timeout=2.0,
            )
        except Exception:
            return ""

    def _find_window(self) -> str:
        """
        Sucht sichtbare Fenster anhand des Namens.

        Wenn mehrere Treffer existieren, wird das größte Fenster verwendet.
        Dadurch werden kleine Hilfsfenster möglichst vermieden.
        """
        try:
            output = self._run_xdotool(
                "search",
                "--onlyvisible",
                "--name",
                self.window_name,
            )
        except RuntimeError as error:
            session_type = os.environ.get("XDG_SESSION_TYPE", "unbekannt")
            raise RuntimeError(
                f"Kein sichtbares Fenster mit dem Namen "
                f"'{self.window_name}' gefunden.\n"
                f"Sitzungstyp: {session_type}\n"
                f"Originalfehler: {error}"
            ) from error

        window_ids = [
            line.strip()
            for line in output.splitlines()
            if line.strip().isdigit()
        ]

        if not window_ids:
            raise RuntimeError(
                f"Kein sichtbares Fenster mit dem Namen "
                f"'{self.window_name}' gefunden."
            )

        candidates = []

        for window_id in window_ids:
            try:
                width, height = self._window_geometry(window_id)
                title = self._window_title(window_id)
                area = width * height
                logger.debug(
                    f"Fensterkandidat: ID={window_id}, "
                    f"Titel='{title}', Größe={width}x{height}"
                )

                if width > 0 and height > 0:
                    candidates.append(
                        (area, window_id, width, height, title)
                    )

            except Exception as error:
                logger.debug(
                    f"Fenster-ID {window_id} konnte nicht geprüft werden: "
                    f"{error}"
                )

        if not candidates:
            raise RuntimeError(
                f"Fenster '{self.window_name}' wurde gefunden, "
                "aber seine Größe konnte nicht ermittelt werden."
            )

        candidates.sort(reverse=True)

        _, window_id, width, height, title = candidates[0]

        logger.info(
            f"Verwende Fenster: ID={window_id}, "
            f"Titel='{title}', Größe={width}x{height}"
        )

        return window_id

    def _window_still_exists(self) -> bool:
        """Prüft, ob das gespeicherte Fenster noch vorhanden ist."""
        if not self.window_id:
            return False

        result = subprocess.run(
            ["xdotool", "getwindowname", self.window_id],
            capture_output=True,
            text=True,
            timeout=2,
        )

        return result.returncode == 0

    def _capture_window(self) -> Image.Image:
        """Nimmt das Fenster direkt anhand seiner X11-Fenster-ID auf."""
        if not self._window_still_exists():
            logger.warning("Gespeichertes Fenster existiert nicht mehr. Suche erneut.")
            self.window_id = self._find_window()

        hexadecimal_id = hex(int(self.window_id))

        if shutil.which("magick"):
            command = [
                "magick",
                "import",
                "-silent",
                "-window",
                hexadecimal_id,
                "png:-",
            ]
        else:
            command = [
                "import",
                "-silent",
                "-window",
                hexadecimal_id,
                "png:-",
            ]

        result = subprocess.run(
            command,
            capture_output=True,
            timeout=15,
        )

        if result.returncode != 0:
            error_message = result.stderr.decode(
                "utf-8",
                errors="replace",
            ).strip()
            raise RuntimeError(
                f"Fensteraufnahme fehlgeschlagen. "
                f"Fenster-ID: {hexadecimal_id}. "
                f"ImageMagick: {error_message}"
            )

        if not result.stdout:
            raise RuntimeError(
                "ImageMagick hat keine Bilddaten zurückgegeben."
            )

        with Image.open(io.BytesIO(result.stdout)) as source_image:
            screenshot = source_image.copy()

        logger.debug(
            f"Fenster direkt aufgenommen: "
            f"ID={hexadecimal_id}, Größe={screenshot.size}"
        )

        return screenshot

    def _prepare_image(self, image: Image.Image) -> Image.Image:
        """Konvertiert und skaliert das Bild bei Bedarf."""
        if image.mode == "RGBA":
            background = Image.new(
                "RGB",
                image.size,
                (0, 0, 0),
            )
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
            if self.use_fullscreen:
                screenshot = ImageGrab.grab()
                logger.debug(
                    f"Fullscreen-Screenshot aufgenommen: {screenshot.size}"
                )
            else:
                screenshot = self._capture_window()

            screenshot = self._prepare_image(screenshot)

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )[:-3]

            filepath = (
                self.output_dir /
                f"screenshot_{timestamp}.jpg"
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
                f"Fehler bei der Screenshot-Aufnahme: {error}",
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
            f"Dauer={duration}, Maximum={max_screenshots}"
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
            f"Aufnahme beendet: {count} Screenshots "
            f"in {elapsed:.1f}s"
        )

        return count


def main() -> int:
    """Programmeinstieg."""
    parser = argparse.ArgumentParser(
        description="Nimmt Screenshots des Dota-2-Fensters auf"
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
