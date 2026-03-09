---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: hybrid-workflow-skill
description: >
  Nahtlose Verkettung von Office- und Programmier-Skills ohne Medienbruch:
  PostgreSQL → CSV → Excel + Sankey → PowerPoint in einer Pipeline,
  asynchrone Parallel-Orchestrierung (Bash &-Operator + wait),
  PowerPoint-Generierung (python-pptx), Command-Chain-Tabelle,
  Datenstrom-Protokoll zwischen Skills (stdout/JSON-Lines/Dateipfad).
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Hybride Workflows / Cross-Domain-Pipelines
    description: >
      Nahtlose Verkettung von Office- und Programmier-Skills ohne Medienbruch:
      PostgreSQL → CSV → Excel + Sankey → PowerPoint in einer Pipeline,
      asynchrone Parallel-Orchestrierung (Bash &-Operator + wait),
      PowerPoint-Generierung (python-pptx), Command-Chain-Tabelle,
      Datenstrom-Protokoll zwischen Skills (stdout/JSON-Lines/Dateipfad)

triggers:
  # Hybride Workflows / Cross-Domain-Pipelines / PowerPoint
  - Office- und Programmier-Skills ohne Medienbruch kombinieren
  - End-to-End-Pipeline PostgreSQL → CSV → Excel + Sankey → PowerPoint aufbauen
  - Quartalsbericht oder Finanzbericht vollautomatisch generieren
  - Asynchrone Skill-Verkettung: parallele und sequenzielle Schritte orchestrieren
  - PowerPoint-Präsentation (.pptx) aus Excel und Diagrammen automatisch erstellen
  - SVG-Diagramm oder Sankey-Chart in PowerPoint-Slide einbetten
  - Excel-Erkenntnisse in präsentationsfertige .pptx überführen
  - Mehrere Skills gleichzeitig ausführen (Bash &-Operator + wait)
  - Datenstrom zwischen Skills (stdout, JSON-Lines, CSV-Dateipfad) definieren
  - Command-Chain-Tabelle für Hybrid-Workflow dokumentieren

resources:
  - resources/pptx_generator.py
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

## Hybride Workflows — Schnittstellen zwischen Office-Arbeit und Programmieren

Die transformative Leistungsfähigkeit dieses Skill-Systems offenbart sich an den
Schnittstellen beider Domänen: Deterministische Programmier-Werkzeuge und analytische
Office-Bedürfnisse verschmelzen über das Skill- und MCP-Framework nahtlos —
ohne Medienbrüche, ohne manuelle Übergaben zwischen Teams.

### Command Chain — Abstraktionsebenen des Systems

| Schicht | Abstraktionsebene | Komponente | Domäne | Funktion |
|---|---|---|---|---|
| **Sichere Ausführungsumgebung** | Infrastructure Layer | Docker Sandbox (node:20-slim) | Programmieren | Isolierte MicroVM; Host-System vor Agenten-Aktionen geschützt |
| **Datenextraktion & Querying** | Extension Layer | MCP-Server (PostgreSQL / SQLite) | Programmieren | Deterministische Rohdaten-Abfrage via API; kein Schema-Leak, kein Credential-Leak |
| **Daten-Einlagerung & Transformation** | Delegation Layer | CSV Data Summarizer / Polars Engine | Office-Arbeit | Bereinigte, deduplizierte, strukturierte CSV-Datenströme |
| **Finanzmodellierung & Analyse** | Core Execution Layer | xlsx-Skill (pandas, openpyxl) | Office-Arbeit | Dynamisches Excel-Workbook mit erhaltenen Formel-Abhängigkeiten |
| **System- und Prozessvisualisierung** | Core Execution Layer | Mermaid.js / PlantUML / Excalidraw | Office-Arbeit | Vektorgrafiken, Flowcharts, Sankey-Diagramme, C4-Architekturen |
| **Präsentation & Reporting** | Core Execution Layer | pptx-Skill (python-pptx) | Office-Arbeit | Präsentationsfertige PowerPoint mit eingebetteten Diagrammen und Excel-Erkenntnissen |
| **Design & UI Implementierung** | Core Execution Layer | Tailwind v4 / shadcn UI Skill | Programmieren | Responsives React-Frontend, WCAG-konform und barrierefrei |

