---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: shell-scripting-skill
description: >
  Sichere, strukturierte und wiederholbare Shell-Skripte sowie Office-Automatisierung:
  ETL-Pipelines (CSV/Polars/Pandas), Excel-Finanzmodelle (.xlsx) mit Formelinjektion,
  Data Warehousing, CSS und visuelle Aufbereitung. Agenten-Ausführung in leichtgewichtigen,
  kurzlebigen Docker-Containern (node:20-slim, Non-Root, UID-Passthrough).
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Office-Arbeit
    description: >
      Datenadministration, ETL-Pipelines, Data Warehousing,
      Excel-Finanzmodellierung, Analyse und Visualisierung
  - name: Vision
    description: >
      Bildbeschreibung, Dokumentenextraktion (Rechnungen/Quittungen),
      Diagramm-Analyse, Screenshot-Auswertung, Batch-Verarbeitung,
      PDF-Chunking, Graphlit-Integration, OCR-Prompt-Engineering
  - name: Visualisierung
    description: >
      Deklarative Diagramme (Mermaid, PlantUML, D2, Graphviz): Flowcharts,
      Gantt, Sequenz, C4, ERD, Sankey — aus Text, CSV oder Meeting-Notizen
  - name: Container-Ausführung
    description: >
      Agenten in kurzlebigen Docker-Containern: node:20-slim (Debian, kein Alpine),
      Non-Root-User (useradd -m -u 1001), UID-Passthrough (-u $(id -u):$(id -g)),
      ephemere Dateisysteme (--rm), Volume-Mounts mit Schreibrecht-Kontrolle,
      YOLO-Modus (--dangerously-skip-permissions) in Docker Desktop Sandboxes / MicroVMs
  - name: Hybride Workflows / Cross-Domain-Pipelines
    description: >
      Nahtlose Verkettung von Office- und Programmier-Skills ohne Medienbruch:
      PostgreSQL → CSV → Excel + Sankey → PowerPoint in einer Pipeline,
      asynchrone Parallel-Orchestrierung (Bash &-Operator + wait),
      PowerPoint-Generierung (python-pptx), Command-Chain-Tabelle,
      Datenstrom-Protokoll zwischen Skills (stdout/JSON-Lines/Dateipfad)
  - name: Datenbank
    description: >
      MCP-basierte Datenbankintegration: PostgreSQL-Schema-Exploration ohne Token-Overload,
      Read-Only MCP-Konfiguration (DROP TABLE / DELETE via Protokoll blockiert),
      Schreiboperationen ausschließlich als Flyway-Migrationsdateien (nie direkt ausführen),
      SQLite als Agentic-Memory-Backend (Langzeitpersistenz über Session-Grenzen hinweg),
      lokaler HTTP-Server + Headless-Agent + SQLite-MCP-Server für Entitäten und Kontextbeziehungen
  - name: Frontend / CSS-Framework / Design-System
    description: >
      Tailwind CSS v3/v4 (CSS-First @theme, @import-Migration, gap statt Margin-Hacks),
      shadcn/ui und Radix UI Komponentenbibliotheken,
      Anti-generische-KI-Ästhetik (Design-Manifest: verbotene Fonts, Pflicht-Asymmetrien),
      CSS Custom Properties für kohärente Farbpaletten, hardware-beschleunigte
      Mikrointeraktionen (transform/opacity/will-change), Gradient Meshes, Noise-Overlays,
      Subagenten-Orchestrierung (component-composition-reviewer, design-verification,
      a11y-wcag-compliance-auditor) für WCAG 2.1 AA und Figma-Token-Abgleich
  - name: Shell-Scripting
    description: Sichere, wiederholbare Bash/Zsh-Automatisierungen
  - name: Datenformate
    description: CSV, Excel (.xlsx), CSS

