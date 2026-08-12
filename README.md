# Dota Analyse Pipeline

Dieses Projekt erstellt Analyse-Material aus einem Dota-2-Match.

## Ziel

Während eines Matches werden Screenshots erstellt. Die Ingame-Uhrzeit wird per OCR ausgelesen. Nach dem Match wird die Replay-Demo geparsed. Danach werden relevante Spielsituationen ausgewählt und als PDF plus strukturierte Daten im Output-Ordner bereitgestellt.

## Grober Ablauf

1. Screenshots aufnehmen
2. Ingame-Uhrzeit per OCR erkennen
3. Screenshot-Zeitachse speichern
4. Demo-Datei nach Replay-Download parsen
5. Spielsituationen aus Demo-Daten erkennen
6. passende Screenshots auswählen
7. Analyse-PDF erzeugen
8. Output-Ordner für manuelle LLM-Analyse bereitstellen

## Hinweis

Große Dateien wie Screenshots, Demos und PDFs werden nicht in Git gespeichert.
