#!/usr/bin/env python3
"""
Dota Analyse Pipeline - Hauptkoordinator

Steuert den Ablauf der gesamten Pipeline:
1. Screenshots aufnehmen
2. Ingame-Uhrzeit per OCR erkennen
3. Screenshot-Zeitachse speichern
4. Demo-Datei parsen
5. Spielsituationen erkennen
6. Passende Screenshots auswählen
7. Analyse-PDF erzeugen
8. Output-Ordner bereitstellen
"""

import sys
import logging
from pathlib import Path
from typing import Optional


# Konfigurieren des Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Stelle sicher, dass alle notwendigen Verzeichnisse existieren."""
    dirs = [
        'scripts',
        'scripts/utils',
        'config',
        'inputs/json',
        'inputs/demos',
        'inputs/noobibel',
        'screenshots',
        'outputs',
        'logs'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Verzeichnis gesichert: {dir_path}")


def main():
    """Haupteinstiegspunkt der Pipeline."""
    logger.info("=" * 60)
    logger.info("Dota Analyse Pipeline gestartet")
    logger.info("=" * 60)
    
    try:
        setup_directories()
        logger.info("Grundstruktur ist bereit für Pipeline-Module")
        
        # TODO: Einzelne Module importieren und ausführen
        # from scripts.capture_screenshots import capture_screenshots
        # from scripts.ocr_timestamps import extract_timestamps
        # from scripts.parse_demo import parse_demo
        # from scripts.select_scenes import select_scenes
        # from scripts.generate_pdf import generate_pdf
        
        logger.info("Pipeline-Koordinator ist aktiv. Module können hinzugefügt werden.")
        return 0
        
    except Exception as e:
        logger.error(f"Fehler in Pipeline: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
