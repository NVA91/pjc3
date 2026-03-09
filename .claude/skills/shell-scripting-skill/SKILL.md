# Skill: shell-scripting-skill

## Zweck
Sichere, strukturierte und wiederholbare Shell-Skripte sowie strukturierte Arbeit mit Office-Dateien (CSV, Excel, CSS) und Tabellen zur Aufgabenverwaltung.

---

## Trigger-Bedingungen

Verwende diesen Skill, wenn der Nutzer:
- Shell-Skripte erstellen oder überarbeiten möchte
- Bash-/Zsh-Automatisierungen plant
- CSV-Dateien lesen, schreiben oder verarbeiten will
- Excel-Tabellen (.xlsx) für Aufgabenverwaltung oder Datenspeicherung benötigt
- CSS-Dateien strukturieren oder bearbeiten will
- Komplexe Themen in Tabellen- oder Strukturform aufbereiten möchte
- Explizit `/shell-scripting-skill` aufruft

---

## Kernkompetenzen

### 1. Sichere Shell-Skript-Programmierung

**Grundregeln — immer anwenden:**

```bash
#!/usr/bin/env bash
set -euo pipefail          # Sofortiger Abbruch bei Fehler, ungesetzten Variablen, Pipe-Fehlern
IFS=$'\n\t'                # Sichere Feld-Trennung (kein Wordsplitting durch Leerzeichen)
```

**Sicherheits-Checkliste für jedes Skript:**

| Prüfpunkt | Beschreibung | Beispiel |
|---|---|---|
| `set -euo pipefail` | Fehler-Exit + undefinierte Vars abfangen | Immer erste Zeile nach Shebang |
| Variablen quoten | Verhindert Wordsplitting und Globbing | `"$var"` statt `$var` |
| Pfade validieren | Existenz prüfen bevor Zugriff | `[[ -f "$file" ]] \|\| die "Datei nicht gefunden"` |
| Keine `rm -rf` ohne Guard | Niemals ohne Bestätigung löschen | Nutze Trash oder `--dry-run` |
| Temp-Files sicher erstellen | Kein vorhersagbarer Dateiname | `tmpfile=$(mktemp)` |
| Cleanup-Trap | Temp-Files bei Exit entfernen | `trap 'rm -f "$tmpfile"' EXIT` |
| Readonly für Konstanten | Verhindert versehentliche Überschreibung | `readonly CONFIG_FILE="/etc/app.conf"` |
| Eingaben sanitisieren | Kein Shell-Injection | Validiere Nutzereingaben mit Regex |

**Standardstruktur eines sicheren Skripts:**

```bash
#!/usr/bin/env bash
# BESCHREIBUNG: Was macht dieses Skript?
# VERWENDUNG:   ./skript.sh [optionen] <argument>
# AUTOR:        Name
# VERSION:      1.0.0

set -euo pipefail
IFS=$'\n\t'

# --- Konstanten ---
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# --- Hilfsfunktionen ---
die() { echo "FEHLER: $*" >&2; exit 1; }
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
usage() { grep '^# VERWENDUNG:' "$0" | sed 's/# VERWENDUNG:\s*//' ; exit 0; }

# --- Argumente prüfen ---
[[ $# -lt 1 ]] && usage

# --- Hauptlogik ---
main() {
    local input_file="$1"
    [[ -f "$input_file" ]] || die "Datei nicht gefunden: $input_file"
    log "Verarbeite: $input_file"
    # ... Logik hier
}

main "$@"
```

---

### 2. Keine unautorisierten Datei-Operationen

**Pflichtregeln — niemals verletzen:**

- Kein Öffnen, Lesen oder Schreiben von Dateien/Verzeichnissen ohne explizite Nutzerfreigabe
- Vor jeder Dateiänderung: Nutzerpfad anzeigen und Bestätigung einholen
- Trockenlauf (`--dry-run`) als Standard für destruktive Operationen
- Pfade immer relativ oder konfigurierbar — keine hardcodierten absoluten Pfade außer `/tmp`

