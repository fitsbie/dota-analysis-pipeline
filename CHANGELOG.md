# Changelog

## Unreleased

- Projektstruktur initial angelegt.
- README.md erstellt.
- PROJECT_CONTEXT.md erstellt.
- .gitignore erstellt.

## Phase 1 - Basis-Struktur

### Added
- Komplette Ordnerstruktur erstellt:
  - `scripts/` und `scripts/utils/` für Pipeline-Module
  - `config/` für Konfigurationsdateien
  - `inputs/` mit Unterordnern für JSON, Demos, Regelwerke
  - `screenshots/`, `outputs/`, `logs/` für Daten
- `run_pipeline.py` als Haupt-Koordinator mit Logging und Struktur-Vorbereitung
- `scripts/utils/logging_config.py` für zentrale Logging-Konfiguration
- `.gitignore` erweitert für Python und große Dateien

## Phase 2 - Modul 1: Screenshot-Aufnahme (erweitert)

### Added
- `scripts/capture_screenshots.py` - Screenshot-Aufnahme während Match
  - **Fenster-Targeting**: Gezielt nur das Dota 2 Fenster erfassen
  - **Fullscreen-Modus**: Alternative zu Fenster-Targeting
  - **xdotool Integration**: Automatische Fenster-Lokalisierung (Cashy OS/Linux)
  - **Qualitätskontrolle**: JPEG-Qualität und Bildgröße konfigurierbar
  - **Zeitstempel**: Millisekunden-genaue Filenames
  - **Error Handling**: Robuste Fehlerbehandlung und Fallbacks
  
- `scripts/utils/file_utils.py` - Datei-Hilfsfunktionen
  - `ensure_directory()` - Verzeichnis garantieren
  - `get_screenshots()` - Screenshots auflisten (sortiert)
  - `cleanup_old_files()` - Alte Dateien bereinigen

- `docs/CASHY_OS_SETUP.md` - Cashy OS Setup-Guide
  - Voraussetzungen (xdotool, pytesseract)
  - Schritt-für-Schritt Anleitung
  - CLI-Beispiele für verschiedene Szenarien
  - Troubleshooting-Guide
  - Tipps für optimale OCR-Qualität

### Dependencies
- PIL/Pillow installiert und funktionsfähig
- xdotool verfügbar (für Fenster-Targeting auf Linux/Cashy OS)

### Optimierungen für Cashy OS
- Automatische xdotool-Unterstützung mit Fallback auf Fullscreen
- wmctrl als Alternative für Fenster-Geometrie
- Robuste Error-Handling bei fehlenden System-Tools

### Cashy OS Setup
- `scripts/setup_cashy_os.sh` - Automatisches Setup-Skript
  - Erkennt Package Manager automatisch (apt, dnf, yum, pacman, zypper)
  - Installiert alle System-Abhängigkeiten
  - Überprüft Installationen
  
- `SETUP_CASHY_OS_QUICK.md` - Schnelleinstiegs-Guide

- `docs/CASHY_OS_SETUP.md` erweitert
  - Multi-OS Package Manager Support
  - Detailliertes Troubleshooting
  - Cashy OS spezifische Lösungen
