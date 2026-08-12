# LLM-Handoff

Diese Datei beschreibt, wie ein LLM an diesem Projekt arbeiten soll.

## Vor jeder Änderung zuerst lesen

1. PROJECT_CONTEXT.md
2. README.md
3. CHANGELOG.md
4. das konkret betroffene Skript

## Regeln für Änderungen

- Keine isolierten Änderungen ohne Blick auf die gesamte Pipeline.
- Immer prüfen, welche Input- und Output-Dateien betroffen sind.
- Keine großen Output-Dateien in Git aufnehmen.
- Bei Änderungen an bestehenden Skripten vollständigen neuen Skript-Code ausgeben.
- Nach wichtigen Änderungen PROJECT_CONTEXT.md und CHANGELOG.md aktualisieren.
- Wenn run_pipeline.py betroffen ist, die gesamte Pipeline-Reihenfolge prüfen.
