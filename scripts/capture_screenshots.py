#!/usr/bin/env python3
"""
Screenshot-Aufnahme Modul

Nimmt regelmäßig Screenshots während eines Dota-Matches auf.
Speichert diese mit Zeitstempel im screenshots/ Verzeichnis.

Anforderungen:
- PIL/Pillow für Screenshot-Verarbeitung
- xdotool (Linux) für Fenster-Targeting
- Konfigurierbare Aufnahmeparameter (Intervall, Dauer, Qualität)

Unterstützte Modi:
1. Vollscreen - Screenshot des gesamten Displays
2. Fenster-Targeting - Nur das Dota 2 Fenster erfassen (empfohlen)

Verwendung:
    # Dota 2 Fenster (Cashy OS / Linux)
    python3 scripts/capture_screenshots.py --interval 2 --window-name "Dota 2"
    
    # Alternativ: Vollscreen
    python3 scripts/capture_screenshots.py --interval 2 --fullscreen
"""

import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Füge parent directory zu Path hinzu für Imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PIL import ImageGrab, Image
except ImportError:
    ImageGrab = None
    Image = None

from scripts.utils.logging_config import get_logger


logger = get_logger(__name__)


class ScreenshotCapture:
    """Verwaltet die Screenshot-Aufnahme mit Unterstützung für Fenster-Targeting."""
    
    def __init__(
        self,
        output_dir: str = 'screenshots',
        interval: float = 2.0,
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        window_name: Optional[str] = None,
        use_fullscreen: bool = False
    ):
        """
        Initialisiere ScreenshotCapture.
        
        Args:
            output_dir: Verzeichnis für Screenshot-Speicherung
            interval: Aufnahmeintervall in Sekunden
            quality: JPEG-Qualität (1-95)
            max_width: Maximale Breite (None = keine Skalierung)
            max_height: Maximale Höhe (None = keine Skalierung)
            window_name: Fenster-Name zum Targeting (z.B. "Dota 2")
            use_fullscreen: Verwende Fullscreen-Modus (ignoriert window_name)
        """
        self.output_dir = Path(output_dir)
        self.interval = interval
        self.quality = max(1, min(95, quality))  # Begrenze auf 1-95
        self.max_width = max_width
        self.max_height = max_height
        self.window_name = window_name
        self.use_fullscreen = use_fullscreen
        self.window_id = None
        self.window_bounds = None
        
        # Erstelle Output-Verzeichnis
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Screenshot-Verzeichnis: {self.output_dir.absolute()}")
        
        # Prüfe PIL-Verfügbarkeit
        if ImageGrab is None:
            logger.error(
                "PIL/Pillow nicht installiert. "
                "Bitte installiere: pip install Pillow"
            )
            raise ImportError("PIL/Pillow ist erforderlich")
        
        # Konfiguriere Aufnahme-Modus
        if not self.use_fullscreen and self.window_name:
            self._setup_window_targeting()
        else:
            logger.info("Verwende Fullscreen-Modus")
    
    def _setup_window_targeting(self) -> None:
        """Suche und konfiguriere das Ziel-Fenster."""
        try:
            # Versuche xdotool zu verwenden (Linux/Cashy OS)
            result = subprocess.run(
                ['xdotool', 'search', '--name', self.window_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.window_id = result.stdout.strip().split('\n')[0]
                logger.info(f"Fenster gefunden: '{self.window_name}' (ID: {self.window_id})")
                self._update_window_bounds()
            else:
                logger.warning(
                    f"Fenster '{self.window_name}' nicht gefunden. "
                    "Verwende Fullscreen-Modus."
                )
                self.use_fullscreen = True
                
        except FileNotFoundError:
            logger.warning(
                "xdotool nicht verfügbar. "
                "Unter Cashy OS/Linux: sudo apt install xdotool"
            )
            self.use_fullscreen = True
        except Exception as e:
            logger.warning(f"Fenster-Targeting fehlgeschlagen: {e}. Verwende Fullscreen.")
            self.use_fullscreen = True
    
    def _update_window_bounds(self) -> None:
        """Aktualisiere die Fenster-Grenzen."""
        if not self.window_id:
            return
        
        try:
            # Hole Fenster-Geometrie mit xdotool
            result = subprocess.run(
                ['xdotool', 'getwindowgeometry', self.window_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse output: "Position: x,y (screen x), Size: WxH"
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Position:' in line:
                        # Extract x, y
                        pos_part = line.split('Position:')[1].split('(')[0].strip()
                        x, y = map(int, pos_part.split(','))
                    elif 'Geometry:' in line:
                        # Alternative format
                        geom_part = line.split('Geometry:')[1].strip()
                        parts = geom_part.split('+')
                        if len(parts) >= 3:
                            width, height = map(int, parts[0].split('x'))
                            x, y = int(parts[1]), int(parts[2])
                    elif 'Size:' in line:
                        # Extract width, height
                        size_part = line.split('Size:')[1].strip()
                        width, height = map(int, size_part.split('x'))
                
                # Versuche alternativ wmctrl
                if not self.window_bounds:
                    result = subprocess.run(
                        ['wmctrl', '-l', '-G'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if self.window_name in line:
                                parts = line.split()
                                if len(parts) >= 5:
                                    x, y = int(parts[2]), int(parts[3])
                                    width, height = int(parts[4]), int(parts[5])
                                    self.window_bounds = (x, y, x + width, y + height)
                                    logger.info(
                                        f"Fenster-Grenzen: "
                                        f"Position ({x}, {y}), Size ({width}x{height})"
                                    )
                                    return
                
                if not self.window_bounds:
                    self.window_bounds = (x, y, x + width, y + height)
                    logger.info(
                        f"Fenster-Grenzen: "
                        f"Position ({x}, {y}), Size ({width}x{height})"
                    )
                
        except Exception as e:
            logger.warning(f"Fenster-Grenzen konnten nicht bestimmt werden: {e}")
            self.window_bounds = None
    
    def capture_screenshot(self) -> Optional[Path]:
        """
        Nimmt einen Screenshot auf.
        
        Returns:
            Path zur gespeicherten Datei oder None bei Fehler
        """
        try:
            # Nimm Screenshot auf (Fenster oder Fullscreen)
            if self.use_fullscreen or not self.window_bounds:
                screenshot = ImageGrab.grab()
                logger.debug(f"Fullscreen-Screenshot aufgenommen: {screenshot.size}")
            else:
                # Fenster-basierter Screenshot
                screenshot = ImageGrab.grab(bbox=self.window_bounds)
                logger.debug(
                    f"Fenster-Screenshot aufgenommen: "
                    f"{screenshot.size} bei {self.window_bounds}"
                )
            
            # Skaliere falls nötig
            if self.max_width or self.max_height:
                screenshot = self._resize_image(screenshot)
            
            # Erstelle Filename mit Timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # ms genau
            filename = f"screenshot_{timestamp}.jpg"
            filepath = self.output_dir / filename
            
            # Speichere Screenshot
            screenshot.save(str(filepath), quality=self.quality, optimize=False)
            logger.debug(f"Screenshot gespeichert: {filename}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Fehler beim Screenshot-Aufnahme: {e}", exc_info=True)
            return None
    
    def _resize_image(self, image):
        """
        Skaliere Bild wenn Grenzen gesetzt sind.
        
        Args:
            image: PIL Image
            
        Returns:
            Skaliertes PIL Image
        """
        width, height = image.size
        
        # Berechne neue Größe bei Überschreitung
        new_width = self.max_width or width
        new_height = self.max_height or height
        
        if width > new_width or height > new_height:
            # Behalte Aspect Ratio
            image.thumbnail((new_width, new_height))
            logger.debug(f"Bild skaliert auf: {image.size}")
        
        return image
    
    def capture_continuous(
        self,
        duration: Optional[float] = None,
        max_screenshots: Optional[int] = None
    ) -> int:
        """
        Nimmt kontinuierlich Screenshots auf.
        
        Args:
            duration: Gesamtdauer in Sekunden (None = unbegrenzt)
            max_screenshots: Max. Anzahl Screenshots (None = unbegrenzt)
            
        Returns:
            Anzahl erfolgreich gespeicherter Screenshots
        """
        count = 0
        start_time = time.time()
        
        logger.info(
            f"Starte Screenshot-Aufnahme: "
            f"Intervall={self.interval}s, "
            f"Dauer={duration}s, "
            f"Max={max_screenshots}"
        )
        
        try:
            while True:
                # Prüfe Dauer-Limit
                if duration and (time.time() - start_time) >= duration:
                    logger.info("Dauer-Limit erreicht")
                    break
                
                # Prüfe Screenshot-Limit
                if max_screenshots and count >= max_screenshots:
                    logger.info(f"Screenshot-Limit erreicht: {max_screenshots}")
                    break
                
                # Nimm Screenshot auf
                filepath = self.capture_screenshot()
                if filepath:
                    count += 1
                    elapsed = time.time() - start_time
                    logger.info(
                        f"[{count}] Screenshot nach {elapsed:.1f}s: {filepath.name}"
                    )
                
                # Warte bis zur nächsten Aufnahme
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            logger.info("Screenshot-Aufnahme durch Benutzer unterbrochen")
        except Exception as e:
            logger.error(f"Fehler während Screenshot-Aufnahme: {e}", exc_info=True)
        
        elapsed = time.time() - start_time
        logger.info(
            f"Screenshot-Aufnahme beendet: "
            f"{count} Screenshots in {elapsed:.1f}s"
        )
        
        return count


def main():
    """Haupteinstiegspunkt."""
    parser = argparse.ArgumentParser(
        description="Nimmt Screenshots während Dota-Match auf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:

  # Dota 2 Fenster (Cashy OS / Linux) - EMPFOHLEN
  python3 scripts/capture_screenshots.py --count 10 --window-name "Dota 2"
  
  # 10 Screenshots mit 2 Sekunden Abstand (Fullscreen)
  python3 scripts/capture_screenshots.py --count 10 --interval 2 --fullscreen
  
  # 30 Minuten Match-Recording mit Fenster-Targeting
  python3 scripts/capture_screenshots.py --duration 1800 --interval 3 --window-name "Dota 2"
  
  # Mit Skalierung und besserer Qualität
  python3 scripts/capture_screenshots.py --count 50 --quality 90 \\
    --window-name "Dota 2" --max-width 1920 --max-height 1080
        """
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=2.0,
        help='Aufnahmeintervall in Sekunden (default: 2.0)'
    )
    
    parser.add_argument(
        '--duration',
        type=float,
        default=None,
        help='Gesamtdauer in Sekunden (default: unbegrenzt)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=None,
        help='Max. Anzahl Screenshots (default: unbegrenzt)'
    )
    
    parser.add_argument(
        '--quality',
        type=int,
        default=85,
        help='JPEG-Qualität 1-95 (default: 85)'
    )
    
    parser.add_argument(
        '--max-width',
        type=int,
        default=None,
        help='Max. Bildbreite in Pixeln (default: keine Skalierung)'
    )
    
    parser.add_argument(
        '--max-height',
        type=int,
        default=None,
        help='Max. Bildhöhe in Pixeln (default: keine Skalierung)'
    )
    
    parser.add_argument(
        '--window-name',
        type=str,
        default=None,
        help='Fenster-Name für Targeting (z.B. "Dota 2"). Benötigt xdotool.'
    )
    
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='Verwende Fullscreen-Modus (default: Fenster-Targeting falls --window-name gesetzt)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='screenshots',
        help='Output-Verzeichnis (default: screenshots/)'
    )
    
    args = parser.parse_args()
    
    try:
        # Erstelle Capture-Instanz
        capture = ScreenshotCapture(
            output_dir=args.output_dir,
            interval=args.interval,
            quality=args.quality,
            max_width=args.max_width,
            max_height=args.max_height,
            window_name=args.window_name,
            use_fullscreen=args.fullscreen
        )
        
        # Starte kontinuierliche Aufnahme
        count = capture.capture_continuous(
            duration=args.duration,
            max_screenshots=args.count
        )
        
        return 0 if count > 0 else 1
        
    except Exception as e:
        logger.error(f"Kritischer Fehler: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
