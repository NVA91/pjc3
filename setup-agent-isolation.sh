#!/bin/bash
# setup-agent-isolation.sh — Host-Setup für UID-Namespace-Isolation
#
# Erstellt dedizierte System-User für jeden Agenten mit strikten
# Verzeichnisrechten. Verhindert Cross-Agent-Zugriff auf Dateisystem-Ebene.
#
# Ausführen als root auf dem Docker-Host:
#   sudo bash setup-agent-isolation.sh
#
# UID-Mapping (fest — niemals ändern, da sonst Dateieigentümer inkonsistent):
#   CLAUDE:  1001:1001
#   GRAVITY: 1002:1002
#   NEXUS:   1003:1003

set -euo pipefail

create_agent_user() {
    local agent_name="$1"
    local uid="$2"
    local gid="$3"

    echo "→ Erstelle Agent-User: ${agent_name} (uid=${uid}, gid=${gid})"

    # Erstelle Gruppe, falls nicht vorhanden
    if ! getent group "${agent_name}-agent" &>/dev/null; then
        groupadd -g "$gid" "${agent_name}-agent"
    fi

    # Erstelle dedizierten System-User ohne Login-Shell
    if ! id "${agent_name}-agent" &>/dev/null; then
        useradd \
            -u "$uid" \
            -g "$gid" \
            -r \
            -s /bin/false \
            -d "/srv/agents/${agent_name}" \
            -c "Docker Agent ${agent_name}" \
            "${agent_name}-agent"
    fi

    # Projektverzeichnis mit strikten Rechten anlegen
    mkdir -p "/srv/agents/${agent_name}/projects"
    chown -R "${uid}:${gid}" "/srv/agents/${agent_name}"

    # 700: Nur der Agent-User darf lesen/schreiben/ausführen
    chmod 700 "/srv/agents/${agent_name}"

    # Explizit anderen Usern den Zugriff verweigern (Cross-Access-Schutz)
    chmod o-rwx "/srv/agents/${agent_name}"

    echo "  ✅ /srv/agents/${agent_name} (${uid}:${gid}, chmod 700)"
}

# UID-Tabelle (fest — niemals zwei Agenten die gleiche UID geben)
create_agent_user "CLAUDE"  1001 1001
create_agent_user "GRAVITY" 1002 1002
create_agent_user "NEXUS"   1003 1003

echo ""
echo "✅ Agent-Isolation abgeschlossen."
echo "   Audit: ls -lan /srv/agents/"
