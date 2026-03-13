# Shell-Scripting und CSS — Detailreferenz

## Shell-Skripte — Pflichtstruktur

Jedes generierte Skript muss diese Struktur haben:

```bash
#!/usr/bin/env bash
# BESCHREIBUNG: Kurze Erläuterung des Zwecks
# VERWENDUNG:   ./script.sh [optionen] arg1 arg2
# VERSION:      1.0.0

set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# Hilfsfunktionen
die()     { echo "[FEHLER] $*" >&2; exit 1; }
log()     { echo "[INFO]  $*"; }
confirm() { read -rp "$1 [y/N] " ans; [[ "$ans" =~ ^[Yy]$ ]]; }
usage()   { echo "Verwendung: $SCRIPT_NAME [optionen]"; exit 0; }

# Argument-Prüfung
[[ $# -lt 1 ]] && usage

main() {
    # Hauptlogik hier
    log "Starte $SCRIPT_NAME"
}

main "$@"
```

Vollständige Vorlage: `resources/shell_template.sh`

## Temp-File-Pattern (sicher)

```bash
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

# tmp verwenden...
some_command > "$tmp"
```

## Argument-Parsing-Pattern

```bash
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)    usage ;;
        -v|--verbose) VERBOSE=1; shift ;;
        -o|--output)  OUTPUT="$2"; shift 2 ;;
        --)           shift; break ;;
        -*)           die "Unbekannte Option: $1" ;;
        *)            break ;;
    esac
done
```

## Sicherheits-Checkliste für Shell-Skripte

- `set -euo pipefail` — Sofortiger Exit bei Fehler, ungesetzten Variablen, Pipeline-Fehlern
- `IFS=$'\n\t'` — Verhindert Wordsplitting bei Leerzeichen
- Alle Variablen quoten: `"$var"` statt `$var`
- Arrays für Befehle mit Argumenten: `cmd=("git" "commit" "-m" "$msg")` → `"${cmd[@]}"`
- Keine `eval` ohne explizite Notwendigkeit
- Eingabe-Validierung vor Dateioperationen

---

## CSS — Regeln und Konventionen

**Namenskonvention**: BEM (`block__element--modifier`)

```css
/* Korrekt: BEM */
.tabelle { }
.tabelle__kopf { }
.tabelle__zelle--hervorgehoben { }

/* Falsch: Kein BEM */
.tabelle .kopf .hervorgehoben { }
```

**Keine Inline-Styles** in generierten HTML-Dateien.

**Tabellen-Grundstil**: `resources/tabellen.css`

### Status-Badge-Pattern (BEM)

```css
.badge { display: inline-block; padding: 2px 8px; border-radius: 3px; }
.badge--offen    { background: #FFE699; }
.badge--aktiv    { background: #9DC3E6; }
.badge--erledigt { background: #A9D18E; }
.badge--blockiert{ background: #FF7C80; }
```

## Visuelle Aufbereitung

| Darstellungsform | Wann verwenden |
|-----------------|----------------|
| Markdown-Tabelle mit Bewertungsspalte | Vergleiche und Entscheidungen |
| Baumdarstellung mit `├──` / `└──` | Projektstrukturen, Verzeichnisse |
| Nummerierte Schrittliste | Prozesse mit Entscheidungspunkten |
| Mermaid-Flowchart | Komplexe Entscheidungsbäume |
