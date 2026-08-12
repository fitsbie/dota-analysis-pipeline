# Projektkontext: Dota Analyse Pipeline

## Ziel

Dieses Projekt erstellt automatisch Analyse-Material aus einem Dota-2-Match.

## Grundidee

Während des Matches werden regelmäßig Screenshots erstellt. Aus den Screenshots wird per OCR die Ingame-Uhrzeit gelesen. Nach dem Match wird die Demo-Datei geparsed. Danach werden anhand der Demo-Daten relevante Spielsituationen ausgewählt. Die passenden Screenshots werden in eine große PDF überführt.

## Fester Pipeline-Ablauf

1. Screenshots aufnehmen
2. Ingame-Uhrzeit per OCR erkennen
3. Screenshot-Zeitachse als Datei speichern
4. Replay-Download abwarten oder Demo-Datei übernehmen
5. Demo-Datei parsen
6. Spielsituationen anhand der Demo-Daten erkennen
7. passende Screenshots auswählen
8. Analyse-PDF erzeugen
9. Output-Ordner für manuelle LLM-Weiterverarbeitung bereitstellen

## Wichtige Ordner

- scripts/: ausführbare Skripte
- scripts/utils/: Hilfsfunktionen
- config/: Konfigurationsdateien
- inputs/json/: geparste oder vorbereitete Match-JSON-Dateien
- inputs/noobibel/: Noobibel-Dateien oder Regelwerke
- inputs/demos/: lokale Demo-Dateien, nicht in Git
- screenshots/: lokale Screenshots, nicht in Git
- outputs/: fertige Analysepakete, nicht in Git
- logs/: Log-Dateien, nicht in Git
- docs/: Projektdokumentation

## Arbeitsregeln

- Einzelskripte sollen unabhängig testbar bleiben.
- run_pipeline.py steuert später nur die Reihenfolge.
- Große Output-Dateien werden nicht in Git aufgenommen.
- Nach größeren Änderungen PROJECT_CONTEXT.md und CHANGELOG.md aktualisieren.
- Bei Skriptänderungen immer prüfen, ob andere Pipeline-Schritte betroffen sind.
- Änderungen an bestehenden Skripten sollen als kompletter Skript-Code dokumentiert werden.

## Aktueller Stand

Projekt wurde initial lokal angelegt.

## Offene nächste Schritte

- Erste Skriptstruktur erstellen
- Screenshot-Aufnahme definieren
- OCR-Schritt definieren
- Demo-Parsing-Schritt definieren
- Szenenauswahl definieren
- PDF-Erstellung definieren
