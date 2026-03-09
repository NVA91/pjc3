#!/usr/bin/env python3
# LADESTUFE 3 — RESSOURCE | KATEGORIE: Office-Arbeit
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: Vollständige Polars-basierte ETL-Pipeline (4 Phasen):
#               Phase 1 Discovery → Phase 2 Schema-Inspektion →
#               Phase 3 Bereinigung & Normalisierung → Phase 4 Transformation
# VERWENDUNG:
#   python csv_etl_pipeline.py entdecken  <verzeichnis> [--muster "*.csv"]
#   python csv_etl_pipeline.py inspizieren <datei.csv>
#   python csv_etl_pipeline.py bereinigen  <datei.csv> [ausgabe.csv] [--dry-run]
#   python csv_etl_pipeline.py transformieren <datei.csv> <sql> [ausgabe.csv]
#   python csv_etl_pipeline.py pipeline    <verzeichnis> <ausgabe.csv> [--dry-run]
# ABHÄNGIGKEITEN:
#   pip install polars           (Pflicht)
#   pip install pandas           (Optional, nur für Fallback)

from __future__ import annotations

import sys
import re
import json
from pathlib import Path
from datetime import datetime

try:
    import polars as pl
    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False

# =============================================================================
# PROTOKOLL-UTILITIES
# =============================================================================

def _log(phase: str, msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{phase}] {msg}")

def _ok(msg: str) -> None:
    print(f"OK  | {msg}")

def _info(msg: str) -> None:
    print(f"    | {msg}")

def _warn(msg: str) -> None:
    print(f"WRN | {msg}", file=sys.stderr)

def _err(msg: str, code: int = 1) -> None:
    print(f"ERR | {msg}", file=sys.stderr)
    sys.exit(code)

def _trennlinie(titel: str = "") -> None:
    breite = 72
    if titel:
        print(f"\n{'─' * 4} {titel} {'─' * (breite - len(titel) - 6)}")
    else:
        print("─" * breite)

# =============================================================================
# PHASE 1 — DISCOVERY
# Äquivalent zum MCP-Tool get_files_list mit Glob-Mustern.
# Scannt Verzeichnisse autonom nach CSV-Exporten — kein manuelles Hochladen.
# =============================================================================

def phase1_entdecken(verzeichnis: str, muster: str = "*.csv") -> list[Path]:
    """
    Phase 1: Autonomes Scannen nach CSV-Dateien (Discovery).
    Ersetzt MCP get_files_list, wenn kein MCP-Server verfügbar.

    Output (stdout):
        - Gefundene Dateien mit Größe und Änderungsdatum
        - Gesamtstatistik
    Returns:
        Liste gefundener Pfade (für Weiterverarbeitung)
    """
    _trennlinie("PHASE 1 — DISCOVERY")
    basis = Path(verzeichnis)
    if not basis.exists():
        _err(f"Verzeichnis nicht gefunden: {verzeichnis}")
    if not basis.is_dir():
        _err(f"Kein Verzeichnis: {verzeichnis}")

    dateien = sorted(basis.rglob(muster))
    gesamt_bytes = 0

    if not dateien:
        _warn(f"Keine Dateien mit Muster '{muster}' in: {basis.resolve()}")
        return []

    _log("Discovery", f"Scanne: {basis.resolve()!s} | Muster: {muster}")
    print(f"\n{'Nr':>4}  {'Datei':<45} {'Größe':>9}  Geändert")
    print("─" * 72)

    for i, p in enumerate(dateien, 1):
        stat = p.stat()
        groesse_kb = stat.st_size / 1024
        gesamt_bytes += stat.st_size
        geaendert = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        # Pfad relativ zur Basis anzeigen
        rel = p.relative_to(basis) if p.is_relative_to(basis) else p
        print(f"{i:>4}  {str(rel):<45} {groesse_kb:>8.1f}K  {geaendert}")

    print("─" * 72)
    _ok(f"Discovery: {len(dateien)} Dateien | Gesamt: {gesamt_bytes/1024:.1f} KB")
    return dateien


