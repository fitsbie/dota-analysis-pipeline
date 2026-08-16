#!/bin/bash
# Debug: Aktiviert Dota 2 Fenster und zeigt Details

echo "🔍 Suche Dota 2 Fenster..."
echo "================================"
echo ""

# Finde Dota 2 Fenster mit wmctrl
WINDOW_INFO=$(wmctrl -l | grep -i "dota")

if [ -z "$WINDOW_INFO" ]; then
    echo "❌ Dota 2 Fenster nicht gefunden!"
    echo ""
    echo "Alle Fenster:"
    wmctrl -l
    exit 1
fi

echo "✅ Fenster gefunden:"
echo "$WINDOW_INFO"
echo ""

# Extrahiere Window ID (erste Spalte)
WINDOW_ID=$(echo "$WINDOW_INFO" | awk '{print $1}')
echo "Window ID: $WINDOW_ID"

# Extrahiere Fenster-Name (alles nach dem Hostname)
WINDOW_NAME=$(echo "$WINDOW_INFO" | awk '{$1=$2=$3=$4=$5=$6=""; print $0}' | sed 's/^ //')
echo "Fenster-Name: '$WINDOW_NAME'"
echo ""

# Aktiviere das Fenster (in den Vordergrund bringen)
echo "🔼 Bringe Fenster in den Vordergrund..."
wmctrl -i -a "$WINDOW_ID"
sleep 1

echo ""
echo "✅ Fenster ist jetzt aktiv!"
echo ""
echo "💡 Nutze jetzt mit diesem Namen:"
echo "   python3 scripts/capture_screenshots.py --count 3 --window-name \"$WINDOW_NAME\""
echo ""
echo "Oder versuche Screenshot gleich:"
echo "   python3 scripts/capture_screenshots.py --count 3 --window-name \"$(echo "$WINDOW_NAME" | tr -d ' ' | head -c 10)\""
