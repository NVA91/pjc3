# ETL-Pipeline — Detailreferenz

## Orchestrierungs-Phasen

| Phase | Beschreibung | Technologie / MCP-Tool | Resultat |
|-------|-------------|----------------------|---------|
| **1. Discovery** | Autonomes Scannen nach neuen Datenexporten | MCP `get_files_list` + Glob-Muster | System findet Rohdaten ohne manuelles Hochladen |
| **2. Schema-Inspektion** | Analyse der internen Dateistruktur | MCP `get_schema` → `df.schema.items()` | Modell versteht Entitäten, verhindert Datentypfehler |
| **3. Bereinigung & Normalisierung** | Fehler, Duplikate, Standardisierung | `csv_etl_pipeline.py` → Polars/Pandas | Unicode-Fehler, Datumsformate, Duplikate korrigiert |
| **4. Sichere Transformation** | Aggregation, Filterung, Zusammenführung | `execute_polars_sql` + `pl.concat` | Konsolidierte Datensätze, einlagerungsbereit |

## Werkzeugwahl — MCP vs. Python-Ressource

```
Aufgabe erfordert Dateisystem-Zugriff (Verzeichnis scannen, Schema lesen)?
├── Ja  → MCP-Tools: get_files_list / get_schema
│          → Ergebnis (stdout) an Python-Ressource weitergeben
└── Nein → Direkt: resources/csv_etl_pipeline.py
           Modi: entdecken | inspizieren | bereinigen | transformieren | pipeline
```

## Pflicht-Ablauf für jeden ETL-Job

1. **Discovery-Ergebnis zeigen** — Gefundene Dateien dem Nutzer auflisten, bevor Verarbeitung startet.
2. **Schema kommunizieren** — Erkannte Spalten und Datentypen vor Phase 3 bestätigen lassen.
3. **Bereinigungsplan vorlegen** — Korrekturen erst nach Nutzerfreigabe durchführen.
4. **Transformations-Output nach stdout** — Niemals direkt in Produktionsdatenbank schreiben ohne Prüfschritt.
5. **Protokoll erzeugen** — Statistik: Zeilen ein/aus, Fehler, Duplikate.

## Polars vs. Pandas — Entscheidungstabelle

| Kriterium | Polars | Pandas |
|-----------|--------|--------|
| Datenmenge | > 100.000 Zeilen oder > 50 MB | < 100.000 Zeilen, kleine Dateien |
| SQL-ähnliche Abfragen | `execute_polars_sql` — nativ | Umweg über `query()` |
| Speichereffizienz | Arrow-basiert, deutlich geringer | Höherer Speicherbedarf |
| Ecosystem | Wachsend, modern | Sehr breit (sklearn, seaborn...) |
| **Standard** | **Bevorzugen** | Nur bei Ecosystem-Zwang |

## Data Warehousing — Erweiterter Scope

| Aufgabe | Methode | Übergabe an |
|---------|---------|-------------|
| Fehlende Werte identifizieren | Musterbasiert: Median/Modus/Vorwärts-Fill je Dtype | Datenbank-Skill oder Excel-Modell |
| Telefonnummern normalisieren | Regex → E.164-Format (`+49...`) | Relationale DB |
| Firmennamen standardisieren | Strip + Title-Case + Alias-Mapping | Master-Data-Management |
| Vollständigkeit prüfen | Pflichtfeld-Validierung vor Übergabe | Downstream-System |

**Übergabe-Protokoll** (vor Weiterleitung an DB-Skill):
- Ausgabe als JSON-Lines (eine Zeile = ein Datensatz) nach stdout
- Fehler-Zeilen separat nach stderr mit Zeilennummer und Fehlertyp
- Abschluss-Statistik: `{"ok": N, "fehler": M, "duplikate": K}`

## CSV-Verarbeitung — Entscheidungsbaum

```
Handelt es sich um einen ETL-Prozess (Discovery → Schema → Bereinigung → Transform)?
├── Ja  → resources/csv_etl_pipeline.py  (Polars, alle 4 Phasen)
│          + MCP-Tools für Discovery/Schema wenn Dateisystem-Zugriff nötig
└── Nein → Einfache Operation?
           ├── Nein → resources/csv_verarbeitung.py  (Stdlib)
           └── Ja   → Shell-Tools: awk, cut, sort, tail (kein Python nötig)
```

## CSV Shell-Kurzreferenz

| Operation | Befehl |
|-----------|--------|
| Header überspringen | `tail -n +2 datei.csv` |
| Spalte 2 filtern (> 100) | `awk -F',' 'NR>1 && $2>100'` |
| Spalten 1 und 3 | `cut -d',' -f1,3` |
| Sortieren nach Spalte 2 | `sort -t',' -k2,2n` |
| Zeilen zählen | `awk -F',' 'END{print NR-1}'` |