triggers:
  # Office-Arbeit / ETL / Data Warehousing
  - ETL-Pipeline aufbauen oder automatisieren (Extract, Transform, Load)
  - CSV-Dateien scannen, bereinigen, normalisieren oder konsolidieren
  - Polars oder Pandas für Datentransformation einsetzen
  - Schema einer CSV-Datei inspizieren oder Datentypen prüfen
  - Daten deduplizieren, Datumsformate oder Telefonnummern normalisieren
  - Mehrere CSV-Dateien zusammenführen (concat/merge)
  - SQL-ähnliche Abfragen auf flachen Dateien ausführen
  - Daten-Einlagerung in strukturierte Formate automatisieren
  - Fehlende Werte identifizieren und musterbasiert auffüllen
  - Daten für relationale Datenbank-Skills aufbereiten
  # Excel-Automatisierung / Finanzmodellierung
  - Excel-Finanzmodell erstellen (Income Statement, Balance Sheet, Cash Flow)
  - SaaS-Metriken modellieren (ARR, Churn, LTV, MRR)
  - Szenario-Analyse erstellen (Base / Bull / Bear Case)
  - Excel-Formeln injizieren statt Hardcoded Values eintragen
  - Pivot-Tabellen sortieren, filtern oder Schema ändern
  - Bedingte Formatierung oder Datenbalken in Excel anwenden
  - Finanzmodellierungs-Konventionen anwenden (blaue/schwarze Schrift)
  - Zirkelbezüge (#REF!, #VALUE!) in Excel debuggen und korrigieren
  - Excel-Datei mit LibreOffice headless verifizieren
  # Vision / Bildbeschreibung / Dokumentenanalyse
  - Bild beschreiben oder kontextuell interpretieren (Vision)
  - Rechnung, Quittung oder Lieferschein aus Bild/Scan extrahieren
  - Balken-, Linien- oder Kreisdiagramm aus Screenshot analysieren
  - UI-Screenshot oder Fehlermeldung strukturiert beschreiben
  - Mehrere Bilder oder Dokumente als Batch verarbeiten
  - Visuelle Informationen in JSON oder Markdown überführen
  - OCR-ähnliche Extraktion aus analogen Dokumenten durchführen
  - Automatisierte Reporting-Workflows mit Bildinput aufbauen
  # Visualisierung / Diagramme
  - Flussdiagramm oder Prozessablauf als Mermaid/PlantUML generieren
  - Gantt-Diagramm aus CSV-Daten oder Projektplan erstellen
  - Sequenzdiagramm für API-Interaktionen oder Workflows zeichnen
  - C4-Modell für Systemarchitektur oder Komponenten erstellen
  - Entity-Relationship-Diagramm (ERD) aus Datenbankschema generieren
  - Sankey-Diagramm für Volumenverteilungen oder Datenflüsse erstellen
  - Diagramm-Code in SVG oder PNG rendern (mmdc, dot, d2, plantuml)
  - Meeting-Notizen oder Prozessbeschreibung in Flowchart überführen
  - D2 oder Graphviz DOT-Code für komplexe Graphen schreiben
  # Container-Ausführung / Docker / Agent-Isolation
  - Dockerfile für Agenten-Ausführung erstellen (node:20-slim, Non-Root)
  - Warum Alpine für NPM-Agenten ungeeignet ist (musl libc Linker-Fehler)
  - Non-Root-User im Container anlegen (useradd -m -u 1001)
  - Docker-Basis-Image für CLI-Agenten wählen und sichern
  - docker run mit UID-Passthrough (-u $(id-u):$(id-g)) konfigurieren
  - Read-Only-Filesystem-Fehler durch fehlenden UID-Passthrough debuggen
  - Kurzlebige Container mit --rm und Volume-Mount für Workspace aufsetzen
  - Agenten-Dateisystem nach Session-Ende rückstandslos verwerfen
  - --dangerously-skip-permissions für autonome Write-Ops im Container aktivieren
  - YOLO-Modus: Code schreiben, Container bauen und E2E-Tests in MicroVM ausführen
  - Docker Desktop Sandboxes / MicroVMs für isolierte Agenten-Umgebungen einrichten
  # Datenbank / MCP-Datenbankintegration / Agentic Memory
  - PostgreSQL-Schema über MCP-Server iterativ inspizieren (kein Token-Overload)
  - SELECT-Abfragen strukturiert über MCP-Tools senden (kein Klartext-Credential)
  - MCP-Host verwaltet physische Datenbankverbindung; Agent sendet nur Requests
  - SQLite als Agentic-Memory-Backend einrichten
  - Langzeitgedächtnis für Agenten jenseits des Kontextfensters implementieren
  - Lokalen HTTP-Server zur Steuerung einer Headless-Agent-Session aufbauen
  - Entitäten und kontextuelle Beziehungen in SQLite-MCP-Server speichern
  - Historischen Kontext aus früheren Sessions abrufen und weiterverwenden
  - MCP-Server auf Read-Only konfigurieren (DROP TABLE / DELETE verhindern)
  - Schreiboperationen als SQL-Migrationsdatei generieren statt direkt ausführen
  - Flyway/Liquibase-Migrationsskripte für Schema-Änderungen erzeugen
  - SQL-Migration mit Rollback-Kommentar und Idempotenz-Pattern erstellen
  - CI/CD-Pipeline für sichere Datenbankmigrationen einrichten (Staging → Prod)
  - CREATE INDEX CONCURRENTLY ohne Table-Lock auf Produktionstabellen
  # Frontend / CSS-Framework / Design-System / UI/UX
  - Tailwind CSS Utility-First-Komponenten implementieren
  - shadcn/ui oder Radix UI Komponentenbibliothek einrichten und nutzen
  - "Generische KI-Ästhetik" im Frontend vermeiden
  - Design-Manifest mit verbotenen Fonts und Pflicht-Design-Patterns erstellen
  - Inter, Roboto oder andere übernutzte Systemschriftarten durch Alternativen ersetzen
  - Asymmetrische, nicht-uniforme Layouts mit Tailwind CSS bauen
  - Überlappende Elemente (negative margins, z-index, translate) umsetzen
  - Gradient Mesh als Hintergrundtextur implementieren (CSS / SVG)
  - Noise-Overlay für organische Hintergrundtexturen hinzufügen
  - CSS Custom Properties (--color-*, --spacing-*) für kohärente Farbpalette definieren
  - Hardware-beschleunigte Mikrointeraktionen mit transform und opacity umsetzen
  - will-change, translate3d, backface-visibility für GPU-Rendering optimieren
  - Hover-, Focus- und Active-States als feinkörnige Mikrointeraktionen gestalten
  - Komponentensystem aus shadcn/ui-Primitives zusammenbauen
  - UI-Komponenten-Bibliothek (Button, Card, Input, Dialog) konfigurieren
  - Tailwind v4: @tailwind-Direktiven durch @import "tailwindcss" ersetzen
  - Tailwind v4: tailwind.config.js durch @theme-Direktive in CSS migrieren
  - Tailwind v4: Margin-Hacks (mt-/ml- auf Kind) durch gap-Utilities auf Parent ersetzen
  - Dark Mode konsistent via dark:-Klassen implementieren (kein @media-Mix)
  - Subagenten für Frontend: component-composition-reviewer + design-verification + a11y
  - WCAG 2.1 AA: Farbkontrast (4.5:1), ARIA-Attribute, Tastaturnavigation prüfen
  - Figma-Token-Abgleich: Spacing / Farbe / Typografie gegen Design-System verifizieren
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
  # Shell-Scripting
  - Shell-Skripte erstellen, prüfen oder überarbeiten
  - Bash- oder Zsh-Automatisierungen entwickeln
  # Weitere Datenformate
  - CSS-Dateien strukturieren, benennen (BEM) oder stylen
  - Komplexe Inhalte in Tabellen- oder Baumstruktur aufbereiten
  - Expliziter Aufruf via /shell-scripting-skill

resources:
  - resources/csv_etl_pipeline.py
  - resources/excel_finanzmodell.py
  - resources/vision_dokument.py
  - resources/diagramm_generator.py
  - resources/docker_agent_run.sh
  - resources/db_agentic_memory.py
  - resources/ui_design_system.py
  - resources/pptx_generator.py
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

### Data Warehousing — Erweiterter Scope

Die ETL-Pipeline bildet die Grundlage für autonomes Data Warehousing. Zusätzlich zu den 4 Phasen:

| Aufgabe | Methode | Übergabe an |
|---|---|---|
| Fehlende Werte identifizieren | Musterbasiert: Median/Modus/Vorwärts-Fill je Dtype | Datenbank-Skill oder Excel-Modell |
| Telefonnummern normalisieren | Regex → E.164-Format (`+49...`) | Relationale DB |
| Firmennamen standardisieren | Strip + Title-Case + Alias-Mapping | Master-Data-Management |
| Vollständigkeit prüfen | Pflichtfeld-Validierung vor Übergabe | Downstream-System |

**Übergabe-Protokoll** (vor Weiterleitung an DB-Skill):
- Ausgabe als JSON-Lines (eine Zeile = ein Datensatz) nach stdout
- Fehler-Zeilen separat nach stderr mit Zeilennummer und Fehlertyp
- Abschluss-Statistik: `{"ok": N, "fehler": M, "duplikate": K}`

---

## Excel-Automatisierung und finanzielle Modellierung

Der xlsx-Skill kombiniert analytische Kraft (pandas) mit Formatierungspräzision (openpyxl),
ohne die visuelle Integrität bestehender Unternehmensvorlagen zu zerstören.

### Kerngrundsatz: Formelinjektion statt Hardcoded Values

```
FALSCH → Zelle B12 = 142857  (statisch, verliert Abhängigkeiten)
RICHTIG → Zelle B12 = "=B5*B8*(1+B11)"  (dynamisch, Analyst kann B11 ändern)
```

Alle Finanzmodelle werden mit echten Excel-Formeln geschrieben. Aktualisiert ein Analyst
eine Annahme (z. B. Wachstumsrate in B11), berechnet Excel das gesamte Modell neu.

### Fähigkeiten-Übersicht

| Bereich | Fähigkeiten | Ressource |
|---|---|---|
| **Institutionelle Finanzmodelle** | 3-Statement (IS/BS/CF), SaaS-Metriken (ARR/Churn/LTV), Szenario-Analyse (Base/Bull/Bear) | `excel_finanzmodell.py` |
| **Datenaufbereitung & Pivot** | Importierte Daten sortieren/filtern, Pivot-Schema ändern, fehlende Werte füllen, Duplikate entfernen | `excel_finanzmodell.py` |
| **Industriestandard-Formatierung** | Blaue Schrift = manuelle Eingabe, Schwarz = Formel, bedingte Formatierung, Datenbalken, Zahlenformate | `excel_finanzmodell.py` |
| **Debugging & Verifikation** | Zirkelbezüge lokalisieren, #REF!/#VALUE! korrigieren, LibreOffice headless Formel-Check | `excel_finanzmodell.py` |

### Farbcodierungs-Konvention (Finanzmodellierungs-Standard)

| Schriftfarbe | Hex | Bedeutung | Wann setzen |
|---|---|---|---|
| Blau | `#0070C0` | Manuelle Eingabe / Annahme | Hardcoded input cells |
| Schwarz | `#000000` | Berechnete Formel | Alle `=`-Zellen |
| Grün | `#00B050` | Verknüpfung zu anderem Sheet | Cross-sheet references |
| Rot | `#FF0000` | Fehler / Warnung | Negative Werte, Checks |

### Ablauf für jedes Finanzmodell

1. **Struktur bestätigen** — Welche Sheets? Welche Perioden (Monate/Jahre)?
2. **Annahmen-Zellen definieren** — Blau färben, benennen (Named Ranges)
3. **Formeln injizieren** — Niemals berechnete Werte hardcoden
4. **Formatierung anwenden** — Zahlenformate, bedingte Formatierung
5. **Verifizieren** — LibreOffice headless öffnen, Formel-Errors prüfen, stdout-Report

### Debugging-Protokoll (#REF!, #VALUE!, Zirkelbezüge)

```
1. Fehlerzellen lokalisieren → ws.iter_rows() + cell.value.startswith("#") prüfen
2. Ursache klassifizieren:
   ├── #REF!  → gelöschte/verschobene Quellzelle → Formel neu aufbauen
   ├── #VALUE! → falscher Datentyp in Formel → Typ-Cast oder Quellzelle prüfen
   └── Zirkelbezug → Abhängigkeits-Graph traversieren → Iterative Calculation oder Formel umstrukturieren
3. Korrektur dokumentieren → Kommentar in Zelle schreiben
4. Re-Verifikation → LibreOffice erneut ausführen → 0 Errors bestätigen
```

---

## Vision: Bildbeschreibung und visuelle Dokumentenanalyse

Das Modell nähert sich Bildern nicht über einfache OCR oder Objekterkennung, sondern über
denselben Reasoning-Apparat wie bei Text: Achsenbeschriftungen werden gelesen, Relationen
zwischen Datenpunkten korreliert, strategische Bedeutung im Geschäftskontext interpretiert.

### Anwendungsfälle und Ausgabeformate

| Anwendungsfall | Input | Ausgabeformat | Ressource |
|---|---|---|---|
| **Allgemeine Bildbeschreibung** | Beliebiges Bild (PNG/JPG/WebP) | Markdown-Prose | `vision_dokument.py beschreiben` |
| **Rechnungs-/Quittungsextraktion** | Scan, Foto, PDF-Screenshot | JSON (strukturiert) | `vision_dokument.py rechnung` |
| **Diagramm-Analyse** | Chart-Screenshot (Balken/Linie/Kreis) | JSON + Interpretation | `vision_dokument.py diagramm` |
| **UI-Screenshot / Fehleranalyse** | Browser/App-Screenshot | Markdown strukturiert | `vision_dokument.py screenshot` |
| **Batch-Verarbeitung** | Verzeichnis mit Bildern | JSON-Lines (1 Datei = 1 Zeile) | `vision_dokument.py batch` |

### Architektur-Prinzip

```
Bild-Input (lokal / URL)
    ↓
Claude Vision API (claude-sonnet-4-6, base64 oder URL)
    ↓  kontextuelle Interpretation (kein simple OCR)
Strukturierter Output (JSON / Markdown)
    ↓
Downstream: ETL-Pipeline | Excel-Modell | Datenbank-Skill | Report
```

### Rechnungsextraktion — JSON-Schema (Standard)

```json
{
  "dokument_typ": "rechnung | quittung | lieferschein | unbekannt",
  "rechnungsnummer": "...",
  "datum": "YYYY-MM-DD",
  "faellig_am": "YYYY-MM-DD | null",
  "lieferant": { "name": "...", "adresse": "...", "ust_id": "..." },
  "empfaenger": { "name": "...", "adresse": "..." },
  "positionen": [
    { "beschreibung": "...", "menge": 0, "einheit": "...",
      "einzelpreis": 0.0, "gesamtpreis": 0.0, "mwst_satz": 0.19 }
  ],
  "zwischensumme": 0.0,
  "mwst_betrag": 0.0,
  "gesamtbetrag": 0.0,
  "waehrung": "EUR",
  "konfidenz": 0.0,
  "anmerkungen": "..."
}
```

### Diagramm-Analyse — Ausgabestruktur

```json
{
  "diagramm_typ": "balken | linie | kreis | streuung | tabelle | unbekannt",
  "titel": "...",
  "x_achse": { "bezeichnung": "...", "einheit": "..." },
  "y_achse": { "bezeichnung": "...", "einheit": "..." },
  "datenpunkte": [{ "label": "...", "wert": 0.0 }],
  "trend": "steigend | fallend | stabil | gemischt",
  "interpretation": "Kontextuelle Bedeutung in 2-3 Sätzen",
  "handlungsempfehlung": "..."
}
```

### Pflicht-Ablauf für jeden Vision-Job

1. **Bildpfad bestätigen** — Pfad dem Nutzer anzeigen; kein autonomes Scannen ohne Freigabe.
2. **Modus wählen** — `rechnung` / `diagramm` / `screenshot` / `beschreiben` / `batch`.
3. **API-Key prüfen** — `ANTHROPIC_API_KEY` muss gesetzt sein (kein `load_dotenv()` in Ressource).
4. **Output nach stdout** — JSON oder Markdown; kein direktes Schreiben in Drittsysteme.
5. **Konfidenz kommunizieren** — Bei niedriger Konfidenz (`< 0.7`) Nutzer zur manuellen Prüfung auffordern.

### Batch-Verarbeitung — Übergabe an ETL-Pipeline

```
Verzeichnis mit Bildern
    → vision_dokument.py batch (JSON-Lines nach stdout)
    → Pipe zu csv_etl_pipeline.py transformieren
    → Konsolidierter Datensatz für DB-Einlagerung
```

```bash
# Beispiel-Verkettung (Rechnungen batch → ETL → Excel)
python vision_dokument.py batch ./rechnungen/ rechnung \
  | python csv_etl_pipeline.py transformieren - "SELECT * FROM df WHERE konfidenz > 0.8" \
  > rechnungen_verifiziert.csv
```

### Infrastrukturelle Herausforderungen & Skalierung

Rohe API-Aufrufe stoßen bei hochskalierenden Office-Anwendungen an Grenzen.
Pflicht-Überlegungen vor dem Einsatz:

| Herausforderung | Ursache | Lösung |
|---|---|---|
| **Token-Limit bei PDFs** | Jede Seite ≈ 1.500–3.000 Token; 100-Seiten-PDF > Kontext-Fenster | PDF → Bilder (1 Bild/Seite) + Chunking; `vision_dokument.py batch` |
| **API-Ratenlimits** | Burst > 50 req/min triggert 429-Fehler | Exponentieller Backoff + Queue (max 3 Retry); Graphlit übernimmt dies |
| **Tabellenstruktur-Verlust** | Modell ignoriert Zellen-Grenzen ohne expliziten Prompt | Prompt muss explizit fordern: `Behalte alle Zeilenumbrüche und Tabellenstruktur exakt bei` |
| **Ausgabe-Inkonsistenz** | JSON-Schema weicht bei seltenen Layouts ab | JSON-Schema im System-Prompt mitgeben; `IFERROR`-ähnliches Fallback in Parser |
| **Hochskalierbar (> 100 Seiten)** | Eigenimplementierung von Chunking + Retry zu komplex | Graphlit-Integration: übernimmt Chunking, Ratenlimit, Normalisierung |

**Prompt-Engineering für OCR-ähnliche Aufgaben (Pflicht):**

```
System-Prompt Ergänzung für Tabellenextraktion:
"Behalte alle Zeilenumbrüche EXAKT bei. Trenne Tabellenspalten mit | (Pipe).
 Füge nach jeder Tabellenzeile einen Newline ein. Verliere keine Zelle."
```

**Graphlit-Integration (für Enterprise-Scale):**
- Graphlit übernimmt: PDF-to-Image-Konvertierung, Seiten-Chunking, Retry-Logik, Output-Normalisierung
- Das Modell ist exklusiv für semantische und visuelle Extraktion zuständig
- Schnittstelle: Graphlit MCP-Server → `get_document_content` → Ergebnis an ETL-Pipeline

---

## Grafiken und Diagramme — Deklarative Visualisierung

Anstatt Pixel manuell zu verschieben, übersetzt der Agent abstrakte Beschreibungen,
Meeting-Notizen oder CSV-Datenströme in exakten, maschinenlesbaren Diagramm-Code.
Rendering-Engines (mmdc, dot, d2, plantuml) erzeugen daraus SVG oder PNG.

### Tool-Auswahl nach Diagramm-Typ

| Diagramm-Typ | Empfohlenes Tool | Stärke | Wann verwenden |
|---|---|---|---|
| **Flowchart / Entscheidungsbaum** | Mermaid.js | Web-nativ, Markdown-einbettbar | Prozesse, Workflows, Decision Trees |
| **Sequenzdiagramm** | Mermaid.js / PlantUML | Präzise Lebenslinien, Aktivierungen | API-Interaktionen, Protokolle |
| **Gantt-Diagramm** | Mermaid.js | Einfache Syntax, CSV-kompatibel | Projektplanung, Meilensteine |
| **C4-Modell** | PlantUML (C4-Lib) | Strukturierte 4-Level-Architektur | System-/Container-/Komponenten-Sicht |
| **ERD (Entity-Relationship)** | Mermaid.js / PlantUML | Relationen, Kardinalitäten | Datenbankschema, Datenmodelle |
| **Sankey-Diagramm** | D2 / Graphviz | Volumenflüsse, Proportionen | Ressourcenverteilung, Datenflüsse |
| **Komplexe Graphen** | Graphviz DOT | Beliebige Knoten-/Kanten-Layouts | Abhängigkeits-Graphen, Netzwerke |

### Rendering-Pipeline

```
Beschreibung / CSV / Meeting-Notizen
    ↓
diagramm_generator.py <typ> (Claude API generiert Code)
    ↓
Diagramm-Code (Mermaid / PlantUML / D2 / DOT) → stdout
    ↓  (optional, wenn lokale Tools installiert)
Rendering: mmdc | plantuml | d2 | dot
    ↓
SVG / PNG-Datei
```

### Rendering-Voraussetzungen (optional, lokal)

| Tool | Install | Für |
|---|---|---|
| `mmdc` (Mermaid CLI) | `npm install -g @mermaid-js/mermaid-cli` | Mermaid → SVG/PNG |
| `plantuml` | `apt install plantuml` | PlantUML → SVG/PNG |
| `d2` | `curl -fsSL https://d2lang.com/install.sh \| sh` | D2 → SVG/PNG |
| `dot` (Graphviz) | `apt install graphviz` | DOT → SVG/PNG |

### Pflicht-Ablauf für jeden Diagram-Job

1. **Diagramm-Typ klären** — Flowchart / Gantt / Sequenz / C4 / ERD / Sankey?
2. **Input-Format prüfen** — Freitext, CSV oder strukturierte Beschreibung?
3. **Tool wählen** — Tool-Tabelle konsultieren; Standard: Mermaid (web-kompatibel)
4. **Code generieren** — `diagramm_generator.py` aufrufen; Code nach stdout
5. **Rendern** — Lokal (wenn Tool installiert) oder Code in Online-Editor zeigen
6. **Nutzer-Review** — Code und visuelle Vorschau zeigen, Anpassungen iterieren

---

## Agenten-Ausführung in leichtgewichtigen Containern

Agenten-Prozesse werden in kurzlebige, ephemere Docker-Container ausgelagert.
Das Container-Dateisystem wird nach Beendigung der Session rückstandslos verworfen (`--rm`).
Diese Architektur verhindert persistente Seiteneffekte und Konfigurationsdrift.

### Basis-Image-Wahl: node:20-slim (Debian) — NICHT Alpine

| Kriterium | `node:20-slim` (Debian) | `node:20-alpine` (Alpine) |
|---|---|---|
| **C-Bibliothek** | glibc (GNU standard) | musl libc |
| **Native NPM-Pakete** | Vollständig kompatibel | Häufig Linker-Fehler bei nativen Modulen |
| **CLI-Agenten** (z.B. `@anthropic-ai/claude-code`) | Problemlos | Kryptische Fehler möglich |
| **Image-Größe** | ~200 MB (slim) | ~100 MB |
| **Empfehlung** | **Pflicht für NPM-CLI-Agenten** | Nur für einfache Node.js-Anwendungen |

**Warum musl libc Probleme macht:**
Native NPM-Pakete (`*.node`-Binaries) werden gegen glibc kompiliert. Alpine's musl libc ist
nicht ABI-kompatibel — beim Laden der Binary tritt ein Linker-Fehler auf:
`Error loading shared library libstdc++.so.6: No such file or directory`.
Workarounds (Kompatibilitäts-Pakete, Cross-Compilation) sind fragil und nicht produktionsgeeignet.

### Sicherheitskonformes Dockerfile (Standard-Template)

```dockerfile
# PFLICHT: node:20-slim (Debian-basiert) — KEIN Alpine (musl libc Inkompatibilität)
FROM node:20-slim

# Non-Root-User anlegen: UID 1001 (feste Zuweisung, nicht root)
# -m → Home-Verzeichnis anlegen (/home/claude)
# -u 1001 → feste UID, entspricht CLAUDE-Agent-Konvention aus CLAUDE.md
RUN useradd -m -u 1001 claude

# CLI-Agent global installieren (als root, vor USER-Wechsel)
RUN npm install -g @anthropic-ai/claude-code

# Workspace-Verzeichnis vorbereiten
WORKDIR /workspace

# Wechsel zum Non-Root-User VOR dem Entrypoint — kritisch für Sicherheit
USER claude

ENTRYPOINT ["claude"]
```

**Warum `USER claude` vor `ENTRYPOINT`?**
Wird der ENTRYPOINT als root ausgeführt, hat ein kompromittierter Agent-Prozess
effektive root-Rechte im Container. Der Wechsel zu UID 1001 reduziert den
Privilege-Level auf das absolute Minimum — konsistent mit dem UID-Namespace-
Isolations-Prinzip aus CLAUDE.md (Gebot UID-Namespace-Isolation).

### Laufzeit-Orchestrierung: docker run mit UID-Passthrough

```bash
# PFLICHT-Kommando für Lese- und Schreiboperationen:
docker run --rm \
  -v "$(pwd):/workspace" \
  -u "$(id -u):$(id -g)" \
  claude-agent-image \
  <claude-argumente>
```

**Parameter-Erklärung:**

| Parameter | Wert | Zweck |
|---|---|---|
| `--rm` | — | Container-Dateisystem nach Beendigung löschen (ephemer) |
| `-v "$(pwd):/workspace"` | Host-CWD → `/workspace` | Agent kann Host-Dateien lesen und schreiben |
| `-u "$(id -u):$(id -g)"` | Host-UID:GID | UID-Passthrough — kritisch für Schreibrecht |

**Warum `-u $(id -u):$(id -g)` kritisch ist:**

```
Ohne -u:
  Container läuft als UID 1001 (claude)
  Host-Dateien gehören UID 1000 (lokaler User)
  → Schreibzugriff verweigert: "Read-Only Filesystem"-Fehler
  → Agent kann keine Dateien im gemounteten Volume erzeugen/ändern

Mit -u $(id-u):$(id-g):
  Container übernimmt Host-UID und Host-GID
  → Dateieigentümer stimmt überein → Vollständiger Lese-/Schreibzugriff
  → Neu erzeugte Dateien gehören dem Host-User (kein sudo nötig)
```

**Fehler-Diagnose — "Read-Only Filesystem" im Container:**

```
Symptom: agent error: EROFS: read-only file system, open '/workspace/output.json'
Ursache:  -u-Flag fehlt → Container-UID ≠ Host-Datei-UID
Fix:      docker run ... -u "$(id -u):$(id -g)" ...
```

### Erweitertes Run-Kommando (mit Umgebungsvariablen)

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -u "$(id -u):$(id -g)" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  --network host \
  claude-agent-image \
  --print "Analysiere /workspace/daten.csv und schreibe Ergebnis nach /workspace/ergebnis.json"
```

**Sicherheits-Hinweise zum erweiterten Kommando:**
- `-e ANTHROPIC_API_KEY` → API-Key als Umgebungsvariable (kein File-Mount, da Claude Code ihn aus `$env` liest)
- `--network host` → Nur wenn Agent externe APIs aufrufen muss; andernfalls weglassen
- `--network none` → Vollständige Netzwerk-Isolation für rein lokale Verarbeitungsaufgaben

### Pflicht-Ablauf für Container-Agenten-Setup

1. **Image wählen** — `node:20-slim` (Pflicht); Alpine explizit ablehnen
2. **Non-Root-User** — `useradd -m -u 1001 claude`; UID mit CLAUDE.md-Konvention abgleichen
3. **Schreibrecht-Test** — `docker run --rm -v "$(pwd):/workspace" -u "$(id -u):$(id -g)" image touch /workspace/test.txt`
4. **Ephemer-Verhalten prüfen** — `--rm` Flag bestätigen; kein named Volume für Session-Daten
5. **API-Key** — Nur über `-e`-Flag übergeben; kein Hardcoding in Dockerfile oder Image

### YOLO-Modus: --dangerously-skip-permissions in Docker-Isolierung

Für autonome Write-Operationen (Code schreiben, Dateien erzeugen, Pakete installieren)
muss die interaktive Bestätigungslogik des Agenten deaktiviert werden.

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -u "$(id -u):$(id -g)" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  --network none \
  claude-agent-image \
  --dangerously-skip-permissions \
  --print "Schreibe Unit-Tests für alle Funktionen in /workspace/src/"
```

**Warum `--dangerously-skip-permissions` im Container architektonisch sicher ist:**

```
Ohne Docker:
  Agent läuft direkt auf Host → skip-permissions = voller Systemzugriff
  → GEFÄHRLICH auf der Entwicklerworkstation

Mit Docker:
  Agent läuft in isoliertem Container-FS
  → skip-permissions = Vollzugriff nur innerhalb des Containers
  → Host-System bleibt durch Docker-Isolationsgrenze geschützt
  → Container-FS wird nach Beendigung verworfen (--rm)
  → Primärer Schutzmechanismus = Docker-Isolation, nicht Permission-Dialog
```

**Wann YOLO-Modus angemessen ist:**

| Szenario | YOLO | Grund |
|---|---|---|
| Autonome Code-Generierung in Container | ✓ | Docker ist Sicherheitsgrenze |
| E2E-Tests in MicroVM ausführen | ✓ | Isoliertes Dateisystem |
| Direkter Einsatz auf Entwickler-Host | ✗ | Kein primärer Schutz |
| Produktionsserver | ✗ | Niemals |

### Docker Desktop Sandboxes / MicroVMs

Moderne Erweiterung: Docker Desktop Sandboxes implementieren spezialisierte MicroVMs,
die über Standard-Container-Isolation hinausgehen.

| Feature | Standard-Docker-Container | Docker Desktop Sandbox (MicroVM) |
|---|---|---|
| **Dateisystem-Isolation** | Container-FS (Overlay) | Vollständig isoliertes VM-Dateisystem |
| **Netzwerk-Kontrolle** | Bridge / host / none | Konfigurierbare Netzwerkzugriffsregeln pro VM |
| **Docker-Daemon** | Shared Host-Daemon | Privater Docker-Daemon pro Sandbox |
| **YOLO-Modus** | Architektonisch vertretbar | Vollständig sicher (MicroVM-Grenze) |
| **Use Case** | Standard-Agenten-Ausführung | "YOLO-Modus"-Agenten, CI/CD-Pipelines |

**YOLO-Modus in MicroVM — Maximale Autonomie:**
Der Agent kann in Höchstgeschwindigkeit Code schreiben, Container bauen und
End-to-End-Tests ausführen, ohne jegliches Risiko für die Entwicklerworkstation.
Die MicroVM-Grenze bildet eine härtere Isolationsschicht als Standard-Container.

### Ressource

Vollständiges Build-und-Run-Skript (inkl. YOLO-Modus): `resources/docker_agent_run.sh` (Ladestufe 3)

---

## Datenbankintegration, Schemaverwaltung und Agentic Memory

KI-Agenten greifen über das **Model Context Protocol (MCP)** sicher auf relationale und
nicht-relationale Datenbanken zu — ohne Klartext-Credentials im Kontextfenster und ohne
das gesamte Datenbankschema auf einmal laden zu müssen.

### Architektur: MCP als intelligente Abstraktionsschicht

```
Agent (Modell)
    │  strukturierte Requests (MCP-Protokoll)
    ▼
MCP-Server (z.B. postgres-mcp, sqlite-mcp)
    │  physische Datenbankverbindung (verwaltet vom MCP-Host)
    ▼
Datenbank (PostgreSQL / SQLite / andere)
```

**Kernprinzip:**
- **MCP-Host** (Client-Applikation) verwaltet die physische Datenbankverbindung
- **Agent** sendet ausschließlich strukturierte Requests an die MCP-Tools
- Credentials verbleiben im MCP-Host — niemals im Agenten-Kontext

### PostgreSQL-Integration: Iterative Schema-Exploration

Der Agent inspiziert das Datenbankschema iterativ, um den Token-Overhead zu minimieren.
Niemals das gesamte Schema auf einmal laden — stattdessen:

```
Schritt 1: Tabellenliste holen
  MCP-Tool: list_tables → ["users", "orders", "products", ...]

Schritt 2: Relevante Tabellen selektiv inspizieren
  MCP-Tool: get_schema("orders") →
    { columns: [{name: "id", type: "uuid", pk: true}, ...],
      indexes: [...], foreign_keys: [...] }

Schritt 3: Gezielte SELECT-Abfrage konstruieren
  MCP-Tool: execute_query("SELECT o.id, u.email, o.total
                           FROM orders o JOIN users u ON o.user_id = u.id
                           WHERE o.created_at > NOW() - INTERVAL '7 days'
                           LIMIT 100")
```

**Ablaufregeln für PostgreSQL-Abfragen:**

| Regel | Begründung |
|---|---|
| Nur SELECT (kein INSERT/UPDATE/DELETE) | Read-Only-Sicherheit; Schreiboperationen nur nach expliziter Freigabe |
| LIMIT immer setzen (max. 1.000) | Verhindert Token-Explosion durch große Result-Sets |
| Schema iterativ erkunden (Tabelle für Tabelle) | Kein Token-Overload durch Bulk-Schema-Import |
| Keine Credentials im Prompt | MCP-Host verwaltet Connection-String; Agent kennt ihn nicht |
| Abfrage-Ergebnis als JSON nach stdout | Standardisiertes Format für ETL-Pipeline-Weitergabe |

### SQLite als Agentic Memory — Langzeitgedächtnis

SQLite ermöglicht persistentes Agenten-Gedächtnis über Session-Grenzen hinweg.
Nach dem Ende des Kontextfensters bleibt das Wissen in der Datenbank erhalten.

**Architektur: Lokaler HTTP-Server + Headless-Agent + SQLite-MCP-Server**

```
Entwickler / Orchestrierer
    │  HTTP-Request (POST /task)
    ▼
Lokaler HTTP-Server (Python/FastAPI)
    │  startet Headless-Agent-Session
    ▼
Claude Code (headless, --print)
    │  MCP-Protokoll
    ▼
SQLite-MCP-Server
    │  SQL
    ▼
SQLite-Datenbank (memory.db)
    ├── entities     (Projektentitäten: Dateien, Funktionen, Konzepte)
    ├── relations    (Kontextbeziehungen: "gehört zu", "implementiert", "hängt ab von")
    ├── interactions (Interaktionshistorie: Zeitstempel, Prompt, Response, Tags)
    └── context      (Abrufbarer Kontext: Session-übergreifende Fakten)
```

**Speicher-Operationen:**

```python
# Entität speichern (z.B. neue Funktion entdeckt)
mcp.execute("INSERT INTO entities (name, type, description, project)
             VALUES ('parse_invoice', 'function', 'Extracts fields from invoice PDF', 'pjc3')")

# Beziehung knüpfen
mcp.execute("INSERT INTO relations (from_entity, relation, to_entity)
             VALUES ('parse_invoice', 'implementiert', 'vision_dokument.py')")

# Historischen Kontext abrufen (neue Session)
mcp.execute("SELECT e.name, e.description, i.response
             FROM entities e JOIN interactions i ON e.name = i.entity
             WHERE e.project = 'pjc3'
             ORDER BY i.created_at DESC LIMIT 20")
```

**Agentic-Memory-Workflow:**

```
Session 1: Agent analysiert Codebase
  → Entitäten extrahieren (Funktionen, Module, Konzepte)
  → Beziehungen in SQLite speichern
  → Interaktionshistorie persistieren
  Context-Window endet → SQLite-DB bleibt erhalten

Session 2 (neue Session, leeres Context-Window):
  → Relevante Entitäten und Relationen aus SQLite laden
  → Historischen Kontext rekonstruieren
  → Agent arbeitet mit vollständigem Projektwissen
  → Neue Erkenntnisse werden zurückgeschrieben
```

### Datenbank-Sicherheit: Read-Only-Konfiguration und Schreiboperationen via CI/CD

Sicherheitsaspekte spielen bei der Agenten-Datenbank-Interaktion eine übergeordnete Rolle.
Der Architekturansatz setzt auf mehrere Schutzschichten, um destruktive Aktionen zu verhindern.

#### Read-Only MCP-Konfiguration — Primärer Schutz

MCP-Server für relationale Datenbanken werden **primär auf schreibgeschützte Abfragen** konfiguriert.
Protokollbasierte und kryptografische Schranken verhindern unbeabsichtigte destruktive Aktionen:

| Bedrohung | Ursache | MCP-Schutz |
|---|---|---|
| `DROP TABLE` | Halluzination oder Prompt-Injection | MCP-Server: `allowed_operations: [SELECT]` — DDL blockiert |
| Unautorisiertes `DELETE` | Fehlerhafte WHERE-Klausel, falscher Kontext | DML-Whitelist: nur SELECT zugelassen |
| Daten-Exfiltration | `SELECT * FROM users` ohne LIMIT | Result-Size-Limit im MCP-Server (z. B. `max_rows: 1000`) |
| Credential-Leak | Connection-String im Prompt | MCP-Host verwaltet Credentials — Agent sieht sie nie |

**MCP-Server-Konfiguration (postgres-mcp — Beispiel):**

```json
{
  "allowed_operations": ["SELECT"],
  "max_rows": 1000,
  "schema_exploration": true,
  "write_operations": false,
  "ddl_operations": false
}
```

**Protokollbasierte Schranken — wie sie wirken:**

```
Agent sendet: execute_query("DROP TABLE users")
    ↓
MCP-Server prüft: Operation-Typ = DDL (nicht in allowed_operations)
    ↓
MCP-Server antwortet: { "error": "Operation not permitted: DDL statements are disabled" }
    ↓
Agent erhält Fehler → kein Datenbankzugriff erfolgt
    ↓
Agent soll Nutzer informieren, nicht umgehen
```

> **Pflicht:** Der Agent darf niemals versuchen, MCP-Sicherheitsschranken zu umgehen
> (z.B. durch SQL-Injection-Techniken gegen den MCP-Server selbst oder durch
> Formulierung von DELETE als verschachtelte SELECT-Subqueries wo möglich).
> Bei verweigertem Zugriff: Nutzer informieren, nicht eskalieren.

#### Schreiboperationen via Migrationsdateien — Einziger erlaubter Write-Weg

Sind Schreiboperationen (Schema-Migrationen, Daten-Korrekturen) zwingend notwendig,
**generiert der Agent ausschließlich SQL-Code als Textdatei** — er führt ihn niemals direkt aus.

```
Agent                        Dateisystem                  CI/CD-Pipeline
  │                               │                              │
  │  SQL generieren               │                              │
  ├──────────────────────────────►│                              │
  │  migrations/V3__add_index.sql │                              │
  │                               │                              │
  │  Review anfordern             │                              │
  ├──────────────────────────────►│ (Nutzer prüft Datei)         │
  │                               │                              │
  │                               │  git commit + push           │
  │                               ├─────────────────────────────►│
  │                               │                              │  Flyway/Liquibase
  │                               │                              │  führt Migration aus
  │                               │                              │  (Staging → Prod)
```

**Migrations-Datei-Namenskonvention (Flyway-Standard):**

```
migrations/
├── V1__create_users_table.sql        # Erstellt Tabelle
├── V2__add_email_index.sql           # Fügt Index hinzu
├── V3__add_created_at_column.sql     # Fügt Spalte hinzu (nicht nullable mit DEFAULT)
└── R__refresh_materialized_views.sql # Repeatable Migration (immer neu ausführen)
```

**Pflicht-Inhalte einer Migrations-Datei (Agent muss alle generieren):**

```sql
-- Migration: V3__add_created_at_column.sql
-- Zweck:     Zeitstempel-Spalte für Audit-Trail in orders-Tabelle
-- Autor:     Claude Code (generiert, nicht ausgeführt)
-- Erstellt:  2026-03-09
-- Review:    Pflichtfeld — vor CI/CD-Ausführung durch Entwickler prüfen
--
-- RÜCKGÄNGIG MACHEN:
--   ALTER TABLE orders DROP COLUMN IF EXISTS created_at;

BEGIN;

-- Neue Spalte mit DEFAULT (verhindert NOT NULL Constraint-Fehler bei bestehenden Zeilen)
ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Index für Datumsbereichs-Abfragen
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at
  ON orders(created_at DESC);

-- Verifikation (Agent zeigt Erwartungswert)
-- ERWARTUNG: 0 Zeilen ohne created_at
-- SELECT COUNT(*) FROM orders WHERE created_at IS NULL;

COMMIT;
```

**Kritische Regeln für Migrations-SQL (Agent muss einhalten):**

| Regel | SQL-Pattern | Grund |
|---|---|---|
| `ADD COLUMN IF NOT EXISTS` | `ALTER TABLE t ADD COLUMN IF NOT EXISTS c TYPE` | Idempotent — wiederholbar ohne Fehler |
| `NOT NULL` immer mit `DEFAULT` | `NOT NULL DEFAULT 'wert'` | Bestehende Zeilen nicht blockieren |
| `CREATE INDEX CONCURRENTLY` | `CREATE INDEX CONCURRENTLY IF NOT EXISTS` | Kein Table-Lock auf Produktionstabellen |
| `BEGIN; ... COMMIT;` | Transaktion wrappen | Rollback bei Fehler automatisch |
| Rollback-Kommentar pflicht | `-- RÜCKGÄNGIG MACHEN: DROP COLUMN ...` | Entwickler kennt Undo-Weg |
| Nur eine Änderung pro Datei | 1 `ALTER TABLE` pro Migration | Atomare, nachvollziehbare Änderungen |

#### Vollständiger Sicherheits-Entscheidungsbaum

```
Agent erhält Datenbankaufgabe
    │
    ├── Aufgabe = Daten lesen / analysieren?
    │   → SELECT via MCP-Tool (Read-Only)
    │   → LIMIT setzen → Ergebnis nach stdout
    │
    ├── Aufgabe = Schema inspizieren?
    │   → list_tables → get_schema (iterativ, Tabelle für Tabelle)
    │   → Kein Bulk-Import
    │
    ├── Aufgabe = Daten schreiben / Schema ändern?
    │   → SQL-Migrationsdatei generieren (Flyway-Konvention)
    │   → Nutzer zur Prüfung auffordern
    │   → Datei im migrations/-Verzeichnis ablegen
    │   → CI/CD-Pipeline informieren (niemals selbst ausführen)
    │
    └── Aufgabe = Credentials abfragen / Connection-String anzeigen?
        → VERWEIGERN — Credentials verbleiben im MCP-Host
        → Nutzer informieren: Credentials sind MCP-Host-Verantwortung
```

### Pflicht-Ablauf für Datenbankjobs

1. **Zugang prüfen** — MCP-Server verfügbar? (`list_tables` als Connectivity-Test)
2. **Schema iterativ erkunden** — Nur benötigte Tabellen inspizieren (niemals Bulk-Import)
3. **Read-Only zuerst** — SELECT konstruieren, Ergebnis validieren, bevor Schreib-Ops
4. **Token-Kontrolle** — LIMIT setzen; Result > 500 Zeilen → Zusammenfassung statt Raw-Dump
5. **Schreib-Ops als Migration** — SQL als Datei generieren, niemals direkt ausführen
6. **Memory-Persistenz** — Neue Erkenntnisse sofort in SQLite schreiben (nicht am Session-Ende)

### Ressource

SQLite Agentic Memory Backend: `resources/db_agentic_memory.py` (Ladestufe 3)

---

## CSS-Frameworks, UI/UX-Automatisierung und Frontend-Design-Systeme

Die Frontend-Entwicklung erfordert strikt komponentenbasiertes Design und Utility-First CSS.
Kernaufgabe des Skills: UI-Implementierungen automatisieren und dabei konsequent
**generische KI-Ästhetik** durch programmatische Design-Restriktionen vermeiden.

### Design-Manifest: Anti-Generisch-KI-Ästhetik (Pflicht)

Jedes UI-Projekt beginnt mit einem expliziten Design-Manifest. Es definiert verbotene
Elemente und erzwingt visuelle Differenzierung durch harte Regeln.

**Verbotene Elemente — niemals einsetzen:**

| Element | Verbotene Werte | Erlaubte Alternative |
|---|---|---|
| **Systemschriftarten** | Inter, Roboto, DM Sans, Plus Jakarta Sans | Syne, Fraunces, Space Grotesk, Clash Display, Cabinet Grotesk |
| **Einheitliche Abstände** | `p-4` überall, `gap-4` in jedem Grid | Bewusste Rhythmus-Brüche: `p-3`, `p-7`, `p-12` kombinieren |
| **Flache Hintergründe** | `bg-gray-100`, `bg-white` ohne Textur | Gradient Mesh, Noise-Overlay, radiale Gradienten |
| **Symmetrische Layouts** | Zentrierung überall, gleiche Spaltenbreiten | Asymmetrie: 7/5-Spalten, bewusste Lücken, versetzte Grids |
| **Standard-Hover-States** | `hover:opacity-70` ohne weitere Transition | Mikro-Bewegungen: scale, translate, clip-path-Transitions |
| **Generische Farben** | `blue-500`, `gray-200` als direkte Klassen | CSS Custom Properties: `var(--color-accent-primary)` |

**Pflicht-Design-Elemente — immer umsetzen:**

```css
/* Design-Manifest: Wird in jede CSS/Tailwind-Konfiguration eingebettet */

:root {
  /* Farbpalette via Custom Properties — kein direktes Tailwind-Klassen-Chaos */
  --color-bg-primary:      #0a0a0f;
  --color-bg-secondary:    #12121a;
  --color-accent-primary:  #7c3aed;   /* Nicht "violet-600" — eigene Benennung */
  --color-accent-warm:     #f59e0b;
  --color-text-primary:    #fafaf9;
  --color-text-muted:      #71717a;
  --color-border-subtle:   rgba(255,255,255,0.08);

  /* Bewusste Asymmetrie in Spacing */
  --space-xs:   0.375rem;  /* 6px  — kein Standard-4px-Grid */
  --space-sm:   0.625rem;  /* 10px */
  --space-md:   1.125rem;  /* 18px */
  --space-lg:   1.875rem;  /* 30px */
  --space-xl:   3.25rem;   /* 52px */
  --space-2xl:  5.5rem;    /* 88px */

  /* Typografie-Skala — nicht-uniform */
  --font-display: 'Clash Display', 'Syne', system-ui;
  --font-body:    'Cabinet Grotesk', 'Space Grotesk', system-ui;
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;
}
```

### Tailwind CSS: Utility-First-Architektur

**Tailwind-Konfiguration für Anti-Generic-Ästhetik (`tailwind.config.js`):**

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      // Eigene Farbpalette — ersetzt Tailwind-Defaults vollständig
      colors: {
        brand: {
          bg:       'var(--color-bg-primary)',
          surface:  'var(--color-bg-secondary)',
          accent:   'var(--color-accent-primary)',
          warm:     'var(--color-accent-warm)',
          text:     'var(--color-text-primary)',
          muted:    'var(--color-text-muted)',
          border:   'var(--color-border-subtle)',
        },
      },
      // Asymmetrische Spacing-Skala
      spacing: {
        '4.5': '1.125rem',   // --space-md
        '7.5': '1.875rem',   // --space-lg
        '13':  '3.25rem',    // --space-xl
        '22':  '5.5rem',     // --space-2xl
      },
      // Schriftarten aus Design-Manifest
      fontFamily: {
        display: ['Clash Display', 'Syne', 'system-ui'],
        body:    ['Cabinet Grotesk', 'Space Grotesk', 'system-ui'],
        mono:    ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      // Animation-Kurven für Mikrointeraktionen
      transitionTimingFunction: {
        'spring':       'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        'smooth-out':   'cubic-bezier(0.16, 1, 0.3, 1)',
        'anticipate':   'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
      // Asymmetrische Grid-Layouts
      gridTemplateColumns: {
        '7-5':  '7fr 5fr',
        '3-7':  '3fr 7fr',
        '5-3-4':'5fr 3fr 4fr',
      },
    },
  },
}
```

**Layout-Asymmetrie mit Tailwind (Pflicht-Muster):**

```html
<!-- FALSCH: Symmetrisches 2-Spalten-Grid -->
<div class="grid grid-cols-2 gap-4 p-4">...</div>