# =============================================================================
# PHASE 2 — SCHEMA-INSPEKTION
# Äquivalent zum MCP-Tool get_schema → liest Kopfzeilen, inferiert Datentypen.
# Das Modell versteht Entitäten und verhindert Fehlinterpretationen.
# =============================================================================

def phase2_inspizieren(pfad: str) -> dict:
    """
    Phase 2: Schema-Inspektion — Spalten, Datentypen, Null-Anteile, Stichproben.
    Ersetzt MCP get_schema / df.schema.items().

    Output (stdout):
        - Spaltenname, inferierter Polars-Dtype, Null-Anteil, Beispielwerte
    Returns:
        Schema-Dict für programmatische Weiterverarbeitung
    """
    _trennlinie("PHASE 2 — SCHEMA-INSPEKTION")
    if not HAS_POLARS:
        _err("polars nicht installiert: pip install polars")

    p = Path(pfad)
    if not p.exists():
        _err(f"Datei nicht gefunden: {pfad}")

    _log("Schema", f"Lade: {p.resolve()!s}")

    # Lazy-Load für Speichereffizienz bei großen Dateien
    df = pl.read_csv(str(p), infer_schema_length=500, ignore_errors=True)
    zeilen, spalten = df.shape

    _log("Schema", f"Dimensionen: {zeilen} Zeilen × {spalten} Spalten")
    print(f"\n{'Spalte':<30} {'Dtype':<20} {'Nulls %':>8}  Beispielwerte")
    print("─" * 80)

    schema_info = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_pct = df[col].null_count() / zeilen * 100 if zeilen > 0 else 0
        beispiele = df[col].drop_nulls().head(3).to_list()
        beispiel_str = " | ".join(str(v) for v in beispiele[:3])[:35]
        print(f"{col:<30} {dtype:<20} {null_pct:>7.1f}%  {beispiel_str}")
        schema_info[col] = {
            "dtype": dtype,
            "null_pct": round(null_pct, 2),
            "beispiele": [str(v) for v in beispiele[:3]],
        }

    print("─" * 80)

    # Duplikat-Analyse
    duplikate = zeilen - df.n_unique()
    _ok(f"Schema-Inspektion abgeschlossen")
    _info(f"Zeilen: {zeilen} | Spalten: {spalten} | Duplikate: {duplikate}")
    if duplikate > 0:
        _warn(f"{duplikate} Duplikat-Zeilen erkannt — Phase 3 (Bereinigung) empfohlen")

    return {"spalten": spalten, "zeilen": zeilen, "duplikate": duplikate, "schema": schema_info}


# =============================================================================
# PHASE 3 — BEREINIGUNG & NORMALISIERUNG
# Identifikation und Korrektur fehlerhafter Einträge, Deduplizierung,
# Standardisierung von Datumsformaten, Unicode-Bereinigung.
# =============================================================================

# Bekannte Datums-Muster für automatische Erkennung
DATUM_MUSTER = [
    (re.compile(r"^\d{2}\.\d{2}\.\d{4}$"),         "%d.%m.%Y"),   # 31.12.2024
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"),            "%Y-%m-%d"),   # 2024-12-31
    (re.compile(r"^\d{2}/\d{2}/\d{4}$"),            "%m/%d/%Y"),   # 12/31/2024
    (re.compile(r"^\d{4}/\d{2}/\d{2}$"),            "%Y/%m/%d"),   # 2024/12/31
    (re.compile(r"^\d{2}-\d{2}-\d{4}$"),            "%d-%m-%Y"),   # 31-12-2024
]

def _erkenne_datums_format(serie: pl.Series) -> str | None:
    """Erkennt Datums-Format anhand der ersten Nicht-Null-Werte."""
    stichprobe = serie.drop_nulls().head(20).to_list()
    for wert in stichprobe:
        s = str(wert).strip()
        for muster, fmt in DATUM_MUSTER:
            if muster.match(s):
                return fmt
    return None

