#!/usr/bin/env bash
# LADESTUFE 3 — RESSOURCE | KATEGORIE: Container-Ausführung
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: Baut ein sicherheitskonformes Docker-Image für Agenten-Ausführung
#               (node:20-slim, Non-Root-User UID 1001) und startet den Container
#               ephemer mit UID-Passthrough für korrekte Dateisystemrechte.
#
# VERWENDUNG:
#   bash docker_agent_run.sh build   [IMAGE_NAME] [TAG]
#   bash docker_agent_run.sh run     [IMAGE_NAME] [PROMPT]  -- claude-Argumente
#   bash docker_agent_run.sh test    [IMAGE_NAME]
#   bash docker_agent_run.sh clean   [IMAGE_NAME]
#
# VORAUSSETZUNG:
#   docker installiert und laufend (docker info)
#   ANTHROPIC_API_KEY in der Shell gesetzt (export ANTHROPIC_API_KEY=sk-ant-...)
#
# SICHERHEITSREGELN:
#   - KEIN Alpine (musl libc → Linker-Fehler bei nativen NPM-Paketen)
#   - Non-Root-User (UID 1001) im Dockerfile
#   - --rm: Container-Dateisystem ephemer (nach Beendigung gelöscht)
#   - -u $(id-u):$(id-g): UID-Passthrough verhindert Read-Only-Filesystem-Fehler
#   - API-Key nur via -e (keine Hardcodierung im Image)

set -euo pipefail
IFS=$'\n\t'

# =============================================================================
# KONFIGURATION
# =============================================================================

readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DEFAULT_IMAGE="claude-agent"
DEFAULT_TAG="latest"
DEFAULT_NPM_PACKAGE="@anthropic-ai/claude-code"

# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

_ts()   { date '+%Y-%m-%d %H:%M:%S'; }
log()   { echo "[$(_ts)] [INFO]  $*" >&2; }
ok()    { echo "[$(_ts)] [OK]    $*" >&2; }
warn()  { echo "[$(_ts)] [WARN]  $*" >&2; }
die()   { echo "[$(_ts)] [ERROR] $*" >&2; exit 1; }

usage() {
  cat >&2 <<EOF

VERWENDUNG:
  bash ${SCRIPT_NAME} build  [IMAGE]  [TAG]         Image bauen (node:20-slim)
  bash ${SCRIPT_NAME} run    [IMAGE]  [PROMPT]       Agent ephemer ausführen
  bash ${SCRIPT_NAME} test   [IMAGE]                Schreibrecht-Test im Volume
  bash ${SCRIPT_NAME} clean  [IMAGE]                Image und Layer entfernen

OPTIONEN (via Umgebungsvariablen):
  IMAGE_NAME=claude-agent     Docker-Image-Name (Standard)
  IMAGE_TAG=latest            Docker-Image-Tag (Standard)
  WORKSPACE=\$(pwd)           Host-Verzeichnis → /workspace im Container
  ANTHROPIC_API_KEY=sk-ant-   API-Key (Pflicht für run)
  NETWORK=none                Docker-Netzwerk (none | host | bridge)

BEISPIELE:
  bash ${SCRIPT_NAME} build
  bash ${SCRIPT_NAME} build mein-agent v1.2
  WORKSPACE=/home/user/projekt bash ${SCRIPT_NAME} run mein-agent "Analysiere README.md"
  bash ${SCRIPT_NAME} test
  bash ${SCRIPT_NAME} clean mein-agent

SICHERHEIT:
  - Basis-Image: node:20-slim (Debian/glibc) — KEIN Alpine (musl libc)
  - Non-Root-User: claude (UID 1001) im Dockerfile
  - UID-Passthrough: -u \$(id-u):\$(id-g) verhindert Read-Only-Filesystem-Fehler
  - Ephemer: --rm löscht Container-Dateisystem nach Beendigung

EOF
  exit 1
}

_pruefe_docker() {
  if ! command -v docker &>/dev/null; then
    die "Docker nicht gefunden. Install: https://docs.docker.com/engine/install/"
  fi
  if ! docker info &>/dev/null; then
    die "Docker-Daemon nicht erreichbar. Starten: sudo systemctl start docker"
  fi
}

_pruefe_api_key() {
  if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    die "ANTHROPIC_API_KEY nicht gesetzt.\nAusführen: export ANTHROPIC_API_KEY=sk-ant-..."
  fi
  if [[ "${ANTHROPIC_API_KEY}" != sk-ant-* ]]; then
    warn "ANTHROPIC_API_KEY hat unerwartetes Format (erwartet: sk-ant-...)"
  fi
}