<!-- RICHTIG: Bewusst asymmetrisch -->
<div class="grid grid-cols-7-5 gap-x-13 gap-y-7 px-13 py-22
            max-lg:grid-cols-1 max-lg:gap-y-13">
  <div class="col-span-1 translate-y-7.5"> <!-- Vertikaler Versatz --> </div>
  <div class="col-span-1 -translate-y-4.5 relative"> <!-- Gegenläufig --> </div>
</div>
```

### shadcn/ui und Radix UI: Komponentenbibliotheken

shadcn/ui und Radix UI bieten zugängliche (a11y-konforme), headless Komponenten-Primitives.
shadcn/ui kopiert Quellcode direkt in das Projekt — kein opaker Abhängigkeitsgraph.

**Setup (Next.js / Vite):**

```bash
# shadcn/ui initialisieren (kopiert Komponenten in ./components/ui/)
npx shadcn@latest init

# Gewünschte Komponenten hinzufügen
npx shadcn@latest add button card dialog input select badge

# Radix UI direkt (für Custom-Primitives ohne shadcn-Wrapper)
npm install @radix-ui/react-dialog @radix-ui/react-popover @radix-ui/react-tooltip
```

**shadcn/ui Komponenten-Customization (Anti-Generic):**

```tsx
// components/ui/button.tsx — NACH dem Kopieren anpassen
// Standard shadcn-Button ist generisch — folgende Änderungen sind Pflicht:

const buttonVariants = cva(
  // Basis: kein abgerundetes Rechteck — bewusste Form-Entscheidung
  "inline-flex items-center justify-center font-body font-medium transition-all duration-200",
  {
    variants: {
      variant: {
        // Primär: gradient + transform-Mikrointeraktion
        default: [
          "bg-gradient-to-r from-brand-accent to-violet-500",
          "text-white px-7 py-3",
          "rounded-[3px]",          // Fast-nicht-abgerundet — bewusste Wahl
          "hover:scale-[1.02] hover:-translate-y-[1px]",
          "hover:shadow-[0_8px_30px_rgba(124,58,237,0.4)]",
          "transition-[transform,box-shadow] duration-200 ease-spring",
          "active:scale-[0.98] active:translate-y-0",
        ],
        // Ghost: nur Border, kein Background
        ghost: [
          "border border-brand-border text-brand-text",
          "px-6 py-3 rounded-[3px]",
          "hover:border-brand-accent hover:text-brand-accent",
          "hover:bg-brand-accent/5",
          "transition-all duration-150 ease-smooth-out",
        ],
        // Destructive: roter Gradient mit Shake-Animation
        destructive: [
          "bg-gradient-to-r from-red-600 to-rose-500 text-white",
          "px-6 py-3 rounded-[3px]",
          "hover:animate-[shake_0.3s_ease-in-out]",
        ],
      },
      size: {
        sm:   "text-sm px-4 py-2",
        md:   "text-base px-7 py-3",
        lg:   "text-lg px-9 py-4",
        icon: "w-10 h-10 p-0",
      },
    },
    defaultVariants: { variant: "default", size: "md" },
  }
)
```

### Hintergrundtexturen: Gradient Mesh und Noise-Overlay

Flache Hintergründe sind verboten. Jeder Hintergrund erhält mindestens eine Textur-Schicht.

**Gradient Mesh (CSS):**

```css
.bg-mesh {
  background-color: var(--color-bg-primary);
  background-image:
    /* Schicht 1: radiales Blob oben-links (Akzentfarbe) */
    radial-gradient(
      ellipse 60% 50% at 10% 15%,
      rgba(124, 58, 237, 0.35) 0%,
      transparent 70%
    ),
    /* Schicht 2: radiales Blob unten-rechts (Warm-Akzent) */
    radial-gradient(
      ellipse 55% 45% at 90% 85%,
      rgba(245, 158, 11, 0.20) 0%,
      transparent 65%
    ),
    /* Schicht 3: linearer Gradient für Tiefe */
    linear-gradient(
      135deg,
      rgba(12, 12, 20, 0.8) 0%,
      rgba(18, 18, 30, 1) 100%
    );
}