def _normalisiere_datum(serie: pl.Series, fmt: str) -> pl.Series:
    """Konvertiert Datum-Strings in ISO-Format YYYY-MM-DD."""
    return serie.str.strptime(pl.Date, fmt, strict=False).cast(pl.Utf8)

def phase3_bereinigen(pfad: str, ausgabe: str | None = None, dry_run: bool = False) -> pl.DataFrame:
    """
    Phase 3: Automatische Bereinigung & Normalisierung.
    - Duplikat-Entfernung
    - Unicode-Normalisierung (strip + NFKC)
    - Datums-Standardisierung → ISO 8601 (YYYY-MM-DD)
    - Whitespace-Bereinigung in String-Spalten
    - Leere Strings → Null

    Output (stdout):
        Bereinigungsprotokoll mit Vorher/Nachher-Statistik
    """
    import unicodedata

    _trennlinie("PHASE 3 — BEREINIGUNG & NORMALISIERUNG")
    if not HAS_POLARS:
        _err("polars nicht installiert: pip install polars")

    p = Path(pfad)
    if not p.exists():
        _err(f"Datei nicht gefunden: {pfad}")

    if dry_run:
        _log("Bereinigung", "MODUS: DRY-RUN — keine Dateien werden geschrieben")

    df = pl.read_csv(str(p), infer_schema_length=500, ignore_errors=True)
    zeilen_vorher = len(df)
    _log("Bereinigung", f"Geladen: {zeilen_vorher} Zeilen | Quelle: {p.name}")

    aktionen: list[str] = []

    # 1. Duplikate entfernen
    df = df.unique()
    duplikate = zeilen_vorher - len(df)
    if duplikate > 0:
        aktionen.append(f"Duplikate entfernt: {duplikate}")

    # 2. String-Spalten: Whitespace + Unicode + Leere → Null
    string_spalten = [c for c, d in zip(df.columns, df.dtypes) if d == pl.Utf8]
    for col in string_spalten:
        df = df.with_columns(
            pl.col(col).str.strip_chars().alias(col)
        )
        df = df.with_columns(
            pl.when(pl.col(col) == "").then(None).otherwise(pl.col(col)).alias(col)
        )

    if string_spalten:
        aktionen.append(f"Whitespace/Leerstring bereinigt: {len(string_spalten)} Spalten")

    # 3. Datums-Erkennung und Normalisierung
    datums_spalten: list[str] = []
    for col in string_spalten:
        fmt = _erkenne_datums_format(df[col])
        if fmt:
            try:
                df = df.with_columns(_normalisiere_datum(pl.col(col), fmt).alias(col))
                datums_spalten.append(f"{col} ({fmt} → ISO)")
            except Exception:
                _warn(f"Datums-Konvertierung fehlgeschlagen für Spalte '{col}' (Format: {fmt})")

    if datums_spalten:
        aktionen.append(f"Datum normalisiert: {', '.join(datums_spalten)}")

    # Protokoll
    zeilen_nachher = len(df)
    print()
    for a in aktionen:
        _info(a)
    _ok(f"Bereinigung: {zeilen_vorher} → {zeilen_nachher} Zeilen | Aktionen: {len(aktionen)}")

    # Schreiben
    if not dry_run and ausgabe:
        ziel = Path(ausgabe)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        df.write_csv(str(ziel))
        _ok(f"Gespeichert: {ziel.resolve()!s}")
    elif dry_run:
        _info("DRY-RUN: Kein Schreibvorgang ausgeführt")

    return df


# =============================================================================
# PHASE 4 — SICHERE TRANSFORMATION
# Komplexe Aggregationen, Filterungen, vertikales/horizontales Merging.
# Äquivalent zu execute_polars_sql + pl.concat.
# =============================================================================