**Bestätigungs-Pattern:**

```bash
confirm() {
    local prompt="${1:-Fortfahren?}"
    read -r -p "$prompt [j/N] " answer
    [[ "${answer,,}" == "j" ]] || { echo "Abgebrochen."; exit 0; }
}

# Verwendung vor destruktiven Aktionen:
confirm "Datei '$target' wird überschrieben. Fortfahren?"
```

---

### 3. CSV-Verarbeitung

**Shell-basiert (kein Python nötig):**

```bash
# CSV lesen (mit Header-Zeile überspringen)
tail -n +2 daten.csv | while IFS=',' read -r spalte1 spalte2 spalte3; do
    echo "Wert 1: $spalte1, Wert 2: $spalte2"
done

# CSV mit awk filtern (Spalte 2 > 100)
awk -F',' 'NR>1 && $2 > 100 { print $0 }' daten.csv

# CSV-Spalten extrahieren
cut -d',' -f1,3 daten.csv > ausgabe.csv

# CSV sortieren nach Spalte 2
(head -1 daten.csv; tail -n +2 daten.csv | sort -t',' -k2,2n) > sortiert.csv
```

**Python-basiert (für komplexe CSV-Operationen):**

```python
import csv
from pathlib import Path

def lese_csv(pfad: str) -> list[dict]:
    """Liest CSV sicher als Liste von Dicts."""
    datei = Path(pfad)
    if not datei.exists():
        raise FileNotFoundError(f"CSV nicht gefunden: {pfad}")
    with datei.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def schreibe_csv(daten: list[dict], pfad: str, felder: list[str]) -> None:
    """Schreibt Liste von Dicts als CSV."""
    with open(pfad, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=felder)
        writer.writeheader()
        writer.writerows(daten)
```

---

### 4. Excel-Tabellen (xlsx) — Aufgabenverwaltung

**Bibliothek:** `openpyxl` (pip install openpyxl)

**Aufgaben-Tabelle erstellen:**

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import date