/* Noise-Overlay: organische Textur über jeder Fläche */
.noise-overlay::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
  pointer-events: none;
  mix-blend-mode: overlay;
  opacity: 0.6;
  z-index: 0;
}
```

**Tailwind-Integration (Gradient Mesh als Plugin):**

```js
// tailwind.config.js — Plugin für Mesh-Hintergründe
const plugin = require('tailwindcss/plugin')

module.exports = {
  plugins: [
    plugin(({ addUtilities }) => {
      addUtilities({
        '.bg-mesh-violet': {
          backgroundImage: [
            'radial-gradient(ellipse 60% 50% at 10% 15%, rgba(124,58,237,0.35) 0%, transparent 70%)',
            'radial-gradient(ellipse 55% 45% at 90% 85%, rgba(245,158,11,0.20) 0%, transparent 65%)',
          ].join(', '),
        },
        '.noise': {
          position: 'relative',
          isolation: 'isolate',
        },
      })
    }),
  ],
}
```

### Hardware-beschleunigte Mikrointeraktionen

Mikrointeraktionen müssen auf der GPU laufen. Nur `transform` und `opacity` ändern —
niemals `width`, `height`, `top`, `left`, `margin` animieren (triggert Layout-Reflow).

**GPU-konforme CSS-Grundregeln:**

```css
/* Pflicht-Muster für alle interaktiven Elemente */
.interactive {
  /* GPU-Layer erzwingen: Browser rendert Element auf separater Compositing-Schicht */
  will-change: transform, opacity;

  /* 3D-Kontext aktivieren → Subpixel-glattes Rendering */
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;

  /* Basis-Transition */
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1),
              opacity   200ms cubic-bezier(0.16, 1, 0.3, 1);
}

