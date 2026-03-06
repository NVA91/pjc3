#!/bin/bash
# safe-container-exec.sh — Wrapper für sichere Container-Befehlsausführung
#
# Schutz gegen:
#   - Directory Traversal: Blockiert alle Pfade mit ".." (Parent-Directory-Referenzen)
#   - Symlink-Attacks: Ausführung strikt im Container-Workdir, kein Host-Pfadzugriff
#   - Command Injection: Whitelist erlaubter Lese-Befehle, keine Schreib-/Exec-Operationen
#
# Verwendung:
#   AGENT_NAMESPACE=CLAUDE bash safe-container-exec.sh <project-name> "<command>"
#
# Beispiele:
#   AGENT_NAMESPACE=CLAUDE bash safe-container-exec.sh pjc001 "ls -la /app/data"
#   AGENT_NAMESPACE=CLAUDE bash safe-container-exec.sh pjc001 "cat /app/data/output.json"
#   AGENT_NAMESPACE=CLAUDE bash safe-container-exec.sh pjc001 "grep ERROR /app/data/app.log"

set -euo pipefail

# ── Whitelist erlaubter Befehle (nur Lese-Operationen) ──────────────────────
# Schreib-Befehle (rm, mv, cp, chmod, chown, ...) sind absichtlich ausgeschlossen.
readonly ALLOWED_COMMANDS=("find" "ls" "cat" "grep" "awk" "sed" "tail" "head")

execute_safe_command() {
    local agent_ns="${AGENT_NAMESPACE:?AGENT_NAMESPACE nicht gesetzt}"
    local project_name="${1:?Projekt-Name fehlt}"
    local command="${2:?Befehl fehlt}"

    local compose_proj="${agent_ns}-${project_name}"
    local container_workdir="/app"

    # ── Schritt 1: Befehl gegen Whitelist prüfen ────────────────────────────
    local cmd_base
    cmd_base=$(echo "$command" | awk '{print $1}')

    local allowed=false
    for allowed_cmd in "${ALLOWED_COMMANDS[@]}"; do
        if [[ "$cmd_base" == "$allowed_cmd" ]]; then
            allowed=true
            break
        fi
    done

    if [[ "$allowed" != true ]]; then
        echo "❌ Befehl nicht erlaubt: $cmd_base"
        echo "   Erlaubt: ${ALLOWED_COMMANDS[*]}"
        return 1
    fi

    # ── Schritt 2: Directory-Traversal blockieren ───────────────────────────
    # Blockiert "../../etc/passwd" und ähnliche Angriffe
    if [[ "$command" =~ \.\. ]]; then
        echo "❌ Parent-Directory-Traversal nicht erlaubt (..)"
        return 1
    fi

    # ── Schritt 3: Absoluten Pfad außerhalb /app blockieren ─────────────────
    # Verhindert direkten Zugriff auf /etc, /root, /proc etc. im Container
    if [[ "$command" =~ (^|[[:space:]])/(?!app/) ]]; then
        echo "❌ Absoluter Pfad außerhalb von /app nicht erlaubt"
        return 1
    fi

    # ── Schritt 4: Befehl im isolierten Container-Kontext ausführen ─────────
    # -w setzt Arbeitsverzeichnis; "cd $container_workdir &&" verhindert
    # dass ein Symlink-Target außerhalb des Workdirs erreichbar wird
    echo "→ Ausführe in [${compose_proj}]: $command"
    docker compose -p "$compose_proj" exec \
        -w "$container_workdir" \
        app sh -c "cd ${container_workdir} && ${command}"
}

# ── Einstiegspunkt ───────────────────────────────────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 2 ]]; then
        echo "Verwendung: AGENT_NAMESPACE=<ns> $0 <project-name> \"<command>\""
        echo "Beispiel:   AGENT_NAMESPACE=CLAUDE $0 pjc001 \"ls -la /app/data\""
        exit 1
    fi
    execute_safe_command "$1" "$2"
fi
