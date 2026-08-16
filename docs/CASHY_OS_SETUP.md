# Cashy OS Setup für Dota 2 Analyse Pipeline

Dieses Dokument beschreibt die Konfiguration der Pipeline für Cashy OS mit Dota 2 im Fenstermodus.

## 🚀 Schnelles Setup (automatisch)

```bash
# Automatische Erkennung des Package Managers und Installation
bash scripts/setup_cashy_os.sh
```

Das Skript:
- ✅ Erkennt automatisch deinen Package Manager
- ✅ Installiert xdotool, wmctrl, tesseract
- ✅ Installiert Python-Abhängigkeiten
- ✅ Überprüft alle Installationen

---

## Manuelles Setup

Wenn das automatische Setup nicht funktioniert, hier die manuellen Schritte:

### 1. xdotool installieren (für Fenster-Targeting)

**Versuche eine der folgenden Optionen:**

```bash
# Option A: APT (Debian/Ubuntu-basiert)
sudo apt install xdotool wmctrl

# Option B: DNF/YUM (Fedora/RHEL-basiert)
sudo dnf install xdotool wmctrl

# Option C: Pacman (Arch-basiert)
sudo pacman -S xdotool wmctrl

# Option D: Zypper (openSUSE-basiert)
sudo zypper install xdotool wmctrl

# Option E: Manuelle Installation (fallback)
# Von Quellen-Code compilieren:
git clone https://github.com/jordansissel/xdotool.git
cd xdotool && make && sudo make install
```

**Falls du "Befehl nicht gefunden" bekommst:**
```bash
# Probiere ohne sudo
xdotool --version

# Oder kontrolliere ob es bereits installiert ist
which xdotool
```

### 2. Python-Abhängigkeiten
```bash
pip install Pillow pytesseract
# oder
pip3 install Pillow pytesseract
```

### 3. Tesseract OCR (für Zeitstempel-Erkennung - später)

```bash
# Option A: APT
sudo apt install tesseract-ocr

# Option B: DNF/YUM
sudo dnf install tesseract

# Option C: Pacman
sudo pacman -S tesseract

# Option D: Zypper
sudo zypper install tesseract
```

## Setup für Dota 2 Fenster-Aufnahme

### Schritt 1: Dota 2 im Fenstermodus starten
- Starten Sie Dota 2 via Steam im Fenstermodus
- Fenster sollte "Dota 2" heißen (standard)
- Positionieren Sie das Fenster optimal für die Aufnahme

### Schritt 2: Fenster-Name überprüfen
```bash
xdotool search --name "Dota 2"
```

Falls der Name anders ist, können Sie ihn mit anpassen:
```bash
wmctrl -l
```

### Schritt 3: Screenshots während Match aufnehmen

**Kurzer Test (3 Screenshots):**
```bash
python3 scripts/capture_screenshots.py --count 3 --interval 1 --window-name "Dota 2"
```

**Echtes Match-Recording (30 Minuten, alle 3 Sekunden):**
```bash
python3 scripts/capture_screenshots.py --duration 1800 --interval 3 --window-name "Dota 2"
```

**Mit Qualitäts-Optimierung:**
```bash
python3 scripts/capture_screenshots.py \
  --duration 1800 \
  --interval 2 \
  --quality 90 \
  --window-name "Dota 2" \
  --max-width 1920 \
  --max-height 1080
```

## Tipps für beste Ergebnisse

### OCR-Qualität optimieren
- **Zeitstempel-Position**: UI-Ecke oben links meist gut sichtbar
- **Auflösung**: Höhere Auflösung hilft der OCR (1920x1080 empfohlen)
- **Intervall**: 2-3 Sekunden reicht für Detail-Erfassung

### Speicher sparen
- **Qualität reduzieren**: --quality 75 spart ~25% Speicher
- **Skalierung**: --max-width 1280 für kleinere Dateien
- **Cleanup**: Alte Screenshots mit file_utils.cleanup_old_files() entfernen

### Troubleshooting für Cashy OS

#### Fehler: "Fenster nicht gefunden"
```bash
# Überprüfe ob Dota 2 läuft und den Namen hat
xdotool search --name "Dota 2"

# Wenn das nicht funktioniert, findest du den echten Namen so:
wmctrl -l
# oder
xdotool search --class Steam
```

**Lösungen:**
- Namen in Anführungszeichen: `"Dota 2"` (mit Leerzeichen)
- Anderen Namen verwenden: z.B. `--window-name "Dota"`
- Fallback auf Fullscreen: `--fullscreen` Option verwenden

#### Fehler: "xdotool command not found"
```bash
# Versuche Setup-Skript
bash scripts/setup_cashy_os.sh

# Oder manuelle Installation (je nach Package Manager)
sudo dnf install xdotool      # Fedora/RHEL
sudo pacman -S xdotool        # Arch
sudo zypper install xdotool   # openSUSE
```

#### Fehler: "Berechtigungsproblem" (permission denied)
```bash
# Nutze Vollscreen-Modus (kein sudo nötig)
python3 scripts/capture_screenshots.py --count 5 --fullscreen

# Oder versuche xhost zu konfigurieren
xhost +local:
```

#### Python-Import Fehler
```bash
# Stelle sicher dass Python-Pakete installiert sind
pip3 install Pillow pytesseract

# Oder nutze das Setup-Skript
bash scripts/setup_cashy_os.sh
```

#### Zu viele/wenige Screenshots
- Interval anpassen: `--interval 1` für mehr, `--interval 5` für weniger
- Duration auf echte Match-Länge setzen (ca. 30-50 Minuten)

## Integration in run_pipeline.py

Die capture_screenshots.py wird später in run_pipeline.py integriert:

```python
from scripts.capture_screenshots import ScreenshotCapture

capture = ScreenshotCapture(
    window_name="Dota 2",
    interval=2.0,
    quality=90
)

count = capture.capture_continuous(duration=1800)
```

## Verfügbare Package Manager

Cashy OS kann verschiedene Package Manager nutzen. Das Setup-Skript erkennt automatisch:

| Package Manager | Distribution | Installation |
|---|---|---|
| `apt` | Debian/Ubuntu-basiert | `sudo apt install xdotool` |
| `dnf` | Fedora/RHEL 8+ | `sudo dnf install xdotool` |
| `yum` | RHEL 7 / CentOS | `sudo yum install xdotool` |
| `pacman` | Arch-basiert | `sudo pacman -S xdotool` |
| `zypper` | openSUSE | `sudo zypper install xdotool` |

Falls du unsicher bist welcher verwendet wird:
```bash
# Das Setup-Skript erkennt es automatisch:
bash scripts/setup_cashy_os.sh
```

## Weitere Module

- `ocr_timestamps.py` - Ingame-Uhrzeit aus Screenshots auslesen
- `parse_demo.py` - Demo-Datei parsen
- `select_scenes.py` - Wichtige Szenen auswählen
- `generate_pdf.py` - Analyse-PDF erstellen
