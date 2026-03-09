---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: shell-scripting-skill
description: >
  Sichere, strukturierte und wiederholbare Shell-Skripte sowie Office-Automatisierung:
  ETL-Pipelines (CSV/Polars/Pandas), Excel-Finanzmodelle (.xlsx) mit Formelinjektion,
  Data Warehousing, CSS und visuelle Aufbereitung. Keine Dateien oder Pfade werden
  ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

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
| `resources/csv_verarbeitung.py` | 3 | Datenformate | CSV lesen/schreiben/filtern (Stdlib, einfache Ops) |
| `resources/shell_template.sh` | 3 | Shell-Scripting | Vollständige sichere Bash-Vorlage |
| `resources/excel_aufgaben.py` | 3 | Office-Arbeit | Excel-Aufgabentabelle mit Status-Farben (einfach) |
| `resources/tabellen.css` | 3 | Datenformate | Tabellen-Grundstil + Status-Badges (BEM) |
| `CLAUDE.md` → Docker-Sicherheit | — | — | Immutable Config, Volume Mounts, UID-Isolation |
| `.claude/skills/n8n-workflow-manager/SKILL.md` | — | — | MCP vs. REST API Entscheidung |
