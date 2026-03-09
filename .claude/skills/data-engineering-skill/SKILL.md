---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: data-engineering-skill
description: >
  Speichereffiziente, spaltenbasierte Formate (Parquet, Arrow) für große Datensätze,
  pyarrow/fastparquet für Partitionierung und Schema-Enforcement,
  kein CSV über 100.000 Zeilen, performante Datenpipelines für Server-Anwendungen.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Data Engineering & Performante Speicherformate
    description: >
      Speichereffiziente, spaltenbasierte Formate (Parquet, Arrow) für große Datensätze,
      pyarrow/fastparquet für Partitionierung und Schema-Enforcement,
      kein CSV über 100.000 Zeilen, performante Datenpipelines für Server-Anwendungen

triggers:
  # Data Engineering & Performante Speicherformate
  - Große Datensätze (>100.000 Zeilen) in Parquet statt CSV speichern
  - pyarrow oder fastparquet für Parquet-Lesen/-Schreiben einsetzen
  - Datensatz nach Spalte oder Zeitraum partitionieren (Hive-Partitionierung)
  - Schema-Enforcement für Parquet-Dateien definieren und validieren
  - Apache Arrow In-Memory-Format für Zero-Copy-Operationen nutzen
  - Performante Datenpipeline für Server-Anwendungen konzipieren
  - Speicherverbrauch bei Datenverarbeitung optimieren
  - Lese-/Schreibzugriffe auf großen Datensätzen beschleunigen
  - CSV-Pipeline auf Parquet migrieren (Drop-in-Replacement)

resources: []
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

## Data Engineering & Performante Speicherformate

Für die Verarbeitung großer Datensätze bist du angewiesen, speichereffiziente, spaltenbasierte Formate wie Parquet zu nutzen. Nutze `pyarrow` oder `fastparquet` für Partitionierung und Schema-Enforcement. Vermeide den Einsatz von regulären CSV-Dateien bei Datensätzen über 100.000 Zeilen und baue stattdessen performante Datenpipelines.

**Erwartetes Verhalten:** Der Agent konzipiert Pipelines, die den Arbeitsspeicher schonen und Lese-/Schreibzugriffe bei Server-Anwendungen drastisch beschleunigen.

---

### Format-Entscheidungsbaum

```
Datensatzgröße?
    └── < 10.000 Zeilen     → CSV (einfach, portabel)
    └── 10.000–100.000      → CSV mit explizitem dtype-Cast (pandas/polars)
    └── > 100.000 Zeilen    → Parquet (pflicht)
        └── Schreib-Last?
                └── Ja      → pyarrow.parquet (schnellster Writer)
                └── Nein    → fastparquet (geringerer Speicher-Overhead)
        └── Partitionierung nötig?
                └── Ja      → Hive-Partitionierung (partition_cols=[...])
                └── Nein    → Single-File Parquet
```

---

### Pflicht-Muster: Parquet schreiben und lesen

```python
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.dataset as ds
from pathlib import Path

# Schema explizit definieren — kein Schema-Drift
SCHEMA = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("event_ts", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("amount", pa.float64()),
    pa.field("category", pa.dictionary(pa.int8(), pa.utf8())),  # Enum-Spalte
])

def write_partitioned(table: pa.Table, output_dir: Path) -> None:
    """Schreibt Arrow-Tabelle als Hive-partitioniertes Parquet-Dataset.

    Args:
        table: Validierte Arrow-Tabelle (Schema geprüft).
        output_dir: Zielverzeichnis (wird angelegt falls nicht vorhanden).
    """
    pq.write_to_dataset(
        table,
        root_path=str(output_dir),
        partition_cols=["category"],
        schema=SCHEMA,
        compression="zstd",          # Beste Ratio/Speed-Balance
        use_dictionary=True,
        row_group_size=100_000,
    )

def read_filtered(data_dir: Path, category: str) -> pa.Table:
    """Liest nur relevante Partitionen (Predicate Pushdown).

    Args:
        data_dir: Parquet-Dataset-Verzeichnis.
        category: Filterwert für Partition-Column.

    Returns:
        Gefilterte Arrow-Tabelle.
    """
    dataset = ds.dataset(str(data_dir), format="parquet", partitioning="hive")
    return dataset.to_table(
        filter=ds.field("category") == category,
        columns=["id", "event_ts", "amount"],  # Column Pruning
    )
```

---

### Kennzahlen-Vergleich

| Format | 1M Zeilen schreiben | 1M Zeilen lesen | Speicher auf Disk |
|---|---|---|---|
| CSV (unkomprimiert) | ~2,1 s | ~1,8 s | ~120 MB |
| CSV (gzip) | ~4,5 s | ~3,2 s | ~28 MB |
| Parquet (snappy) | ~0,4 s | ~0,2 s | ~22 MB |
| Parquet (zstd) | ~0,5 s | ~0,2 s | ~18 MB |

**Faustregel:** Parquet + zstd = 6× kleiner als CSV, 9× schneller beim Lesen.

---

### Sicherheitsregeln für Parquet-Pipelines

- **Schema immer explizit** — nie `infer_schema=True` in Produktion
- **Partitions-Tiefe max. 3** — tiefere Hive-Bäume erhöhen Metadaten-Overhead
- **Row Group Size**: 50.000–200.000 Zeilen (zu klein = viele Seeks, zu groß = RAM-Druck)
- **Compression**: `zstd` bevorzugen (besser als `snappy` bei Archiv-Daten)
- **Kein `overwrite=True`** ohne explizite Nutzerfreigabe

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
| (keine spezifischen Ressourcen) | — | Data Engineering | Instruktionen vollständig in LADESTUFE 2 |
