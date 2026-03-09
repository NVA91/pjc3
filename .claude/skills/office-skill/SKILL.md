---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: office-skill
description: >
  Datenadministration, ETL-Pipelines, Data Warehousing,
  Excel-Finanzmodellierung, Analyse und Visualisierung.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Office-Arbeit
    description: >
      Datenadministration, ETL-Pipelines, Data Warehousing,
      Excel-Finanzmodellierung, Analyse und Visualisierung

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

resources:
  - resources/csv_etl_pipeline.py
  - resources/excel_finanzmodell.py
  - resources/excel_aufgaben.py
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

## Hauptkategorie: Office-Arbeit — Datenadministration, Analyse und Visualisierung

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
| `resources/csv_etl_pipeline.py` | 3 | Office-Arbeit | Polars-ETL: Discovery, Schema, Bereinigung, Transformation, Data Warehousing |
| `resources/excel_finanzmodell.py` | 3 | Office-Arbeit | 3-Statement-Modell, SaaS-Metriken, Szenario-Analyse, Formelinjektion, Verifikation |
| `resources/excel_aufgaben.py` | 3 | Office-Arbeit | Excel-Aufgabentabelle mit Status-Farben (einfach) |