# =============================================================================
# DOCKERFILE — inline generiert (kein separates Dockerfile nötig)
# =============================================================================

_dockerfile_inhalt() {
  local npm_paket="${1:-${DEFAULT_NPM_PACKAGE}}"
  cat <<'DOCKERFILE'
# SICHERHEITSREGEL: node:20-slim (Debian/glibc) — KEIN Alpine
# Alpine nutzt musl libc → Linker-Fehler bei nativen NPM-Paketen (*.node-Binaries)
FROM node:20-slim

# --- Sicherheits-Update & minimale Basis-Tools ---
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       git \
    && rm -rf /var/lib/apt/lists/*

# --- Non-Root-User anlegen (PFLICHT) ---
# -m  → Home-Verzeichnis /home/claude erstellen
# -u 1001 → Feste UID (CLAUDE-Konvention aus CLAUDE.md)
# -s /bin/bash → Login-Shell (für interaktive Debugging-Sessions)
RUN useradd -m -u 1001 -s /bin/bash claude

# --- CLI-Agent global installieren (als root, vor USER-Wechsel) ---
# npm install -g muss als root laufen → danach Rechte nicht mehr nötig
DOCKERFILE

  echo "RUN npm install -g ${npm_paket}"

  cat <<'DOCKERFILE'

# --- Workspace vorbereiten ---
RUN mkdir -p /workspace && chown claude:claude /workspace
WORKDIR /workspace

# --- Non-Root-User aktivieren VOR Entrypoint ---
# KRITISCH: Ohne USER-Wechsel läuft der Agent als root im Container
# → privilege escalation möglich bei Container-Escape
USER claude

# --- Gesundheitscheck ---
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=1 \
  CMD claude --version || exit 1

ENTRYPOINT ["claude"]
DOCKERFILE
}

# =============================================================================
# MODUS 1: BUILD — Image bauen
# =============================================================================

modus_build() {
  local image="${1:-${DEFAULT_IMAGE}}"
  local tag="${2:-${DEFAULT_TAG}}"
  local npm_paket="${3:-${DEFAULT_NPM_PACKAGE}}"
  local vollname="${image}:${tag}"

  _pruefe_docker
  log "Baue Image: ${vollname}"
  log "NPM-Paket:  ${npm_paket}"
  log "Basis:      node:20-slim (Debian/glibc — kein Alpine)"

  # Dockerfile in temp-Datei schreiben
  local tmp_dockerfile
  tmp_dockerfile="$(mktemp /tmp/Dockerfile.agent.XXXXXX)"
  trap 'rm -f "${tmp_dockerfile}"' EXIT

  _dockerfile_inhalt "${npm_paket}" > "${tmp_dockerfile}"

  log "Dockerfile-Inhalt:"
  cat "${tmp_dockerfile}" >&2
  echo "---" >&2

  docker build \
    --file "${tmp_dockerfile}" \
    --tag "${vollname}" \
    --label "agent.basis=node:20-slim" \
    --label "agent.non-root=claude:1001" \
    --label "agent.erstellt=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    .

  ok "Image gebaut: ${vollname}"
  docker image inspect "${vollname}" --format \
    "  Größe: {{.Size}} Bytes | ID: {{.Id}}" >&2
}

# =============================================================================
# MODUS 2: RUN — Agent ephemer ausführen
# =============================================================================

modus_run() {
  local image="${1:-${DEFAULT_IMAGE}}"
  local tag="${IMAGE_TAG:-${DEFAULT_TAG}}"
  local vollname="${image}:${tag}"
  shift 1  # restliche Argumente = claude-Parameter

  _pruefe_docker
  _pruefe_api_key

  local workspace="${WORKSPACE:-$(pwd)}"
  local netzwerk="${NETWORK:-none}"

  log "Starte Agent ephemer"
  log "Image:     ${vollname}"
  log "Workspace: ${workspace} → /workspace"
  log "UID:       $(id -u):$(id -g) (Host-UID-Passthrough)"
  log "Netzwerk:  ${netzwerk}"
  log "Claude-Argumente: $*"

  # Schreibrecht-Vorprüfung
  if [[ ! -w "${workspace}" ]]; then
    die "Workspace nicht beschreibbar: ${workspace}"
  fi

  # PFLICHT-Parameter:
  # --rm             → ephemer (Container-FS nach Beendigung gelöscht)
  # -v               → Workspace-Mount für Lese-/Schreibzugriff
  # -u $(id-u):$(id-g) → UID-Passthrough (verhindert Read-Only-Filesystem-Fehler)
  # -e               → API-Key (kein Hardcoding im Image)
  # --network        → Standard: none (Isolation), host wenn API-Calls nötig
  docker run \
    --rm \
    --interactive \
    --tty \
    --volume "${workspace}:/workspace" \
    --user "$(id -u):$(id -g)" \
    --env "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" \
    --network "${netzwerk}" \
    --workdir "/workspace" \
    "${vollname}" \
    "$@"

  ok "Agent beendet — Container-FS wurde verworfen (--rm)"
}

# =============================================================================
# MODUS 3: TEST — Schreibrecht-Test im Volume
# =============================================================================

modus_test() {
  local image="${1:-${DEFAULT_IMAGE}}"
  local tag="${IMAGE_TAG:-${DEFAULT_TAG}}"
  local vollname="${image}:${tag}"

  _pruefe_docker

  local workspace="${WORKSPACE:-$(pwd)}"
  local testdatei="docker_agent_schreibtest_$(date +%s).tmp"

  log "Schreibrecht-Test"
  log "Image:     ${vollname}"
  log "Workspace: ${workspace}"

  # Test 1: UID-Passthrough vorhanden — sollte schreiben können
  log "Test 1: Mit UID-Passthrough (-u $(id -u):$(id -g))"
  if docker run --rm \
      --volume "${workspace}:/workspace" \
      --user "$(id -u):$(id -g)" \
      --network none \
      "${vollname}" \
      --version &>/dev/null; then
    ok "Test 1 bestanden: Container startet korrekt"
  else
    warn "Test 1: claude --version fehlgeschlagen (API-Key evtl. nicht gesetzt)"
  fi

  # Test 2: Schreiben in /workspace
  log "Test 2: Datei in /workspace schreiben"
  if docker run --rm \
      --volume "${workspace}:/workspace" \
      --user "$(id -u):$(id -g)" \
      --entrypoint /bin/bash \
      --network none \
      "${vollname}" \
      -c "touch /workspace/${testdatei} && echo OK"; then
    ok "Test 2 bestanden: Schreibrecht korrekt"
    rm -f "${workspace}/${testdatei}"
  else
    die "Test 2 fehlgeschlagen: Kein Schreibrecht in /workspace — UID-Passthrough prüfen"
  fi

  # Test 3: OHNE UID-Passthrough → soll scheitern (Diagnose-Referenz)
  log "Test 3: OHNE UID-Passthrough (soll scheitern — Referenz-Test)"
  if docker run --rm \
      --volume "${workspace}:/workspace" \
      --entrypoint /bin/bash \
      --network none \
      "${vollname}" \
      -c "touch /workspace/${testdatei}" 2>/dev/null; then
    warn "Test 3: Schreiben OHNE -u möglich → Workspace-Berechtigungen sehr offen (chmod 777?)"
  else
    ok "Test 3: Erwarteter Fehler ohne -u — UID-Passthrough ist notwendig und wirksam"
  fi

  ok "Alle Tests abgeschlossen"
}

# =============================================================================
# MODUS 4: CLEAN — Image entfernen
# =============================================================================

modus_clean() {
  local image="${1:-${DEFAULT_IMAGE}}"
  local tag="${IMAGE_TAG:-${DEFAULT_TAG}}"
  local vollname="${image}:${tag}"

  _pruefe_docker

  log "Entferne Image: ${vollname}"
  if docker image inspect "${vollname}" &>/dev/null; then
    docker image rm "${vollname}"
    ok "Image entfernt: ${vollname}"
  else
    warn "Image nicht gefunden: ${vollname}"
  fi

  log "Entferne dangling Layers"
  docker image prune --force >&2
  ok "Aufräumen abgeschlossen"
}

# =============================================================================
# CLI
# =============================================================================

if [[ $# -lt 1 ]]; then
  usage
fi

modus="$1"; shift

case "${modus}" in
  build)
    modus_build "${1:-${DEFAULT_IMAGE}}" "${2:-${DEFAULT_TAG}}" "${3:-${DEFAULT_NPM_PACKAGE}}"
    ;;
  run)
    image="${1:-${DEFAULT_IMAGE}}"; shift
    modus_run "${image}" "$@"
    ;;
  test)
    modus_test "${1:-${DEFAULT_IMAGE}}"
    ;;
  clean)
    modus_clean "${1:-${DEFAULT_IMAGE}}"
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    die "Unbekannter Modus: '${modus}'\nErlaubt: build | run | test | clean"
    ;;
esac