.interactive:hover {
  /* Nur transform/opacity — KEIN width/height/top/margin */
  transform: translate3d(0, -2px, 0) scale(1.02);
  opacity: 1;
}
```

**Mikrointeraktions-Bibliothek (CSS Custom Properties):**

```css
/* Karten-Hover: Elevation + subtile Rotation */
.card-interactive {
  transform: translate3d(0, 0, 0);
  transition: transform 250ms ease-smooth-out,
              box-shadow 250ms ease-smooth-out;
  will-change: transform;
}
.card-interactive:hover {
  transform: translate3d(0, -4px, 0) rotate(-0.3deg);
  box-shadow:
    0 12px 40px rgba(0,0,0,0.3),
    0 4px 12px rgba(124,58,237,0.2);
}

/* Icon-Microinteraction: Rotation + Scale */
.icon-spin-hover {
  transition: transform 300ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
  will-change: transform;
}
.icon-spin-hover:hover { transform: rotate(15deg) scale(1.15); }

/* Link-Underline: clip-path Slide-In */
.link-fancy {
  position: relative;
  text-decoration: none;
}
.link-fancy::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 1px;
  background: var(--color-accent-primary);
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 250ms cubic-bezier(0.16, 1, 0.3, 1);
}
.link-fancy:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}
```

**Tailwind-Klassen für GPU-Mikrointeraktionen:**

| Interaktion | Tailwind-Klassen | Anmerkung |
|---|---|---|
| Karten-Hover (Elevation) | `hover:-translate-y-1 hover:shadow-2xl transition-[transform,shadow] duration-200 ease-smooth-out` | `will-change-transform` ergänzen |
| Button-Press-Feedback | `active:scale-[0.97] active:translate-y-[1px]` | Physisches Drück-Gefühl |
| Icon-Bounce | `hover:scale-110 hover:-rotate-3 transition-transform duration-300 ease-spring` | Federnde Bewegung |
| Fade-In-Up (Appearing) | `opacity-0 translate-y-4 → opacity-100 translate-y-0` | Nur mit JS-Toggle oder `@starting-style` |
| Shimmer-Loading | `animate-[shimmer_1.5s_infinite]` | Via Tailwind-Custom-Animation |

### Typografie: Schriftarten-Manifest

**Verbotene Schriftarten (generische KI-Ästhetik):**

```
❌ Inter        — Übernutzt in 90% aller KI-generierten UIs
❌ Roboto       — Google-Standard, uncharakteristisch
❌ DM Sans      — Beliebt aber austauschbar
❌ Plus Jakarta Sans — Verbreitet in Startup-Templates
❌ Nunito       — Kindlich und generisch
❌ Poppins      — Übernutzt, indifferent
```

**Erlaubte und empfohlene Schriftarten:**

| Schriftart | Charakter | Einsatz | Bezug |
|---|---|---|---|
| **Clash Display** | Geometrisch, eigenwillig | Headlines, Display | `fontsource` / CDN |
| **Syne** | Variable, modern-expressiv | Headlines, Akzente | Google Fonts |
| **Fraunces** | Optisch, Retro-Revival | Editorial, Long-form | Google Fonts |
| **Cabinet Grotesk** | Charakterstarke Grotesque | Body, UI | `fontsource` |
| **Space Grotesk** | Technisch, präzise | Code-nahe UIs, SaaS | Google Fonts |
| **Gambarino** | Hochkontrast-Serif | Display, Hero | CDN |
| **JetBrains Mono** | Lesbar, Developer-Ästhetik | Code, Terminal | CDN / `fontsource` |

**Font-Einbindung via CSS `@font-face` (Pflicht: kein externes CDN in Produktion):**

```css
/* Lokal eingebundene Schriftart — kein externer Request */
@font-face {
  font-family: 'Clash Display';
  src: url('/fonts/ClashDisplay-Variable.woff2') format('woff2');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;   /* Verhindert unsichtbaren Text während Ladezeit */
}
```

### Tailwind CSS v4 — Neue Konfigurationsparadigmen (CSS-First)

Tailwind v4 bricht mit der JavaScript-Konfigurationsdatei. Die Instruktionen
**müssen** v4-Projekte von v3-Projekten unterscheiden und entsprechend handeln.

**Erkennungsmerkmal v3 vs. v4:**

```bash
# v3-Projekt:
cat tailwind.config.js   # → Datei existiert, enthält module.exports = {...}
grep "@tailwind" src/    # → @tailwind base; @tailwind components; @tailwind utilities