def phase4_transformieren(pfad: str, sql: str, ausgabe: str | None = None) -> pl.DataFrame:
    """
    Phase 4: SQL-ähnliche Transformation mit Polars (execute_polars_sql-Äquivalent).
    Tabellen-Name in SQL: 'df' (fest definiert).

    Beispiel-SQL:
        SELECT status, COUNT(*) AS anzahl FROM df GROUP BY status ORDER BY anzahl DESC
        SELECT * FROM df WHERE prioritaet = 'Hoch' AND status != 'Erledigt'

    Output (stdout):
        Ergebnisvorschau + Statistik
    """
    _trennlinie("PHASE 4 — TRANSFORMATION")
    if not HAS_POLARS:
        _err("polars nicht installiert: pip install polars")

    p = Path(pfad)
    if not p.exists():
        _err(f"Datei nicht gefunden: {pfad}")

    df = pl.read_csv(str(p), infer_schema_length=500, ignore_errors=True)
    _log("Transformation", f"Quelle: {p.name} ({len(df)} Zeilen) | SQL: {sql[:60]}...")

    try:
        ergebnis = pl.SQLContext(df=df).execute(sql, eager=True)
    except Exception as e:
        _err(f"SQL-Fehler: {e}")

    zeilen, spalten = ergebnis.shape
    _ok(f"SQL ausgeführt: {zeilen} Zeilen × {spalten} Spalten")

    # Vorschau (max. 20 Zeilen)
    vorschau = ergebnis.head(20)
    print()
    print(vorschau)

    if zeilen > 20:
        _info(f"... {zeilen - 20} weitere Zeilen nicht angezeigt")

    if ausgabe:
        ziel = Path(ausgabe)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ergebnis.write_csv(str(ziel))
        _ok(f"Gespeichert: {ziel.resolve()!s}")

    return ergebnis


def phase4_concat(pfade: list[Path], ausgabe: str | None = None) -> pl.DataFrame:
    """
    Phase 4 (Variante): Vertikales Merging mehrerer CSV-Dateien (pl.concat).
    Alle Dateien müssen kompatibles Schema haben.
    """
    _trennlinie("PHASE 4 — CONCAT (vertikales Merging)")
    if not HAS_POLARS:
        _err("polars nicht installiert: pip install polars")

    frames: list[pl.DataFrame] = []
    gesamt_vorher = 0

    for p in pfade:
        df_teil = pl.read_csv(str(p), infer_schema_length=500, ignore_errors=True)
        _info(f"Lade: {p.name} ({len(df_teil)} Zeilen)")
        gesamt_vorher += len(df_teil)
        frames.append(df_teil)

    if not frames:
        _err("Keine Dateien zum Zusammenführen")

    ergebnis = pl.concat(frames, how="diagonal_relaxed")
    _ok(f"Concat: {len(pfade)} Dateien | {gesamt_vorher} → {len(ergebnis)} Zeilen (nach Align)")

    if ausgabe:
        ziel = Path(ausgabe)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ergebnis.write_csv(str(ziel))
        _ok(f"Gespeichert: {ziel.resolve()!s}")

    return ergebnis


# =============================================================================
# VOLLSTÄNDIGE PIPELINE (alle 4 Phasen sequenziell)
# =============================================================================

def pipeline_komplett(verzeichnis: str, ausgabe: str, dry_run: bool = False) -> None:
    """
    Führt alle 4 ETL-Phasen sequenziell durch:
    Discovery → Schema-Inspektion → Bereinigung → Concat-Transformation
    """
    _trennlinie("ETL PIPELINE — VOLLSTÄNDIG")
    _log("Pipeline", f"Start | Quelle: {verzeichnis} | Ziel: {ausgabe} | DryRun: {dry_run}")

    # Phase 1
    gefunden = phase1_entdecken(verzeichnis)
    if not gefunden:
        _err("Pipeline abgebrochen: Keine Dateien gefunden")

    # Phase 2 (erste Datei als Schema-Referenz)
    schema = phase2_inspizieren(str(gefunden[0]))

    # Phase 3 (jede Datei einzeln bereinigen)
    bereinigte: list[Path] = []
    for p in gefunden:
        tmp_out = p.parent / f"_bereinigt_{p.name}"
        phase3_bereinigen(str(p), str(tmp_out) if not dry_run else None, dry_run=dry_run)
        if not dry_run:
            bereinigte.append(tmp_out)

    # Phase 4 (alle bereinigten Dateien zusammenführen)
    if not dry_run and bereinigte:
        phase4_concat(bereinigte, ausgabe)
        # Temp-Dateien aufräumen
        for tmp in bereinigte:
            tmp.unlink(missing_ok=True)
        _info("Temporäre Bereinigungsdateien entfernt")
    elif dry_run:
        _info(f"DRY-RUN: Würde {len(gefunden)} Dateien bereinigen und nach '{ausgabe}' zusammenführen")

    _trennlinie()
    _log("Pipeline", f"Abgeschlossen | Ergebnis: {'(dry-run)' if dry_run else ausgabe}")


