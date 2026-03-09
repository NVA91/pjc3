---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: shell-scripting-skill
description: >
  Sichere, strukturierte und wiederholbare Shell-Skripte sowie Arbeit mit
  CSV-Dateien, Excel-Tabellen (.xlsx) und CSS. Keine Dateien oder Pfade werden
  ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

triggers:
  - Shell-Skripte erstellen, prüfen oder überarbeiten
  - Bash- oder Zsh-Automatisierungen entwickeln
  - CSV-Dateien lesen, filtern, transformieren oder schreiben
  - Excel-Tabellen (.xlsx) für Aufgabenverwaltung erstellen oder pflegen
  - CSS-Dateien strukturieren, benennen (BEM) oder stylen
  - Komplexe Inhalte in Tabellen- oder Baumstruktur aufbereiten
  - Expliziter Aufruf via /shell-scripting-skill

resources:
  - resources/shell_template.sh
  - resources/csv_verarbeitung.py
  - resources/excel_aufgaben.py
  - resources/tabellen.css
---

# LADESTUFE 2 — INSTRUKTIONEN
# Wird on-demand geladen, sobald semantische Übereinstimmung mit den Triggern
# erkannt wird (via `cat SKILL.md` im Hintergrund). Moderat: < 5.000 Token.
# Definiert Prozessschritte, Regeln und Leitplanken — kein vollständiger Code.

## Arbeitsweise (Reihenfolge einhalten)

1. **Anforderung klären** — Zieldatei, Pfad und Umfang mit dem Nutzer bestätigen, bevor irgendetwas geschrieben oder ausgeführt wird.
2. **Ressource auswählen** — Passende Ressource aus `resources/` benennen; der Nutzer entscheidet, ob sie ausgeführt wird.
3. **Dry-Run zuerst** — Destruktive oder schreibende Operationen immer zuerst simulieren (`--dry-run`, `echo`-Modus oder Ausgabe nach stdout).
4. **Freigabe einholen** — Vor jeder Dateiänderung: Zielpfad anzeigen, Bestätigung abwarten.
5. **Ausführen & protokollieren** — Ausgabe (stdout/stderr) dem Nutzer vollständig zeigen.

---

## Ladestufe-Übersicht

| Stufe | Komponente | Zeitpunkt | Token-Belastung | Funktionale Bedeutung |
|---|---|---|---|---|
| 1 | Metadaten (YAML-Frontmatter) | Initial beim Session-Start | ~100 Token | Trigger-Mechanismus: Relevanz-Bewertung durch das Modell |
| 2 | Instruktionen (diese Datei) | On-Demand bei semantischer Übereinstimmung | < 5.000 Token | Prozessschritte, Regeln, Leitplanken |
| 3 | Ressourcen (externe Skripte) | Bei explizitem Aufruf während der Ausführung | Nur stdout wird verrechnet | Skripte laufen in Sandbox; Quellcode belastet Kontextfenster nicht |

---

## Sicherheitsregeln — niemals verletzen

- **Kein Dateizugriff ohne Freigabe**: Keine Datei öffnen, lesen oder schreiben ohne explizite Nutzererlaubnis.
- **Keine hardcodierten absoluten Pfade** außer `/tmp` — immer relative Pfade oder konfigurierbare Variablen.
- **Kein `rm -rf` ohne Guard** — immer `confirm()`-Pattern oder `--dry-run` vorschalten.
- **Variablen immer quoten**: `"$var"` statt `$var` (verhindert Wordsplitting und Globbing).
- **`set -euo pipefail` + `IFS=$'\n\t'`** in jedem Bash-Skript als erste ausführbare Zeile.
- **Temp-Files**: Nur via `mktemp` + `trap 'rm -f "$tmp"' EXIT`.

---

## Shell-Skripte — Pflichtstruktur

Jedes generierte Skript muss diese Struktur haben:

```
Shebang          → #!/usr/bin/env bash
Metadaten        → # BESCHREIBUNG / VERWENDUNG / VERSION
Sicherheits-Set  → set -euo pipefail + IFS
Konstanten       → readonly SCRIPT_DIR, SCRIPT_NAME
Hilfsfunktionen  → die(), log(), confirm(), usage()
Argument-Prüfung → [[ $# -lt N ]] && usage
main()           → Hauptlogik, immer als Funktion
Aufruf           → main "$@"
```

Vollständige Vorlage: `resources/shell_template.sh` (Ladestufe 3)

---

## CSV-Verarbeitung — Entscheidungsbaum

```
Ist die CSV-Operation komplex (Joins, Typen, Encoding)?
├── Nein → Shell-Tools: awk, cut, sort, tail (kein Python nötig)
│           Beispiele: Filtern, Spalten extrahieren, sortieren
└── Ja   → Python: csv.DictReader / csv.DictWriter
            Ressource: resources/csv_verarbeitung.py (Ladestufe 3)
```

Shell-Kurzreferenz:

| Operation | Befehl |
|---|---|
| Header überspringen | `tail -n +2 datei.csv` |
| Spalte 2 filtern (`> 100`) | `awk -F',' 'NR>1 && $2>100'` |
| Spalten 1 und 3 | `cut -d',' -f1,3` |
| Sortieren nach Spalte 2 | `sort -t',' -k2,2n` |
| Zeilen zählen | `awk -F',' 'END{print NR-1}'` |

---

## Excel (.xlsx) — Prozess

1. Prüfen: Ist `openpyxl` installiert? (`pip show openpyxl`)
2. Ressource laden: `resources/excel_aufgaben.py` (Ladestufe 3)
3. Ausgabepfad vom Nutzer bestätigen lassen
4. Skript ausführen — stdout zeigt Speicherpfad und Zeilenanzahl

Status-Farbschema (fest definiert, nicht ändern):

| Status | Hex | Verwendung |
|---|---|---|
| Offen | `FFE699` | Gelb — noch nicht begonnen |
| In Arbeit | `9DC3E6` | Blau — aktiv bearbeitet |
| Erledigt | `A9D18E` | Grün — abgeschlossen |
| Blockiert | `FF7C80` | Rot — Blocker vorhanden |

---

## CSS — Regeln

- **Namenskonvention**: BEM (`block__element--modifier`)
- **Keine Inline-Styles** in generierten HTML-Dateien
- **Tabellen-Grundstil** und Status-Badges: `resources/tabellen.css` (Ladestufe 3)
- Vor Änderung an bestehenden CSS-Dateien: Datei lesen und Kontext verstehen

---

## Visuelle Aufbereitung

Für Vergleiche und Entscheidungen: Markdown-Tabelle mit Bewertungsspalte.
Für Projektstrukturen: Baumdarstellung mit `├──` / `└──` und Kommentar-Annotation.
Für Prozesse: Nummerierte Schrittliste mit Entscheidungspunkten.

---

## Verwandte Ressourcen

| Ressource | Ladestufe | Inhalt |
|---|---|---|
| `resources/shell_template.sh` | 3 | Vollständige sichere Bash-Vorlage |
| `resources/csv_verarbeitung.py` | 3 | CSV lesen/schreiben/filtern (Python) |
| `resources/excel_aufgaben.py` | 3 | Excel-Aufgabentabelle mit Farben |
| `resources/tabellen.css` | 3 | Tabellen-Grundstil + Status-Badges |
| `CLAUDE.md` → Docker-Sicherheit | — | Immutable Config, Volume Mounts, UID-Isolation |
| `.claude/skills/n8n-workflow-manager/SKILL.md` | — | MCP vs. REST API Entscheidung |