# v4-Projekt:
cat package.json | grep tailwind   # → "tailwindcss": "^4.0.0"
grep "@import" src/     # → @import "tailwindcss";
```

**Migration v3 → v4 (Agent-Pflichtschritte):**

```
1. @tailwind-Direktiven ersetzen:
   VORHER:  @tailwind base;
            @tailwind components;
            @tailwind utilities;
   NACHHER: @import "tailwindcss";

2. tailwind.config.js → @theme-Direktive:
   VORHER:  module.exports = { theme: { extend: { colors: { brand: '#7c3aed' } } } }
   NACHHER: In CSS-Datei:
            @theme {
              --color-brand: #7c3aed;
              --font-display: 'Clash Display', system-ui;
              --spacing-13: 3.25rem;
            }

3. Margin-Hacks durch gap ersetzen:
   VORHER:  <div class="flex"><div class="mt-4 ml-6">...</div></div>
   NACHHER: <div class="flex gap-x-6 gap-y-4">...</div>

4. Dark Mode: Klassen-Varianten statt media-query:
   VORHER:  @media (prefers-color-scheme: dark) { ... }
   NACHHER: dark:bg-brand-bg dark:text-brand-text
            (konsistent durch gesamte App — kein Mix aus beiden Methoden)
```

**Tailwind v4 CSS-First Konfiguration (vollständig):**

```css
/* styles/globals.css — Tailwind v4 Entry Point */
@import "tailwindcss";

/* Design-Tokens via @theme (ersetzt tailwind.config.js vollständig) */
@theme {
  /* Schriftarten (Design-Manifest: kein Inter/Roboto) */
  --font-display: 'Clash Display', 'Syne', system-ui, sans-serif;
  --font-body:    'Cabinet Grotesk', 'Space Grotesk', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;

  /* Asymmetrische Spacing-Skala */
  --spacing-4_5: 1.125rem;
  --spacing-7_5: 1.875rem;
  --spacing-13:  3.25rem;
  --spacing-22:  5.5rem;

  /* Asymmetrische Grid-Templates */
  --grid-template-columns-7-5: 7fr 5fr;
  --grid-template-columns-3-7: 3fr 7fr;

  /* Bézier-Kurven */
  --ease-spring:     cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-smooth-out: cubic-bezier(0.16, 1, 0.3, 1);

  /* Keyframes */
  --animate-fade-up: fade-up 0.4s var(--ease-smooth-out) both;
  --animate-shimmer: shimmer 1.5s infinite linear;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
  from { background-position: -200% 0; }
  to   { background-position:  200% 0; }
}

