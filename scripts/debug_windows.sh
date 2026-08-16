#!/bin/bash
# Debug: Findet alle offenen Fenster

echo "🔍 Alle offenen Fenster auf deinem System:"
echo "============================================"
echo ""

# Versuch xdotool
if command -v xdotool &> /dev/null; then
    echo "Mit xdotool:"
    xdotool search --name "." | while read wid; do
        xdotool getwindowname "$wid"
    done | head -20
    echo ""
fi

# Versuch wmctrl
if command -v wmctrl &> /dev/null; then
    echo "Mit wmctrl:"
    wmctrl -l
    echo ""
fi

# Spezifische Suche nach Dota
echo "Spezifische Suche nach Dota:"
if command -v xdotool &> /dev/null; then
    xdotool search --name -i "dota\|steam\|game" || echo "Keine Matches"
fi

echo ""
echo "💡 Tipp: Wenn Dota 2 läuft, sollte der Name hier auftauchen."
echo "   Nutze dann: python3 scripts/capture_screenshots.py --window-name \"[NAME]\""