### Referenz-Pipeline: Quartalsbericht — End-to-End ohne Medienbruch

**Szenario:** Finanzanalyst benötigt Quartalsbericht über globale Transaktionen.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SCHRITT 1 — Datenextraktion (Programmieren)                                │
│  Infrastructure: Docker Sandbox (node:20-slim, Non-Root, UID-Passthrough)   │
│                                                                             │
│  MCP-Tool: PostgreSQL                                                       │
│  execute_query("""                                                          │
│    SELECT region, currency, SUM(amount) AS total,                          │
│           COUNT(*) AS tx_count, AVG(amount) AS avg_tx                      │
│    FROM transactions                                                        │
│    WHERE quarter = 'Q1-2026' AND status = 'settled'                        │
│    GROUP BY region, currency                                                │
│    ORDER BY total DESC                                                      │
│    LIMIT 1000                                                               │
│  """)                                                                       │
│  → Result: JSON nach stdout → temporäre CSV im isolierten Container-FS     │
└────────────────────────┬────────────────────────────────────────────────────┘
                         │ CSV-Datei (im Docker-FS, nie auf Host)
┌────────────────────────▼────────────────────────────────────────────────────┐
│  SCHRITT 2 — Bereinigung & Aggregation (Office-Arbeit)                      │
│                                                                             │
│  csv_etl_pipeline.py bereinigen q1_raw.csv                                 │
│  → Duplikate entfernen, Währungen normalisieren, Null-Werte auffüllen       │
│  → Statistik nach stdout: {"ok": 892, "fehler": 3, "duplikate": 11}        │
└────────────────────────┬────────────────────────────────────────────────────┘
                         │ q1_bereinigt.csv
         ┌───────────────┴───────────────┐
         │ (parallel)                    │ (parallel)
┌────────▼───────────────┐  ┌───────────▼────────────────────────────────────┐
│  SCHRITT 3a — Excel    │  │  SCHRITT 3b — Sankey-Diagramm                  │
│  (Office-Arbeit)       │  │  (Office-Arbeit)                               │
│                        │  │                                                │
│  excel_finanzmodell.py │  │  diagramm_generator.py sankey                 │
│  → 3 Sheets:           │  │  → Mermaid.js Sankey-Code                     │
│    Summary, Regional,  │  │    (Transaktionsflüsse Region → Währung)       │
│    Raw Data            │  │  → SVG-Render via mmdc                         │
│  → Formeln, Pivot,     │  │                                                │
│    Bedingte Formt.     │  │                                                │
└────────┬───────────────┘  └───────────┬────────────────────────────────────┘
         │ q1_bericht.xlsx              │ transaktionsfluss.svg
         └───────────────┬──────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────────────┐
│  SCHRITT 4 — PowerPoint (Office-Arbeit)                                     │
│                                                                             │
│  pptx_generator.py erstellen "Q1 2026 Quartalsbericht"                     │
│    --excel    q1_bericht.xlsx  (Tabellen & KPIs einbetten)                 │
│    --diagramm transaktionsfluss.svg  (Sankey auf Slide 3)                  │
│    --template corporate_vorlage.pptx                                       │
│    --output   Q1_2026_Quartalsbericht.pptx                                 │
│  → Präsentationsfertige .pptx mit Titelbild, KPI-Übersicht,               │
│    Regionaltabellen, Sankey-Diagramm, Anhang                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Datenstrom-Protokoll zwischen Skills

Jeder Skill kommuniziert ausschließlich über definierte Schnittstellen.
Kein Skill hat direkten Zugriff auf das Output eines anderen Skills —
Weitergabe erfolgt ausschließlich über stdout/Dateipfad:

| Von → Nach | Übergabe-Format | Sicherheit |
|---|---|---|
| PostgreSQL MCP → ETL | JSON-Lines via stdout | Kein Datei-Schreiben außerhalb Container |
| ETL → Excel-Skill | CSV-Datei (Pfad bestätigt) | Nutzerfreigabe für Zielpfad |
| ETL → Diagramm-Skill | JSON-Aggregat via stdout | Kein direktes Datenbankzugriff im Diagramm-Skill |
| Excel + SVG → pptx-Skill | Dateipfade als Argumente | Read-Only für Quelldateien |
| pptx-Skill → Nutzer | .pptx-Dateipfad nach stdout | Niemals automatisch per E-Mail senden |

