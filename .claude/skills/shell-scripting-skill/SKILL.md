---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: shell-scripting-skill
description: >
  Sichere, strukturierte und wiederholbare Shell-Skripte sowie Office-Automatisierung:
  ETL-Pipelines (CSV/Polars/Pandas), Excel-Tabellen (.xlsx), CSS und visuelle
  Aufbereitung. Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe
  geöffnet oder verändert.

categories:
  - name: Office-Arbeit
    description: Datenadministration, ETL-Pipelines, Analyse und Visualisierung
  - name: Shell-Scripting
    description: Sichere, wiederholbare Bash/Zsh-Automatisierungen
  - name: Datenformate
    description: CSV, Excel (.xlsx), CSS

triggers:
  # Office-Arbeit / ETL
  - ETL-Pipeline aufbauen oder automatisieren (Extract, Transform, Load)
  - CSV-Dateien scannen, bereinigen, normalisieren oder konsolidieren
  - Polars oder Pandas für Datentransformation einsetzen
  - Schema einer CSV-Datei inspizieren oder Datentypen prüfen
  - Daten deduplizieren oder Datumsformate normalisieren
  - Mehrere CSV-Dateien zusammenführen (concat/merge)
  - SQL-ähnliche Abfragen auf flachen Dateien ausführen
  - Daten-Einlagerung in strukturierte Formate automatisieren
  # Shell-Scripting
  - Shell-Skripte erstellen, prüfen oder überarbeiten
  - Bash- oder Zsh-Automatisierungen entwickeln
  # Weitere Datenformate
  - Excel-Tabellen (.xlsx) für Aufgabenverwaltung erstellen oder pflegen
  - CSS-Dateien strukturieren, benennen (BEM) oder stylen
  - Komplexe Inhalte in Tabellen- oder Baumstruktur aufbereiten
  - Expliziter Aufruf via /shell-scripting-skill

resources:
  - resources/csv_etl_pipeline.py
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

## Hauptkategorie 1: Office-Arbeit — Datenadministration, Analyse und Visualisierung

KI-gestützte Office-Automatisierung agiert als deterministische Ausführungsmaschine:
Rohdatenströme werden in reproduzierbare, strukturierte und visuell aufbereitete Formate überführt.
Das Modell übernimmt ETL-Prozesse, generiert institutionelle Berichte und erstellt Entscheidungshilfen.

### ETL-Pipeline: Orchestrierungs-Phasen

| Phase | CSV-Verarbeitung | Technologie / MCP-Tool | Resultat |
|---|---|---|---|
| **1. Discovery** | Autonomes Scannen von Verzeichnissen nach neuen Datenexporten | MCP `get_files_list` + Glob-Muster | System findet Rohdaten ohne manuelles Hochladen |
| **2. Schema-Inspektion** | Analyse der internen Dateistruktur vor der Verarbeitung | MCP `get_schema` → `df.schema.items()` | Modell versteht Entitäten, verhindert Datentypfehler |
| **3. Bereinigung & Normalisierung** | Fehlerbehebung, Deduplizierung, Standardisierung | `csv_etl_pipeline.py` → Polars/Pandas | Unicode-Fehler, Datumsformate und Duplikate korrigiert |
| **4. Sichere Transformation** | Aggregation, Filterung, Datei-Zusammenführung | `execute_polars_sql` + `pl.concat` | Konsolidierte Datensätze, einlagerungsbereit |

### Werkzeugwahl — wann MCP, wann Python-Ressource?

```
Aufgabe erfordert Dateisystem-Zugriff (Verzeichnis scannen, Schema lesen)?
├── Ja  → MCP-Tools: get_files_list / get_schema
│          → Ergebnis (stdout) an Python-Ressource weitergeben
└── Nein → Direkt: resources/csv_etl_pipeline.py (Ladestufe 3)
           Modi: entdecken | inspizieren | bereinigen | transformieren | pipeline
```

### Pflicht-Ablauf für jeden ETL-Job

1. **Discovery-Ergebnis zeigen** — Gefundene Dateien dem Nutzer auflisten, bevor Verarbeitung startet.
2. **Schema kommunizieren** — Erkannte Spalten und Datentypen vor Phase 3 bestätigen lassen.
3. **Bereinigungsplan vorlegen** — Welche Korrekturen werden durchgeführt? Erst nach Freigabe ausführen.
4. **Transformations-Output nach stdout** — Niemals direkt in Produktionsdatenbank schreiben ohne Prüfschritt.
5. **Protokoll erzeugen** — Jede Pipeline-Ausführung gibt Statistik aus: Zeilen ein/aus, Fehler, Duplikate.

### Polars vs. Pandas — Entscheidung

| Kriterium | Polars | Pandas |
|---|---|---|
| Datenmenge | > 100.000 Zeilen oder > 50 MB | < 100.000 Zeilen, kleine Dateien |
| SQL-ähnliche Abfragen | `execute_polars_sql` — nativ | Umweg über `query()` |
| Speichereffizienz | Arrow-basiert, deutlich geringer | Höherer Speicherbedarf |
| Ecosystem / Bibliotheken | Wachsend, modern | Sehr breit (sklearn, seaborn...) |
| **Standard** | **Bevorzugen** | Nur bei Ecosystem-Zwang |

Ressource für alle 4 Phasen: `resources/csv_etl_pipeline.py` (Ladestufe 3)

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
Handelt es sich um einen ETL-Prozess (Discovery → Schema → Bereinigung → Transform)?
├── Ja  → resources/csv_etl_pipeline.py  (Polars, alle 4 Phasen, Ladestufe 3)
│          + MCP-Tools für Discovery/Schema wenn Dateisystem-Zugriff nötig
└── Nein → Einfache Operation?
           ├── Nein → resources/csv_verarbeitung.py  (Stdlib, Ladestufe 3)
           └── Ja   → Shell-Tools: awk, cut, sort, tail (kein Python nötig)
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

| Ressource | Ladestufe | Kategorie | Inhalt |
|---|---|---|---|
| `resources/csv_etl_pipeline.py` | 3 | Office-Arbeit | Polars-ETL: Discovery, Schema, Bereinigung, Transformation |
| `resources/csv_verarbeitung.py` | 3 | Datenformate | CSV lesen/schreiben/filtern (Stdlib, einfache Ops) |
| `resources/shell_template.sh` | 3 | Shell-Scripting | Vollständige sichere Bash-Vorlage |
| `resources/excel_aufgaben.py` | 3 | Office-Arbeit | Excel-Aufgabentabelle mit Status-Farben |
| `resources/tabellen.css` | 3 | Datenformate | Tabellen-Grundstil + Status-Badges (BEM) |
| `CLAUDE.md` → Docker-Sicherheit | — | — | Immutable Config, Volume Mounts, UID-Isolation |
| `.claude/skills/n8n-workflow-manager/SKILL.md` | — | — | MCP vs. REST API Entscheidung |
