#!/bin/bash
# safe-project-exec.sh — Harte Guard-Regeln für Host-Befehle im Projekt
#
# Ziel:
# - Keine Path-Hopping/Traversal-Angriffe
# - Keine Shell-Operatoren oder Command-Chaining
# - Nur explizit erlaubte, read-only Befehle
# - grep nur auf konkreten Dateien (kein rekursives/weites Suchen)

set -euo pipefail

readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ALLOWED_COMMANDS=("ls" "cat" "head" "tail" "grep" "awk" "sed")
readonly ALLOWED_GREP_FLAGS=("-i" "-n" "-c" "-v" "-w" "-x" "-e")

fail() {
    echo "❌ $1" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Verwendung:
  bash safe-project-exec.sh <command> [args...]

Beispiele:
  bash safe-project-exec.sh ls -la ./docs
  bash safe-project-exec.sh cat ./README.md
  bash safe-project-exec.sh grep TODO ./README.md

Harte Regeln:
  - Nur Befehle aus Whitelist (read-only)
  - Kein ".." (Path Traversal)
  - Keine Shell-Operatoren (;, &&, ||, |, >, <, $(), `...`)
  - grep nur auf expliziten Dateien, nie rekursiv/weit
EOF
}

is_allowed_command() {
    local cmd="$1"
    for allowed in "${ALLOWED_COMMANDS[@]}"; do
        if [[ "$cmd" == "$allowed" ]]; then
            return 0
        fi
    done
    return 1
}

is_flag() {
    [[ "$1" == -* ]]
}

is_allowed_grep_flag() {
    local candidate="$1"
    local allowed
    for allowed in "${ALLOWED_GREP_FLAGS[@]}"; do
        if [[ "$candidate" == "$allowed" ]]; then
            return 0
        fi
    done
    return 1
}

