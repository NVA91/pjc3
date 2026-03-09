#!/usr/bin/env bash
# LADESTUFE 3 — RESSOURCE
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: Sichere, wiederholbare Bash-Skript-Vorlage.
#               Alle Sicherheitsregeln aus SKILL.md sind bereits eingebaut.
# VERWENDUNG:   ./shell_template.sh [--dry-run] <eingabe-datei>
# VERSION:      1.0.0
# IDEMPOTENZ:   Ja — mehrfaches Ausführen ohne Schaden möglich

# =============================================================================
# SICHERHEITS-SET (Pflicht — erste ausführbare Zeile, niemals entfernen)
# =============================================================================
set -euo pipefail          # -e: Exit bei Fehler | -u: Exit bei ungesetzter Var | -o pipefail: Pipe-Fehler propagieren
IFS=$'\n\t'                # Kein Wordsplitting durch Leerzeichen

# =============================================================================
# KONSTANTEN (readonly — verhindert versehentliche Überschreibung)
# =============================================================================
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"
readonly TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"

# Konfigurierbare Pfade — KEINE hardcodierten absoluten Pfade außer /tmp
readonly LOG_DIR="${LOG_DIR:-/tmp/${SCRIPT_NAME%.sh}_logs}"
readonly DRY_RUN="${DRY_RUN:-false}"

# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

# Fehler nach stderr, dann Exit
die() {
    echo "FEHLER [${SCRIPT_NAME}]: $*" >&2
    exit 1
}

# Strukturiertes Logging mit Timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Warnung (kein Exit)
warn() {
    echo "WARNUNG [${SCRIPT_NAME}]: $*" >&2
}

# Nutzereingabe vor destruktiven Aktionen einholen
confirm() {
    local prompt="${1:-Fortfahren?}"
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "DRY-RUN: Würde fragen: $prompt [Übersprungen]"
        return 0
    fi
    read -r -p "$prompt [j/N] " antwort
    [[ "${antwort,,}" == "j" ]] || { echo "Abgebrochen."; exit 0; }
}

# Hilfeanzeige aus Kommentaren extrahieren
usage() {
    grep '^# VERWENDUNG:' "${BASH_SOURCE[0]}" | sed 's/^# VERWENDUNG:\s*//'
    echo ""
    grep '^# BESCHREIBUNG:' "${BASH_SOURCE[0]}" | sed 's/^# BESCHREIBUNG:\s*//'
    exit 0
}

# Sicheres Temp-File mit automatischer Bereinigung
make_temp() {
    local tmp
    tmp="$(mktemp)" || die "Konnte kein Temp-File erstellen"
    trap 'rm -f '"$tmp"'' EXIT
    echo "$tmp"
}

# =============================================================================
# ARGUMENT-PARSING
# =============================================================================
parse_args() {
    local -n _dry_run_ref=$1
    local -n _input_ref=$2
    shift 2

    _dry_run_ref=false
    _input_ref=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                _dry_run_ref=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            -*)
                die "Unbekannte Option: $1"
                ;;
            *)
                if [[ -z "$_input_ref" ]]; then
                    _input_ref="$1"
                else
                    die "Zu viele Argumente: $1"
                fi
                shift
                ;;
        esac
    done

    [[ -n "$_input_ref" ]] || { usage; }
}

# =============================================================================
# VALIDIERUNGEN
# =============================================================================
validate_input() {
    local datei="$1"

    [[ -e "$datei" ]] || die "Pfad existiert nicht: $datei"
    [[ -f "$datei" ]] || die "Kein reguläres File: $datei"
    [[ -r "$datei" ]] || die "Keine Leserechte: $datei"

    # Traversal-Schutz: Keine relativen Pfad-Sprünge
    [[ "$datei" != *".."* ]] || die "Pfad-Traversal nicht erlaubt: $datei"
}

# =============================================================================
# HAUPTLOGIK
# =============================================================================
verarbeite_datei() {
    local eingabe="$1"
    local dry_run="$2"

    log "Starte Verarbeitung: $eingabe"

    if [[ "$dry_run" == "true" ]]; then
        log "DRY-RUN: Würde verarbeiten → $(wc -l < "$eingabe") Zeilen"
        return 0
    fi

    # Beispiel-Verarbeitung (anpassen):
    local tmp
    tmp="$(make_temp)"

    # --- Hier eigene Logik einfügen ---
    # Beispiel: Zeilen mit "ERROR" herausfiltern
    grep -i "error" "$eingabe" > "$tmp" || true
    local treffer
    treffer="$(wc -l < "$tmp")"

    log "Fertig. $treffer Treffer gefunden."

    # Schreibende Operation: Bestätigung einholen
    local ausgabe="${eingabe%.txt}_result_${TIMESTAMP}.txt"
    confirm "Ergebnis speichern unter: $ausgabe"
    cp "$tmp" "$ausgabe"
    log "Gespeichert: $ausgabe"
}

# =============================================================================
# MAIN (Einstiegspunkt — immer als Funktion, immer letzter Aufruf)
# =============================================================================
main() {
    local dry_run
    local eingabe

    parse_args dry_run eingabe "$@"
    validate_input "$eingabe"

    mkdir -p "$LOG_DIR"

    if [[ "$dry_run" == "true" ]]; then
        log "Modus: DRY-RUN — keine Dateien werden verändert"
    fi

    verarbeite_datei "$eingabe" "$dry_run"
    log "Skript erfolgreich abgeschlossen."
}

main "$@"
