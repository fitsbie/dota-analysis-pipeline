# 🚀 Dota Pipeline - Cashy OS Schnelleinstieg

## 1️⃣ Setup ausführen

```bash
bash scripts/setup_cashy_os.sh
```

Dieses Skript:
- Erkennt dein Betriebssystem automatisch
- Installiert alle nötigen Tools (xdotool, tesseract, etc.)
- Installiert Python-Abhängigkeiten
- Überprüft die Installation

## 2️⃣ Installation überprüfen

```bash
xdotool --version
python3 -c "import PIL; print('PIL ok')"
```

## 3️⃣ Screenshots aufnehmen

**Test (3 Screenshots):**
```bash
python3 scripts/capture_screenshots.py --count 3 --window-name "Dota 2"
```

**Echtes Match (30 Minuten):**
```bash
python3 scripts/capture_screenshots.py \
  --duration 1800 \
  --interval 2 \
  --quality 90 \
  --window-name "Dota 2"
```

## 📖 Vollständige Dokumentation

Siehe: [docs/CASHY_OS_SETUP.md](docs/CASHY_OS_SETUP.md)

## ❌ Probleme?

1. **"Befehl nicht gefunden"**: Überprüfe `which xdotool`
2. **"Fenster nicht gefunden"**: Teste `xdotool search --name "Dota 2"`
3. **Permissions**: Nutze `--fullscreen` Option als Fallback

Mehr Hilfe: [docs/CASHY_OS_SETUP.md#troubleshooting-für-cashy-os](docs/CASHY_OS_SETUP.md#troubleshooting-für-cashy-os)