normalize_path() {
    local input="$1"
    if [[ "$input" == /* ]]; then
        realpath -m "$input"
    else
        realpath -m "$PROJECT_ROOT/$input"
    fi
}

assert_within_project() {
    local original="$1"
    local normalized
    normalized="$(normalize_path "$original")"

    if [[ "$normalized" != "$PROJECT_ROOT" && "$normalized" != "$PROJECT_ROOT"/* ]]; then
        fail "Pfad außerhalb des Projekts verboten: $original"
    fi
}

assert_file_in_project() {
    local target="$1"
    local normalized
    normalized="$(normalize_path "$target")"

    assert_within_project "$target"

    if [[ ! -e "$normalized" ]]; then
        fail "Datei nicht gefunden: $target"
    fi

    if [[ ! -f "$normalized" ]]; then
        fail "Nur Dateien erlaubt (kein Verzeichnis): $target"
    fi
}

validate_token_safety() {
    local token="$1"

    if [[ "$token" == *".."* ]]; then
        fail "Path Traversal erkannt (..): $token"
    fi

    if [[ "$token" == *";"* ]] || [[ "$token" == *"|"* ]] || [[ "$token" == *"&"* ]] || \
       [[ "$token" == *">"* ]] || [[ "$token" == *"<"* ]] || [[ "$token" == *\`* ]] || \
       [[ "$token" == *'$('* ]]; then
        fail "Shell-Operatoren oder Subshells sind verboten: $token"
    fi
}

validate_generic_paths() {
    local cmd="$1"
    shift
    local arg
    local saw_path=false

    for arg in "$@"; do
        if is_flag "$arg"; then
            continue
        fi

        # Für awk/sed kann das erste non-flag Argument ein Programm sein.
        # Pfadprüfung erfolgt dort in der spezialisierten Validierung.
        if [[ "$cmd" == "awk" || "$cmd" == "sed" ]]; then
            saw_path=true
            break
        fi

        assert_within_project "$arg"
        saw_path=true
    done

    if [[ "$saw_path" == false && "$cmd" != "ls" ]]; then
        fail "Mindestens ein Zielpfad erforderlich"
    fi
}

validate_awk_or_sed() {
    local cmd="$1"
    shift
    local non_flag_count=0
    local arg
    local file_candidates=()

    for arg in "$@"; do
        # Sicherheitsaspekt: -f/--file lädt externen Code aus Datei.
        # Zusätzlich blocken wir -F, weil Flag-Semantik je Tool variieren kann
        # und diese Option in Reports als Missbrauchspfad markiert wurde.
        if [[ "$arg" == "-f" || "$arg" == "--file" || "$arg" == "-F" ]]; then
            fail "$cmd: Flag $arg ist nicht erlaubt (verhindert File-as-Program)"
        fi
        if [[ "$arg" == -f* || "$arg" == -F* || "$arg" == --file=* ]]; then
            fail "$cmd: Flag $arg ist nicht erlaubt (verhindert File-as-Program)"
        fi

        if is_flag "$arg"; then
            continue
        fi
        non_flag_count=$((non_flag_count + 1))
        file_candidates+=("$arg")
    done

    if [[ "$non_flag_count" -lt 2 ]]; then
        fail "$cmd benötigt ein Skript und mindestens eine Datei"
    fi

    # Programm-String (index 0) auf gefährliche Befehle prüfen.
    # sed: e (execute), r/R (read file), w/W (write file) ermöglichen RCE bzw. Path-Bypass.
    # awk: system(), getline, cmd|getline ermöglichen RCE bzw. beliebige Datei-Lese.
    local program_string="${file_candidates[0]}"
    if [[ "$cmd" == "sed" ]]; then
        # Python-Validator: entfernt s/.../.../ und /regex/-Adress-Tokens, prüft dann
        # ob gefährliche Befehle e(xecute), r/R(ead), w/W(rite) im Rest verbleiben.
        # Bash-Regex reicht hier nicht aus (schlägt fehl bei Adressen wie "1e cmd").
        local _sed_check
        _sed_check=$(python3 -c "
import sys, re
prog = sys.stdin.read().rstrip()
cleaned = re.sub(r's/[^/]*/[^/]*/[gGpPiImMqQ]*', '', prog)
cleaned = re.sub(r'/[^/]*/', '', cleaned)
print('SAFE' if not re.search('[eErRwW]', cleaned) else 'UNSAFE')
" <<< "$program_string" 2>/dev/null)
        if [[ "$_sed_check" != "SAFE" ]]; then
            fail "sed: Gefährliche Befehle (e/r/R/w/W) im Programm-String verboten"
        fi
    fi
    if [[ "$cmd" == "awk" ]]; then
        if [[ "$program_string" =~ system[[:space:]]*\( ]] || \
           [[ "$program_string" =~ getline ]] || \
           [[ "$program_string" =~ \|[[:space:]]*\"  ]] || \
           [[ "$program_string" =~ \"[[:space:]]*\| ]]; then
            fail "awk: Gefährliche Funktionen (system/getline/pipe) im Programm-String verboten"
        fi
    fi

    local index=0
    for arg in "${file_candidates[@]}"; do
        if [[ "$index" -eq 0 ]]; then
            index=$((index + 1))
            continue
        fi
        assert_file_in_project "$arg"
        index=$((index + 1))
    done
}

validate_grep() {
    shift
    local args=("$@")
    local non_flag_count=0
    local arg
    local file_candidates=()

    for arg in "${args[@]}"; do
        if [[ "$arg" == "-r" || "$arg" == "-R" || "$arg" == "--recursive" ]]; then
            fail "Weite/rekursive grep-Suche ist verboten ($arg)"
        fi
        if is_flag "$arg"; then
            if ! is_allowed_grep_flag "$arg"; then
                fail "grep-Flag nicht erlaubt: $arg"
            fi
            continue
        fi
        non_flag_count=$((non_flag_count + 1))
        file_candidates+=("$arg")
    done

    if [[ "$non_flag_count" -lt 2 ]]; then
        fail "grep benötigt Pattern + mindestens eine Datei"
    fi

    local index=0
    for arg in "${file_candidates[@]}"; do
        if [[ "$index" -eq 0 ]]; then
            index=$((index + 1))
            continue
        fi
        if [[ "$arg" == "." || "$arg" == "/" ]]; then
            fail "Weite grep-Ziele sind verboten: $arg"
        fi
        assert_file_in_project "$arg"
        index=$((index + 1))
    done
}

main() {
    if [[ $# -lt 1 ]]; then
        usage
        exit 1
    fi

    local cmd="$1"
    shift
    local args=("$@")

    is_allowed_command "$cmd" || fail "Befehl nicht erlaubt: $cmd (erlaubt: ${ALLOWED_COMMANDS[*]})"

    validate_token_safety "$cmd"
    for token in "${args[@]}"; do
        validate_token_safety "$token"
    done

    case "$cmd" in
        grep)
            validate_grep "$cmd" "${args[@]}"
            ;;
        awk|sed)
            validate_awk_or_sed "$cmd" "${args[@]}"
            ;;
        ls)
            if [[ "${#args[@]}" -eq 0 ]]; then
                args=("$PROJECT_ROOT")
            fi
            validate_generic_paths "$cmd" "${args[@]}"
            ;;
        cat|head|tail)
            validate_generic_paths "$cmd" "${args[@]}"
            for arg in "${args[@]}"; do
                if is_flag "$arg"; then
                    continue
                fi
                assert_file_in_project "$arg"
            done
            ;;
        *)
            fail "Interner Fehler: fehlende Validierung für $cmd"
            ;;
    esac

    echo "→ Guard OK | Projekt: $PROJECT_ROOT"
    cd "$PROJECT_ROOT"
    "$cmd" "${args[@]}"
}

main "$@"