### Asynchrone Skill-Verkettung — Orchestrierungs-Muster

Unabhängige Skills laufen parallel; abhängige Skills sequenziell.
Orchestrierungs-Entscheidung vor jedem Job:

```
Kann Schritt B beginnen, bevor Schritt A fertig ist?
├── Nein (B braucht A's Output) → Sequenziell: A | B
└── Ja  (B ist unabhängig)     → Parallel:     A & B & C; wait

Beispiel Quartalsbericht:
  Schritt 1 (PostgreSQL)    → sequenziell (Basis für alles)
  Schritt 2 (ETL)           → sequenziell (braucht Schritt 1)
  Schritt 3a (Excel)        \
                             → PARALLEL (beide brauchen nur Step 2)
  Schritt 3b (Sankey)       /
  Schritt 4 (PowerPoint)    → sequenziell (braucht 3a + 3b)
```

**Bash-Implementierung (Parallel-Ausführung mit wait):**

```bash
set -euo pipefail

# Schritt 1+2: Sequenziell
python db_agentic_memory.py kontext abrufen --projekt Q1-2026 > kontext.json
# MCP-Abfrage erfolgt via Claude Code + MCP-Tool, Output → CSV
python csv_etl_pipeline.py bereinigen q1_raw.csv > q1_bereinigt.csv

# Schritt 3: Parallel
python excel_finanzmodell.py q1_bereinigt.csv --output q1_bericht.xlsx &
PID_EXCEL=$!

python diagramm_generator.py sankey q1_bereinigt.csv \
  --titel "Transaktionsflüsse Q1 2026" --output transaktionsfluss.svg &
PID_DIAG=$!

# Auf beide warten
wait $PID_EXCEL && wait $PID_DIAG

# Schritt 4: Sequenziell (nach Parallel-Block)
python pptx_generator.py erstellen "Q1 2026 Quartalsbericht" \
  --excel q1_bericht.xlsx \
  --diagramm transaktionsfluss.svg \
  --output Q1_2026_Quartalsbericht.pptx
```

### Domänen-Übergabe-Protokoll (Office ↔ Programmieren)

Beim Übergang zwischen Domänen gelten strikte Regeln:

| Übergang | Regel | Grund |
|---|---|---|
| Programmieren → Office | Rohdaten immer als CSV oder JSON übergeben, niemals als direkten DB-Cursor | Trennung von Datenzugriff und Analyse |
| Office → Programmieren | Excel-Ergebnisse als CSV exportieren (kein .xlsx als Programm-Input) | Maschinenlesbarkeit, keine Formel-Nebenwirkungen |
| Beide → Präsentation | Immer Read-Only-Quellen für pptx/Word; niemals Originaldaten in Präsentation einbetten | Versionssicherheit, kein Datenverlust |
| Jeder Skill | Niemals direkt in Produktionssysteme schreiben (DB, Cloud-Storage, E-Mail) | Immer Nutzerfreigabe vor Externe-Übergabe |

---

## Sicherheitsregeln — niemals verletzen

- **Kein Dateizugriff ohne Freigabe**: Keine Datei öffnen, lesen oder schreiben ohne explizite Nutzererlaubnis.
- **Keine hardcodierten absoluten Pfade** außer `/tmp` — immer relative Pfade oder konfigurierbare Variablen.
- **Kein `rm -rf` ohne Guard** — immer `confirm()`-Pattern oder `--dry-run` vorschalten.
- **Variablen immer quoten**: `"$var"` statt `$var` (verhindert Wordsplitting und Globbing).
- **`set -euo pipefail` + `IFS=$'\n\t'`** in jedem Bash-Skript als erste ausführbare Zeile.
- **Temp-Files**: Nur via `mktemp` + `trap 'rm -f "$tmp"' EXIT`.

---

## Verwandte Ressourcen

| Ressource | Ladestufe | Kategorie | Inhalt |
|---|---|---|---|
| `resources/pptx_generator.py` | 3 | Hybride Workflows | PowerPoint-Generator: Slides aus Excel/CSV/SVG/Diagrammen; Corporate-Template-Support; Titel/KPI/Tabellen/Chart-Layouts |