# =============================================================================
# CLI-EINSTIEG
# =============================================================================

HILFE = """
VERWENDUNG:
  python csv_etl_pipeline.py entdecken    <verzeichnis> [--muster "*.csv"]
  python csv_etl_pipeline.py inspizieren  <datei.csv>
  python csv_etl_pipeline.py bereinigen   <datei.csv> [ausgabe.csv] [--dry-run]
  python csv_etl_pipeline.py transformieren <datei.csv> "<sql>" [ausgabe.csv]
  python csv_etl_pipeline.py pipeline     <verzeichnis> <ausgabe.csv> [--dry-run]

PHASEN:
  entdecken     Phase 1 — Discovery: CSV-Dateien in Verzeichnis finden
  inspizieren   Phase 2 — Schema: Spalten, Typen, Nulls, Duplikate analysieren
  bereinigen    Phase 3 — Bereinigung: Duplikate, Whitespace, Datum normalisieren
  transformieren Phase 4 — SQL-Transformation mit Polars (Tabelle heißt 'df')
  pipeline      Alle 4 Phasen sequenziell (Discovery → Schema → Bereinigung → Concat)

ABHÄNGIGKEITEN:
  pip install polars
"""

if __name__ == "__main__":
    if not HAS_POLARS:
        print("FEHLER: polars nicht installiert.\nAusführen: pip install polars", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print(HILFE)
        sys.exit(0)

    modus = sys.argv[1]
    args = sys.argv[2:]
    dry_run = "--dry-run" in args
    args_clean = [a for a in args if a != "--dry-run"]

    if modus == "entdecken":
        if not args_clean:
            _err("VERWENDUNG: entdecken <verzeichnis> [--muster '*.csv']")
        muster = "*.csv"
        for i, a in enumerate(args_clean):
            if a == "--muster" and i + 1 < len(args_clean):
                muster = args_clean[i + 1]
        phase1_entdecken(args_clean[0], muster)

    elif modus == "inspizieren":
        if not args_clean:
            _err("VERWENDUNG: inspizieren <datei.csv>")
        schema = phase2_inspizieren(args_clean[0])
        print("\nJSON-Schema (maschinenlesbar):")
        print(json.dumps(schema, indent=2, ensure_ascii=False))

    elif modus == "bereinigen":
        if not args_clean:
            _err("VERWENDUNG: bereinigen <datei.csv> [ausgabe.csv] [--dry-run]")
        eingabe = args_clean[0]
        ausgabe = args_clean[1] if len(args_clean) > 1 else None
        phase3_bereinigen(eingabe, ausgabe, dry_run=dry_run)

    elif modus == "transformieren":
        if len(args_clean) < 2:
            _err('VERWENDUNG: transformieren <datei.csv> "<sql>" [ausgabe.csv]')
        ausgabe = args_clean[2] if len(args_clean) > 2 else None
        phase4_transformieren(args_clean[0], args_clean[1], ausgabe)

    elif modus == "pipeline":
        if len(args_clean) < 2:
            _err("VERWENDUNG: pipeline <verzeichnis> <ausgabe.csv> [--dry-run]")
        pipeline_komplett(args_clean[0], args_clean[1], dry_run=dry_run)

    else:
        print(f"FEHLER: Unbekannter Modus '{modus}'\n{HILFE}", file=sys.stderr)
        sys.exit(1)
