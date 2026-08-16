#!/bin/bash
"""
Cashy OS Setup Helper - Installiert automatisch Abhängigkeiten
Erkennt den Package Manager automatisch
"""

set -e

echo "🔧 Dota Analyse Pipeline - Cashy OS Setup Helper"
echo "=================================================="
echo ""

# Erkenne Package Manager
PM=""
if command -v dnf &> /dev/null; then
    PM="dnf"
    INSTALL_CMD="sudo dnf install -y"
elif command -v yum &> /dev/null; then
    PM="yum"
    INSTALL_CMD="sudo yum install -y"
elif command -v pacman &> /dev/null; then
    PM="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm"
elif command -v zypper &> /dev/null; then
    PM="zypper"
    INSTALL_CMD="sudo zypper install -y"
elif command -v apt &> /dev/null; then
    PM="apt"
    INSTALL_CMD="sudo apt install -y"
else
    echo "❌ Kein bekannter Package Manager gefunden!"
    echo "Unterstützt: apt, dnf, yum, pacman, zypper"
    exit 1
fi

echo "✅ Erkannter Package Manager: $PM"
echo ""

# System Tools
echo "📦 Installiere System-Tools (xdotool, wmctrl)..."
$INSTALL_CMD xdotool wmctrl || {
    echo "⚠️  Warnung: Könnte xdotool/wmctrl nicht installieren"
    echo "   Das ist ggf. kein Problem - Fallback auf Fullscreen ist aktiv"
}

# Tesseract OCR (für später)
echo "📦 Installiere Tesseract OCR (für OCR-Phase)..."
case $PM in
    dnf|yum)
        $INSTALL_CMD tesseract
        ;;
    pacman)
        $INSTALL_CMD tesseract
        ;;
    zypper)
        $INSTALL_CMD tesseract
        ;;
    apt)
        $INSTALL_CMD tesseract-ocr
        ;;
esac || {
    echo "⚠️  Warnung: Tesseract konnte nicht installiert werden"
}

# Python Packages
echo "📦 Installiere Python-Abhängigkeiten..."
pip install -q Pillow pytesseract || pip3 install -q Pillow pytesseract || {
    echo "❌ Fehler: Python-Pakete konnten nicht installiert werden"
    exit 1
}

echo ""
echo "✅ Setup abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "1. Überprüfe Installation:"
echo "   xdotool --version"
echo "   tesseract --version"
echo "   python3 -c 'import PIL; print(PIL.__version__)'"
echo ""
echo "2. Starte Screenshot-Aufnahme:"
echo "   python3 scripts/capture_screenshots.py --help"
echo ""
echo "3. Test mit Dota 2 Fenster:"
echo "   python3 scripts/capture_screenshots.py --count 3 --window-name 'Dota 2'"