/* CSS Custom Properties (Design-Tokens, unverändert zu v3) */
:root {
  --color-bg-primary:     #0a0a0f;
  --color-accent-primary: #7c3aed;
  /* ... (vollständig: python ui_design_system.py css) */
}
```

**Verbotene v4-Muster:**

| Verboten | Grund | Korrekt |
|---|---|---|
| `@tailwind base/components/utilities` | v3-Syntax, in v4 deprecated | `@import "tailwindcss"` |
| `module.exports` in tailwind.config.js | v3-API | `@theme { ... }` in CSS |
| `mt-4 ml-6` auf Kindelementen | Margin-Hacks — fragil, wartungsarm | `gap-x-6 gap-y-4` auf Parent |
| Mix aus `@media dark` + `dark:` Klassen | Inkonsistentes Dark-Mode-Verhalten | Ausschließlich `dark:` Klassen |

### Subagenten-Orchestrierung für große Frontend-Projekte

Bei komplexen Webprojekten übernimmt nicht ein einzelner Agent alle Aufgaben.
Stattdessen wird eine spezialisierte Subagenten-Matrix parallel eingesetzt:

```
Orchestrierer (Haupt-Agent)
    ├── component-composition-reviewer  → React-Logik + Komponentenstruktur
    ├── design-verification             → Figma-Token-Abgleich
    └── a11y-wcag-compliance-auditor    → Barrierefreiheit + WCAG 2.1
```

**Subagent 1: `component-composition-reviewer`**

- Aufgabe: Reine React-Komponenten-Logik, Props-Typing, State-Management
- Prüft: Prop-Drilling vermieden? Context oder Zustandsmanager korrekt eingesetzt?
- Ausgabe: TypeScript-Komponenten mit vollständigen Interface-Deklarationen
- Darf **nicht** entscheiden: Farben, Abstände, Typografie — das ist design-verification

**Subagent 2: `design-verification`**

- Aufgabe: Abgleich der Implementierung mit Figma-Designtokens
- Prüft:
  ```
  - Entspricht padding-x dem Figma-Token "spacing/component/padding-md" = 18px?
  - Stimmt font-size mit Figma-Textстиль "body/base" = 16px / Cabinet Grotesk überein?
  - Ist border-radius identisch mit Figma-Corner-Radius = 3px?
  - Entspricht Akzentfarbe exakt dem Figma-Token "color/accent/primary" = #7c3aed?
  ```
- Ausgabe: Diff-Report: `[PASS]` / `[FAIL: Abweichung]` pro Token
- Blockiert Commit bei `[FAIL]`-Einträgen

**Subagent 3: `a11y-wcag-compliance-auditor`**

- Aufgabe: Barrierefreiheits-Audit nach WCAG 2.1 AA (gesetzliche Anforderung)
- Prüft das fertige DOM auf:

| WCAG-Kriterium | Prüfung | Mindest-Anforderung |
|---|---|---|
| **1.4.3 Kontrastverhältnis** | Textfarbe vs. Hintergrund | AA: 4.5:1 (normal), 3:1 (groß) |
| **1.4.11 Nicht-Text-Kontrast** | Buttons, Formulare, Icons | 3:1 gegen Umgebung |
| **2.1.1 Tastaturnavigation** | Alle Funktionen per Tab erreichbar? | Vollständig |
| **2.4.7 Fokus sichtbar** | `focus-visible` vorhanden und sichtbar? | Pflicht |
| **4.1.2 ARIA-Attribute** | role, aria-label, aria-describedby korrekt? | Fehlerlos |
| **1.3.1 Semantische Struktur** | h1–h6-Hierarchie korrekt? Landmarks? | Vollständig |

- Ausgabe: WCAG-Audit-Report (JSON + Markdown), blockiert Commit bei AA-Verstößen

**Orchestrierungs-Workflow:**

```
1. Orchestrierer empfängt Feature-Anforderung
    ↓
2. component-composition-reviewer schreibt React + TypeScript
    ↓ (parallel)
3. design-verification prüft gegen Figma-Tokens
   a11y-wcag-compliance-auditor prüft DOM auf WCAG 2.1 AA
    ↓
4. Beide Agenten liefern Reports an Orchestrierer
    ↓
5. Orchestrierer: Alle [PASS]?
   ├── JA  → git commit (korrekte Nachricht)
   └── NEIN → Befunde an component-composition-reviewer
               → Iteration bis alle [PASS]
```

**Garantien dieser Subagenten-Matrix:**
- Funktional einwandfrei (component-composition-reviewer)
- Visuell identisch zu Figma-Design (design-verification)
- Rechtlich zugänglich — WCAG 2.1 AA (a11y-wcag-compliance-auditor)
- Architektonisch konsistent zur bestehenden Codebasis

### Pflicht-Ablauf für UI/UX-Jobs

1. **Design-Manifest erstellen** — Verbotene Fonts und Pflicht-Muster festlegen, bevor eine Zeile CSS geschrieben wird.
2. **Tailwind-Version prüfen** — v3 oder v4? `@tailwind`-Direktiven (v3) vs. `@import "tailwindcss"` + `@theme` (v4).
3. **CSS Custom Properties definieren** — Farbpalette, Spacing-Skala, Schriftarten in `:root` oder `@theme` zentralisieren.
4. **Tailwind konfigurieren** — v3: `tailwind.config.js`; v4: `@theme { ... }` in CSS. Asymmetrische Grids, Kurven, Keyframes.
5. **Hintergrundtextur wählen** — Gradient Mesh und/oder Noise-Overlay definieren; kein Flat-Color-Hintergrund.
6. **Komponenten customizen** — shadcn/ui-Kopien im Projekt anpassen; Standard-Varianten durch Design-Manifest-konforme ersetzen.
7. **Mikrointeraktionen prüfen** — Nur `transform`/`opacity` in Transitions; `will-change` und `translate3d(0,0,0)` setzen.
8. **Dark-Mode konsistent** — Ausschließlich `dark:` Tailwind-Klassen; kein Mix mit `@media prefers-color-scheme`.
9. **Margin-Hacks eliminieren** — Alle `mt-/ml-/mr-/mb-` auf Kindelementen durch `gap-` auf Parent ersetzen.
10. **Subagenten-Qualitätssicherung** (bei komplexen Projekten) — design-verification + a11y-wcag-compliance-auditor einsetzen.
11. **Visuellen Review** — Screenshot oder Live-Preview; explizit prüfen: Sieht es nach "generischer KI" aus? Wenn ja → Schritt 1.

### Ressource

HTML/CSS/Tailwind Design-System-Generator: `resources/ui_design_system.py` (Ladestufe 3)

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

### Ressource

PowerPoint-Generator: `resources/pptx_generator.py` (Ladestufe 3)

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
| `resources/csv_etl_pipeline.py` | 3 | Office-Arbeit | Polars-ETL: Discovery, Schema, Bereinigung, Transformation, Data Warehousing |
| `resources/excel_finanzmodell.py` | 3 | Office-Arbeit | 3-Statement-Modell, SaaS-Metriken, Szenario-Analyse, Formelinjektion, Verifikation |
| `resources/vision_dokument.py` | 3 | Vision | Claude Vision API: Rechnung/Diagramm/Screenshot/Batch → JSON oder Markdown |
| `resources/diagramm_generator.py` | 3 | Visualisierung | Mermaid/PlantUML/D2/Graphviz-Code generieren + optional rendern (SVG/PNG) |
| `resources/docker_agent_run.sh` | 3 | Container-Ausführung | node:20-slim Dockerfile + docker run (UID-Passthrough, YOLO-Modus, MicroVM-Hinweise) |
| `resources/db_agentic_memory.py` | 3 | Datenbank | SQLite Agentic Memory: Entitäten/Relationen/Interaktionen persistieren + HTTP-Server-Modus |
| `resources/ui_design_system.py` | 3 | Frontend | Design-System-Generator: tailwind.config.js, CSS Tokens, HTML-Starter, Button/Card/Input/Badge, Gradient Mesh, Palette |
| `resources/pptx_generator.py` | 3 | Hybride Workflows | PowerPoint-Generator: Slides aus Excel/CSV/SVG/Diagrammen; Corporate-Template-Support; Titel/KPI/Tabellen/Chart-Layouts |
| `resources/csv_verarbeitung.py` | 3 | Datenformate | CSV lesen/schreiben/filtern (Stdlib, einfache Ops) |
| `resources/shell_template.sh` | 3 | Shell-Scripting | Vollständige sichere Bash-Vorlage |
| `resources/excel_aufgaben.py` | 3 | Office-Arbeit | Excel-Aufgabentabelle mit Status-Farben (einfach) |
| `resources/tabellen.css` | 3 | Datenformate | Tabellen-Grundstil + Status-Badges (BEM) |
| `CLAUDE.md` → Docker-Sicherheit | — | — | Immutable Config, Volume Mounts, UID-Isolation |
| `.claude/skills/n8n-workflow-manager/SKILL.md` | — | — | MCP vs. REST API Entscheidung |