def erstelle_aufgaben_tabelle(ausgabe_pfad: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Aufgaben"

    # Header definieren
    headers = ["ID", "Aufgabe", "Priorität", "Status", "Fällig am", "Verantwortlich", "Notizen"]
    header_breiten = [5, 40, 12, 15, 12, 20, 30]

    # Header-Stil
    header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # Header schreiben
    for col, (header, breite) in enumerate(zip(headers, header_breiten), 1):
        zelle = ws.cell(row=1, column=col, value=header)
        zelle.fill = header_fill
        zelle.font = header_font
        zelle.alignment = Alignment(horizontal='center', vertical='center')
        zelle.border = thin_border
        ws.column_dimensions[get_column_letter(col)].width = breite

    # Beispiel-Daten
    aufgaben = [
        [1, "Projektplan erstellen", "Hoch", "Offen", date.today(), "Max M.", ""],
        [2, "README schreiben", "Mittel", "In Arbeit", date.today(), "Anna L.", "Entwurf vorhanden"],
    ]

    # Status-Farben
    status_farben = {
        "Offen": "FFE699",
        "In Arbeit": "9DC3E6",
        "Erledigt": "A9D18E",
        "Blockiert": "FF7C80",
    }

    for row_idx, aufgabe in enumerate(aufgaben, 2):
        for col_idx, wert in enumerate(aufgabe, 1):
            zelle = ws.cell(row=row_idx, column=col_idx, value=wert)
            zelle.border = thin_border
            zelle.alignment = Alignment(vertical='center', wrap_text=True)
        # Status-Zelle einfärben
        status = aufgabe[3]
        if status in status_farben:
            ws.cell(row=row_idx, column=4).fill = PatternFill(
                start_color=status_farben[status],
                end_color=status_farben[status],
                fill_type="solid"
            )

    ws.freeze_panes = "A2"  # Header einfrieren
    ws.auto_filter.ref = ws.dimensions

    wb.save(ausgabe_pfad)
    print(f"Tabelle gespeichert: {ausgabe_pfad}")
```

---

### 5. CSS — Strukturiertes Arbeiten

**Namenskonventionen (BEM):**

```css
/* Block */
.aufgaben-liste { }

/* Element */
.aufgaben-liste__eintrag { }

/* Modifier */
.aufgaben-liste__eintrag--erledigt { }
.aufgaben-liste__eintrag--dringend { }
```

**Strukturvorlage für Tabellen-CSS:**

```css
/* === TABELLEN-STYLING === */
.daten-tabelle {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 0.875rem;
}

.daten-tabelle thead th {
    background-color: #2f5496;
    color: #ffffff;
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    border: 1px solid #1e3a6b;
}

.daten-tabelle tbody tr:nth-child(even) {
    background-color: #f5f7fa;
}

.daten-tabelle tbody tr:hover {
    background-color: #dbe8f6;
    transition: background-color 0.15s ease;
}

.daten-tabelle td {
    padding: 0.625rem 1rem;
    border: 1px solid #d1d9e6;
    vertical-align: top;
}

/* Status-Badges */
.status-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-badge--offen     { background: #fff3cd; color: #856404; }
.status-badge--in-arbeit { background: #cfe2ff; color: #084298; }
.status-badge--erledigt  { background: #d1e7dd; color: #0a3622; }
.status-badge--blockiert { background: #f8d7da; color: #842029; }
```

---

### 6. Visuelle Aufbereitung komplexer Themen

**Tabellen-Template für Vergleiche / Entscheidungsmatrizen:**

```markdown
| Kriterium       | Option A | Option B | Option C | Empfehlung |
|-----------------|----------|----------|----------|------------|
| Sicherheit      | ✅ Hoch   | ⚠️ Mittel | ❌ Niedrig | A          |
| Aufwand         | ⚠️ Mittel | ✅ Gering | ✅ Gering  | B/C        |
| Wartbarkeit     | ✅ Gut    | ⚠️ Ok     | ❌ Schlecht| A          |
| Kosten          | 💰💰      | 💰        | 💰        | B/C        |
| **Gesamt**      | **2. Wahl** | **1. Wahl** | **3. Wahl** | **B** |
```

**Strukturbaum für Projekte:**

```
projekt/
├── src/            # Quellcode
│   ├── scripts/    # Shell-Skripte
│   └── lib/        # Hilfsfunktionen
├── data/
│   ├── input/      # Rohdaten (read-only)
│   └── output/     # Ergebnisse
├── docs/           # Dokumentation
└── tests/          # Tests
```

---

## Arbeitsweise dieses Skills

1. **Erst verstehen**: Anforderungen klären bevor Code geschrieben wird
2. **Sicherheit zuerst**: Jedes Skript bekommt `set -euo pipefail` + Eingabevalidierung
3. **Keine Überraschungen**: Pfade und Aktionen werden vor Ausführung angezeigt
4. **Dry-Run als Standard**: Destruktive Operationen zuerst simulieren
5. **Dokumentation inline**: `# BESCHREIBUNG`, `# VERWENDUNG` direkt im Skript
6. **Idempotenz anstreben**: Skripte sollen mehrfach ausführbar sein ohne Schaden

---

## Verwandte Skills / Ressourcen

- Docker-Sicherheit → siehe `CLAUDE.md` (Abschnitte: Immutable Config, Volume Mounts, UID-Isolation)
- MCP-Integration → `@.claude/skills/n8n-workflow-manager/SKILL.md`
- Python-Abhängigkeiten für Excel: `pip install openpyxl` (in `requirements.txt` ergänzen)
- Python-Abhängigkeiten für CSV: Standardbibliothek (`csv`-Modul, kein Install nötig)
