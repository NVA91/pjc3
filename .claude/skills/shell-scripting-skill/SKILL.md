---
# LADESTUFE 1 — METADATEN (~100 Token)

name: shell-scripting-skill
description: >
  This skill should be used when the user asks to "build an ETL pipeline", "process CSV files",
  "create an Excel financial model", "analyze an image or document", "generate a diagram
  or flowchart", "write a bash or zsh script", "extract invoice data from scan",
  "normalize CSV data", "create a Mermaid/PlantUML/D2 diagram", or "automate with shell".
  Covers: ETL/data pipelines (Polars/Pandas), Excel modeling (.xlsx), Vision document analysis,
  declarative diagrams, and secure Bash/Zsh automation.
  No files or paths are opened or modified without explicit user approval.
version: "2.0"
categories:
  - name: Office-Arbeit
    description: ETL-Pipelines, Data Warehousing, Excel-Finanzmodellierung
  - name: Vision
    description: Bildbeschreibung, Dokumentenextraktion, OCR-ähnliche Analyse
  - name: Visualisierung
    description: Mermaid, PlantUML, D2, Graphviz-Diagramme
  - name: Shell-Scripting
    description: Sichere, wiederholbare Bash/Zsh-Automatisierungen
  - name: Datenformate
    description: CSV, Excel (.xlsx), CSS

resources:
  - resources/csv_etl_pipeline.py
  - resources/excel_finanzmodell.py
  - resources/vision_dokument.py
  - resources/diagramm_generator.py
  - resources/shell_template.sh
  - resources/csv_verarbeitung.py
  - resources/excel_aufgaben.py
  - resources/tabellen.css
---

# LADESTUFE 2 — INSTRUKTIONEN

Office-Automatisierung agiert als deterministische Ausführungsmaschine: Rohdatenströme
werden in reproduzierbare, strukturierte und visuell aufbereitete Formate überführt.
Unterstützt werden ETL-Prozesse, Excel-Finanzmodelle mit Formelinjektion, Vision-basierte
Dokumentenanalyse, deklarative Diagramme und sichere Shell-Automatisierungen.

## Arbeitsweise (Reihenfolge einhalten)

1. **Anforderung klären** — Zieldatei, Pfad und Umfang mit dem Nutzer bestätigen, bevor irgendetwas geschrieben oder ausgeführt wird.
2. **Ressource auswählen** — Passende Ressource aus `resources/` benennen; Nutzer entscheidet über Ausführung.
3. **Dry-Run zuerst** — Destruktive oder schreibende Operationen immer simulieren (`--dry-run`, `echo`-Modus oder Ausgabe nach stdout).
4. **Freigabe einholen** — Vor jeder Dateiänderung: Zielpfad anzeigen, Bestätigung abwarten.
5. **Ausführen & protokollieren** — Ausgabe (stdout/stderr) dem Nutzer vollständig zeigen.

---

## Kategorien und Ressourcen

| Kategorie | Aufgabe | Ressource |
|-----------|---------|-----------|
| **ETL/CSV vollständig** | Discovery → Schema → Bereinigung → Transform | `resources/csv_etl_pipeline.py` |
| **CSV einfach** | Lesen, filtern, schreiben (Stdlib) | `resources/csv_verarbeitung.py` |
| **Excel Finanzmodell** | 3-Statement, SaaS-Metriken, Szenario-Analyse, Formelinjektion | `resources/excel_finanzmodell.py` |
| **Excel Aufgaben** | Aufgabentabelle mit Status-Farben | `resources/excel_aufgaben.py` |
| **Vision** | Rechnung/Diagramm/Screenshot/Batch → JSON oder Markdown | `resources/vision_dokument.py` |
| **Diagramm** | Mermaid/PlantUML/D2/Graphviz-Code + optionales Rendering | `resources/diagramm_generator.py` |
| **Shell** | Sichere Bash/Zsh-Vorlage mit allen Pflichtbestandteilen | `resources/shell_template.sh` |
| **CSS/Tabellen** | Tabellen-Grundstil, Status-Badges (BEM) | `resources/tabellen.css` |

**Entscheidungsregel CSV:**
Einfache Einzel-Operation → Shell-Tools (`awk`, `cut`, `sort`) — kein Python nötig.
Mehrstufiger ETL-Prozess → `csv_etl_pipeline.py` (Polars bevorzugt, > 100k Zeilen).
Einfache Python-Operation → `csv_verarbeitung.py` (Stdlib).

**Kerngrundsatz Excel — Formelinjektion statt Hardcoded Values:**
```
FALSCH → Zelle B12 = 142857          (statisch, verliert Abhängigkeiten)
RICHTIG → Zelle B12 = "=B5*B8*(1+B11)"  (dynamisch, Analyst kann Annahmen ändern)
```

---

## Sicherheitsregeln — niemals verletzen

- **Kein Dateizugriff ohne Freigabe** — keine Datei öffnen, lesen oder schreiben ohne explizite Nutzererlaubnis.
- **Keine hardcodierten absoluten Pfade** außer `/tmp` — immer relative Pfade oder konfigurierbare Variablen.
- **Kein `rm -rf` ohne Guard** — immer `--dry-run` oder `confirm()`-Pattern vorschalten.
- **Variablen immer quoten**: `"$var"` statt `$var` (verhindert Wordsplitting und Globbing).
- **`set -euo pipefail` + `IFS=$'\n\t'`** in jedem Bash-Skript als erste ausführbare Zeile.
- **Temp-Files**: Nur via `mktemp` + `trap 'rm -f "$tmp"' EXIT`.

---

## Ladestufe-Übersicht

| Stufe | Komponente | Zeitpunkt | Token-Belastung |
|-------|------------|-----------|-----------------|
| 1 | YAML-Frontmatter | Session-Start | ~100 Token |
| 2 | Diese Datei | Bei semantischer Übereinstimmung | < 1.500 Token |
| 3 | `resources/` Skripte | Expliziter Aufruf | Nur stdout verrechnet |

---

## Weitere Informationen (references/)

Detaillierte Anweisungen, Schemas, Entscheidungsbäume und Workflows:

- **`references/01-etl-pipeline.md`** — ETL-Phasen, Polars vs. Pandas-Tabelle, Data Warehousing, Übergabe-Protokoll, CSV Shell-Tools
- **`references/02-excel-finanzmodell.md`** — Farbkonventionen, Finanzmodell-Ablauf, Debugging-Protokoll (#REF!/#VALUE!/Zirkelbezüge), Status-Farbschema
- **`references/03-vision-analyse.md`** — Anwendungsfälle, JSON-Schemas (Rechnung/Diagramm), Batch-Verarbeitung, Prompt-Engineering, Graphlit-Integration
- **`references/04-diagramme.md`** — Tool-Auswahl nach Diagramm-Typ, Rendering-Pipeline, Rendering-Voraussetzungen, Pflicht-Ablauf
- **`references/05-shell-und-css.md`** — Shell-Skript-Pflichtstruktur, CSS BEM-Konventionen, Visuelle Aufbereitung
