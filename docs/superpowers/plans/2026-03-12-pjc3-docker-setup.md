# pjc3-docker: Home-Infrastruktur Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eigenständiges Repository `pjc3-docker` als Proxmox-ready Home-Infrastruktur mit Caddy, Monitoring-Stack, Vaultwarden, einem Claude-Agenten-Verwalter (FastMCP) und einer MCP-Verknüpfung.

**Architecture:** Docker Compose Stack mit namespace-isolierten Containern nach den pjc3-Sicherheitsregeln (kein absoluter Host-Pfad, `rprivate`, `read_only`, Non-Root-User). Caddy als Reverse Proxy für alle `*.local`-Services. Ein FastMCP-Server (`mcp_docker_agent.py`) exponiert Stack-Verwaltungs-Tools für Claude. Ein Skill (`.claude/skills/docker-stack-manager/SKILL.md`) beschreibt dem Agenten die Arbeitsweise.

**Tech Stack:** Docker Compose v2, Caddy 2 Alpine, Prometheus, Grafana, Loki 3.x, Vaultwarden, FastMCP (Python), `sys.executable`-Subprozesse

---

## Sicherheits-Konflikt-Hinweis (vor dem Start lesen!)

Die Snippets aus `Dockersipes.txt` enthalten für cAdvisor und Node-Exporter absolute Host-Mounts:
```yaml
# ❌ VERBOTEN laut CLAUDE.md:
volumes:
  - /:/rootfs:ro
  - /var/run:/var/run:rw   # enthält docker.sock!
  - /sys:/sys:ro
  - /var/lib/docker/:/var/lib/docker:ro
```
Diese **verletzen explizit** unsere Sicherheitsregeln (Volume Mount Type Classification + UID-Isolation).

**Lösung im Plan:** cAdvisor wird als **deaktivierter optionaler Service** (`profiles: [monitoring-extended]`) implementiert und ist standardmäßig ausgeschaltet. Node-Exporter wird ohne Root-FS-Mount betrieben (eingeschränkte Metriken). Promtail loggt nur über Docker TCP-Socket-Alternative, nicht über den Unix-Socket.

---

## Datei-Struktur

```
/home/ubhp-nova/claude-c/pjc3-docker/       ← neues Repo (gleiche Ebene wie pjc3)
├── docker-compose.yml                        # Core-Stack: Caddy, Vaultwarden
├── docker-compose.monitor.yml                # Opt-in: Prometheus, Grafana, Loki
├── Caddyfile                                 # Reverse Proxy: *.local → Service
├── prometheus.yml                            # Scrape-Konfiguration
├── loki-config.yml                           # Loki lokale Konfiguration
├── promtail-config.yml                       # Promtail (ohne docker.sock)
├── .env.example                              # Vorlage; .env ist gitignored
├── Makefile                                  # Namespace-isolierte Operations (AGENT_NAMESPACE)
├── safe-container-exec.sh                    # Host-Guard (Whitelist-Befehle)
├── CLAUDE.md                                 # Projektregeln (diese Datei wird erstellt)
├── README.md                                 # Schnellstart-Dokumentation
├── .gitignore                                # .env, data/, secrets/, SYSTEM_VISUALIZATION.md
├── .mcp.json                                 # Lokale MCP-Server-Registrierung
├── mcp_docker_agent.py                       # FastMCP Agenten-Verwalter
├── requirements.txt                          # fastmcp, anthropic, python-dotenv
├── config/                                   # Read-only Container Config
│   ├── .gitkeep
│   └── prometheus.yml → symlink oder Kopie
├── secrets/                                  # Read-only Secrets (nur gitkeep, nie committen)
│   └── .gitkeep
├── data/                                     # Persistente Daten (gitignored)
│   └── .gitkeep
└── .claude/
    └── skills/
        └── docker-stack-manager/
            └── SKILL.md                      # Skill: Stack verwalten mit Claude
```

---

## Chunk 1: Repo-Grundgerüst

### Task 1: Verzeichnis + Git-Init

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/` (Verzeichnis)
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/.gitignore`
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/README.md`

- [ ] **Step 1: Verzeichnis anlegen + Git initialisieren**

```bash
cd /home/ubhp-nova/claude-c
mkdir pjc3-docker && cd pjc3-docker
git init
git branch -M main
```

- [ ] **Step 2: .gitignore erstellen**

```bash
cat > .gitignore << 'EOF'
# Secrets niemals committen
.env
secrets/
data/

# Python
__pycache__/
*.pyc
.venv/
venv/

# Generierte Dateien
SYSTEM_VISUALIZATION.md
*.log
EOF
```

- [ ] **Step 3: Grundstruktur anlegen**

```bash
mkdir -p config secrets data .claude/skills/docker-stack-manager
touch config/.gitkeep secrets/.gitkeep data/.gitkeep
```

- [ ] **Step 4: Initial Commit**

```bash
git add .gitignore config/.gitkeep secrets/.gitkeep data/.gitkeep
git commit -m "init: repo-grundstruktur pjc3-docker"
```

- [ ] **Step 5: GitHub-Repo erstellen und verknüpfen**

```bash
gh repo create pjc3-docker --public --description "Home-Infrastruktur Stack: Caddy, Monitoring, Vaultwarden + Claude-Agent"
git remote add origin git@github.com:$(gh api user --jq .login)/pjc3-docker.git
git push -u origin main
```

---

### Task 2: CLAUDE.md für pjc3-docker

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/CLAUDE.md`

- [ ] **Step 1: CLAUDE.md schreiben**

```markdown
# CLAUDE.md — Projekt pjc3-docker

## Zweck
Home-Infrastruktur Stack: Caddy (Reverse Proxy), Prometheus/Grafana (Monitoring),
Loki (Logs), Vaultwarden (Passwörter) — Proxmox-ready, MCP-verbunden.

## Verzeichnis
/home/ubhp-nova/claude-c/pjc3-docker/   ← gleiches Level wie pjc3

## Umgebung
- `python3` direkt (kein venv erforderlich — FastMCP systemweit installiert)
- Docker + Docker Compose v2 (`docker compose` ohne Bindestrich)
- API-Key: ANTHROPIC_API_KEY in `.env`

## Sicherheitsregeln (STRIKT)
- Kein absoluter Host-Pfad als Volume-Source (außer explizit dokumentierte Ausnahmen)
- Kein /var/run/docker.sock-Mount — NIEMALS
- Alle Bind-Mounts mit propagation: rprivate
- config/ und secrets/ immer read_only: true
- user: "${AGENT_UID}:${AGENT_GID}" — niemals root
- Namespace-Prefix: AGENT_NAMESPACE=CLAUDE, CLAUDE-pjc3docker-vol-*

## Befehle
# Stack starten:
AGENT_NAMESPACE=CLAUDE make up

# MCP-Agenten-Verwalter starten:
python3 mcp_docker_agent.py

# Monitoring-Stack dazuschalten:
AGENT_NAMESPACE=CLAUDE make up-monitor
```

- [ ] **Step 2: Committen**

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md für pjc3-docker"
git push
```

---

## Chunk 2: Docker-Stack (Core)

### Task 3: docker-compose.yml (Core: Caddy + Vaultwarden)

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/docker-compose.yml`
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/Caddyfile`
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/.env.example`

- [ ] **Step 1: docker-compose.yml schreiben**

```yaml
# docker-compose.yml — Core Stack
# Verwendung: AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 make up

services:
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    # Ports nur auf localhost binden (kein öffentliches Expose)
    ports:
      - "127.0.0.1:80:80"
      - "127.0.0.1:443:443"
    user: "${AGENT_UID}:${AGENT_GID}"
    volumes:
      # Named Volumes für Caddy-Daten — kein absoluter Host-Pfad
      - type: volume
        source: caddy-data
        target: /data
      - type: volume
        source: caddy-config
        target: /config
      # Caddyfile: read-only Config-Mount
      - type: bind
        source: ./Caddyfile
        target: /etc/caddy/Caddyfile
        read_only: true
        bind:
          propagation: rprivate
    networks:
      - home-net
    security_opt:
      - no-new-privileges:true
    labels:
      - "agent.namespace=${AGENT_NAMESPACE}"

  vaultwarden:
    image: vaultwarden/server:latest
    restart: unless-stopped
    user: "${AGENT_UID}:${AGENT_GID}"
    environment:
      # Passwörter NIE im Klartext — via Secrets-Datei
      - ADMIN_TOKEN_FILE=/run/secrets/vw_admin_token
    volumes:
      - type: volume
        source: vw-data
        target: /data
      - type: bind
        source: ./secrets
        target: /run/secrets
        read_only: true
        bind:
          propagation: rprivate
    networks:
      - home-net
    security_opt:
      - no-new-privileges:true
    labels:
      - "agent.namespace=${AGENT_NAMESPACE}"

networks:
  home-net:
    driver: bridge

volumes:
  caddy-data:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-caddy-data"
  caddy-config:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-caddy-config"
  vw-data:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-vw-data"
```

- [ ] **Step 2: Caddyfile schreiben**

```caddyfile
# Caddyfile
# Alle Services via *.local erreichbar

vault.local {
  reverse_proxy vaultwarden:80
  tls internal
}

# Platzhalter für eigene Projekte:
# meinapp.local {
#   reverse_proxy meinapp:PORT
#   tls internal
# }
```

- [ ] **Step 3: .env.example schreiben**

```bash
# .env.example — Vorlage, NIE committen
# Kopieren: cp .env.example .env und Werte ausfüllen

AGENT_NAMESPACE=CLAUDE
AGENT_UID=1001
AGENT_GID=1001
ANTHROPIC_API_KEY=sk-ant-...
```

- [ ] **Step 4: Testen ob Compose valide ist**

```bash
# Nur Syntax prüfen — kein Start
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  docker compose config --quiet
```

Erwartet: kein Fehleroutput

- [ ] **Step 5: Committen**

```bash
git add docker-compose.yml Caddyfile .env.example
git commit -m "feat: core stack — caddy + vaultwarden (security-hardened)"
git push
```

---

### Task 4: Makefile (Namespace-isoliert)

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/Makefile`

- [ ] **Step 1: Makefile schreiben**

```makefile
# Makefile — Namespace-isolierte Docker-Operationen
# Verwendung: AGENT_NAMESPACE=CLAUDE make up

ifndef AGENT_NAMESPACE
$(error AGENT_NAMESPACE ist nicht gesetzt. Aufruf: AGENT_NAMESPACE=CLAUDE make <target>)
endif

AGENT_NS      := $(AGENT_NAMESPACE)
PROJ_ID       := pjc3docker
COMPOSE_PROJ  := $(AGENT_NS)-$(PROJ_ID)
COMPOSE       := docker compose -p $(COMPOSE_PROJ)
LOG_DIR       := /var/log/docker-projects/$(AGENT_NS)

.PHONY: up up-monitor down ps logs guard

up:
	@echo "[$(AGENT_NS)/$(PROJ_ID)] Stack starten..."
	$(COMPOSE) up -d
	@echo "[$(AGENT_NS)/$(PROJ_ID)] Läuft."

up-monitor:
	@echo "[$(AGENT_NS)/$(PROJ_ID)] Core + Monitoring starten..."
	$(COMPOSE) -f docker-compose.yml -f docker-compose.monitor.yml up -d

down:
	@printf "Stack '%s' stoppen? [j/N] " "$(COMPOSE_PROJ)"; \
	read ans; \
	[ "$$ans" = "j" ] && $(COMPOSE) down || echo "Abgebrochen."

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs --tail=50 --follow

guard:
ifndef CMD
	$(error CMD nicht gesetzt. Aufruf: make guard CMD='cat /app/data/foo.json')
endif
	@bash safe-container-exec.sh $(PROJ_ID) "$(CMD)"
```

- [ ] **Step 2: safe-container-exec.sh aus pjc3 kopieren und anpassen**

```bash
cp /home/ubhp-nova/claude-c/pjc3/safe-container-exec.sh ./safe-container-exec.sh
chmod +x safe-container-exec.sh
```

- [ ] **Step 3: Syntax prüfen**

```bash
AGENT_NAMESPACE=CLAUDE make ps
```

Erwartet: leere Container-Liste (Stack noch nicht gestartet), kein Make-Fehler

- [ ] **Step 4: Committen**

```bash
git add Makefile safe-container-exec.sh
git commit -m "ops: makefile namespace-isoliert + safe-container-exec"
git push
```

---

## Chunk 3: Monitoring-Stack (Optional)

### Task 5: docker-compose.monitor.yml

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/docker-compose.monitor.yml`
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/prometheus.yml`
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/loki-config.yml`
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/promtail-config.yml`

Hinweis: Node-Exporter und cAdvisor werden mit `profiles: [extended]` als **opt-in** angelegt.
Der Docker-Socket-Mount wird **nicht** verwendet. Stattdessen greift Prometheus direkt auf
den Docker-Daemon-Metrics-Endpoint (TCP) zu — dieser muss einmalig auf dem Host aktiviert werden.

- [ ] **Step 1: docker-compose.monitor.yml schreiben**

```yaml
# docker-compose.monitor.yml — Monitoring-Erweiterung
# Verwendung: AGENT_NAMESPACE=CLAUDE make up-monitor

services:
  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    user: "${AGENT_UID}:${AGENT_GID}"
    volumes:
      - type: bind
        source: ./prometheus.yml
        target: /etc/prometheus/prometheus.yml
        read_only: true
        bind:
          propagation: rprivate
      - type: volume
        source: prometheus-data
        target: /prometheus
    networks:
      - home-net
    security_opt:
      - no-new-privileges:true

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    user: "${AGENT_UID}:${AGENT_GID}"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_admin_pass
    volumes:
      - type: volume
        source: grafana-data
        target: /var/lib/grafana
      - type: bind
        source: ./secrets
        target: /run/secrets
        read_only: true
        bind:
          propagation: rprivate
    networks:
      - home-net
    security_opt:
      - no-new-privileges:true

  loki:
    image: grafana/loki:3.1.1
    restart: unless-stopped
    user: "${AGENT_UID}:${AGENT_GID}"
    volumes:
      - type: bind
        source: ./loki-config.yml
        target: /etc/loki/local-config.yaml
        read_only: true
        bind:
          propagation: rprivate
      - type: tmpfs
        target: /tmp/loki
        tmpfs:
          size: 500M
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - home-net
    security_opt:
      - no-new-privileges:true

  # ⚠️  SICHERHEITSHINWEIS: node-exporter benötigt Host-Mounts (/proc, /sys).
  # Aktivierung NUR wenn explizit benötigt: docker compose --profile extended up
  node-exporter:
    image: prom/node-exporter:latest
    restart: unless-stopped
    profiles: ["extended"]
    # Eingeschränkt: nur /proc und /sys (kein root /)
    # EXCEPTION dokumentiert: Monitoring-Tool braucht Kernel-Interfaces
    volumes:
      - type: bind
        source: /proc
        target: /host/proc
        read_only: true
        bind:
          propagation: rprivate
      - type: bind
        source: /sys
        target: /host/sys
        read_only: true
        bind:
          propagation: rprivate
    command:
      - --path.procfs=/host/proc
      - --path.sysfs=/host/sys
      - --no-collector.filesystem  # Root-FS-Collector deaktiviert
    networks:
      - home-net
    security_opt:
      - no-new-privileges:true

volumes:
  prometheus-data:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-prometheus"
  grafana-data:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-grafana"
```

- [ ] **Step 2: prometheus.yml schreiben**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']

  - job_name: grafana
    static_configs:
      - targets: ['grafana:3000']

  # Docker-Daemon-Metriken via TCP (muss auf Host aktiviert sein):
  # /etc/docker/daemon.json: {"metrics-addr": "127.0.0.1:9323", "experimental": true}
  - job_name: docker
    static_configs:
      - targets: ['host.docker.internal:9323']
```

- [ ] **Step 3: loki-config.yml schreiben**

```yaml
auth_enabled: false
server:
  http_listen_port: 3100
ingester:
  lifecycler:
    address: 127.0.0.1
  chunk_idle_period: 1h
  max_chunk_age: 1h
schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
storage_config:
  tsdb_shipper:
    active_index_directory: /tmp/loki/tsdb-shipper-active
    cache_location: /tmp/loki/tsdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /tmp/loki/chunks
```

- [ ] **Step 4: Syntax-Prüfung**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  docker compose -f docker-compose.yml -f docker-compose.monitor.yml config --quiet
```

Erwartet: kein Fehleroutput

- [ ] **Step 5: Committen**

```bash
git add docker-compose.monitor.yml prometheus.yml loki-config.yml promtail-config.yml
git commit -m "feat: monitoring stack — prometheus, grafana, loki (opt-in extended)"
git push
```

---

## Chunk 4: MCP Agenten-Verwalter

### Task 6: FastMCP-Server `mcp_docker_agent.py`

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/mcp_docker_agent.py`
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/requirements.txt`

Der Agenten-Verwalter stellt Claude Tools bereit, um den Stack zu steuern:
- `stack_status()` → `docker compose ps` Ausgabe
- `stack_start(profile)` → `make up` oder `make up-monitor`
- `stack_stop()` → `make down` (mit Bestätigung im Tool)
- `stack_logs(service, lines)` → Logs abrufen

- [ ] **Step 1: requirements.txt schreiben**

```
fastmcp>=0.1.0
anthropic
python-dotenv
```

- [ ] **Step 2: mcp_docker_agent.py schreiben**

```python
#!/usr/bin/env python3
"""
mcp_docker_agent.py — FastMCP Agenten-Verwalter für pjc3-docker Stack.
Stellt Claude Tools zur Stack-Verwaltung bereit.
"""
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

# Projektverzeichnis — relativ zum Skript, keine absoluten Pfade hardcoden
PROJECT_DIR = Path(__file__).parent.resolve()
AGENT_NAMESPACE = "CLAUDE"
AGENT_UID = "1001"
AGENT_GID = "1001"

mcp = FastMCP("docker-stack-manager")


def _run_make(target: str, extra_env: dict | None = None) -> str:
    """Führt ein Makefile-Target sicher aus (keine shell=True)."""
    env = {
        "AGENT_NAMESPACE": AGENT_NAMESPACE,
        "AGENT_UID": AGENT_UID,
        "AGENT_GID": AGENT_GID,
        "PATH": "/usr/bin:/bin:/usr/local/bin",
    }
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        ["make", target],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    output = result.stdout + result.stderr
    return output.strip() or "(kein Output)"


@mcp.tool()
def stack_status() -> str:
    """Gibt den aktuellen Status aller Container im pjc3-docker Stack zurück."""
    return _run_make("ps")


@mcp.tool()
def stack_start(profile: str = "core") -> str:
    """
    Startet den Docker-Stack.

    Args:
        profile: 'core' für Caddy+Vaultwarden, 'monitor' für + Prometheus/Grafana/Loki
    """
    if profile not in ("core", "monitor"):
        return "Fehler: profile muss 'core' oder 'monitor' sein."
    target = "up" if profile == "core" else "up-monitor"
    return _run_make(target)


@mcp.tool()
def stack_logs(service: str = "", lines: int = 50) -> str:
    """
    Gibt Container-Logs zurück.

    Args:
        service: Service-Name (leer = alle Services)
        lines: Anzahl der letzten Log-Zeilen (max 200)
    """
    lines = min(lines, 200)
    cmd = [
        "docker", "compose",
        "-p", f"{AGENT_NAMESPACE}-pjc3docker",
        "logs", f"--tail={lines}",
    ]
    if service:
        # Whitelist: nur bekannte Service-Namen erlaubt
        allowed = {"caddy", "vaultwarden", "prometheus", "grafana", "loki", "node-exporter"}
        if service not in allowed:
            return f"Fehler: unbekannter Service '{service}'. Erlaubt: {allowed}"
        cmd.append(service)
    result = subprocess.run(
        cmd, cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=15,
    )
    return (result.stdout + result.stderr).strip() or "(keine Logs)"


@mcp.tool()
def stack_info() -> str:
    """Gibt Informationen über die Stack-Konfiguration zurück."""
    return f"""pjc3-docker Stack-Info:
Projektverzeichnis: {PROJECT_DIR}
AGENT_NAMESPACE: {AGENT_NAMESPACE}
Compose-Projekt: {AGENT_NAMESPACE}-pjc3docker
Core-Services: caddy, vaultwarden
Monitor-Services: prometheus, grafana, loki (opt-in)
Erweiterter Monitor: node-exporter (profile: extended)

Befehle:
  stack_status()           → Container-Status
  stack_start('core')      → Core Stack starten
  stack_start('monitor')   → Core + Monitoring starten
  stack_logs('grafana', 100) → Grafana Logs
"""


if __name__ == "__main__":
    mcp.run()
```

- [ ] **Step 3: Ausführbar machen und testen**

```bash
chmod +x mcp_docker_agent.py
# Syntax prüfen (kein Start)
python3 -c "import mcp_docker_agent; print('OK')"
```

Erwartet: `OK`

- [ ] **Step 4: Committen**

```bash
git add mcp_docker_agent.py requirements.txt
git commit -m "feat: fastmcp agenten-verwalter (stack_status, stack_start, stack_logs)"
git push
```

---

### Task 7: .mcp.json — MCP-Verknüpfung

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/.mcp.json`

- [ ] **Step 1: .mcp.json schreiben**

```json
{
  "mcpServers": {
    "docker-stack-manager": {
      "type": "stdio",
      "command": "python3",
      "args": ["mcp_docker_agent.py"],
      "cwd": "/home/ubhp-nova/claude-c/pjc3-docker",
      "env": {
        "AGENT_NAMESPACE": "CLAUDE",
        "AGENT_UID": "1001",
        "AGENT_GID": "1001"
      }
    }
  }
}
```

- [ ] **Step 2: .mcp.json zu .gitignore hinzufügen?**

Nein — `.mcp.json` ist projektspezifische Konfiguration (kein Secret), soll committet werden.
Prüfe aber, dass der Pfad nicht hardcoded einen anderen Nutzer enthält (Username im Pfad).

Falls der Pfad auf einem anderen System falsch wäre, alternativ:

```json
"cwd": "."
```

Und den MCP-Server stets aus dem Projektverzeichnis starten.

- [ ] **Step 3: Committen**

```bash
git add .mcp.json
git commit -m "feat: .mcp.json — lokale MCP-Verknüpfung docker-stack-manager"
git push
```

---

## Chunk 5: Skill + Agenten-Definition

### Task 8: Skill `docker-stack-manager`

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/.claude/skills/docker-stack-manager/SKILL.md`

- [ ] **Step 1: SKILL.md schreiben**

```markdown
---
name: docker-stack-manager
description: >
  Verwaltet den pjc3-docker Home-Infrastruktur Stack.
  Verwende diesen Skill wenn: Stack starten/stoppen, Services prüfen,
  Logs abrufen, neue Services hinzufügen, Sicherheitsregeln prüfen.
---

# Docker Stack Manager Skill

## Stack-Übersicht

Projekt: `/home/ubhp-nova/claude-c/pjc3-docker`
Namespace: `CLAUDE` (UID 1001:1001)
Compose-Projekt: `CLAUDE-pjc3docker`

| Service        | Image                       | Profil    | URL                    |
|----------------|-----------------------------|-----------|------------------------|
| caddy          | caddy:2-alpine              | core      | Reverse Proxy          |
| vaultwarden    | vaultwarden/server:latest   | core      | https://vault.local    |
| prometheus     | prom/prometheus:latest      | monitor   | (intern)               |
| grafana        | grafana/grafana:latest      | monitor   | https://grafana.local  |
| loki           | grafana/loki:3.1.1          | monitor   | (intern)               |
| node-exporter  | prom/node-exporter:latest   | extended  | (intern, opt-in)       |

## MCP-Tools verfügbar

Wenn der MCP-Server `docker-stack-manager` aktiv ist:
- `stack_status()` — Container-Status
- `stack_start('core')` — Core starten
- `stack_start('monitor')` — Core + Monitoring starten
- `stack_logs('service', lines)` — Logs abrufen
- `stack_info()` — Konfigurationsinfo

## Ohne MCP: Makefile-Befehle

```bash
AGENT_NAMESPACE=CLAUDE make up          # Core starten
AGENT_NAMESPACE=CLAUDE make up-monitor  # + Monitoring
AGENT_NAMESPACE=CLAUDE make ps          # Status
AGENT_NAMESPACE=CLAUDE make logs        # Logs
AGENT_NAMESPACE=CLAUDE make down        # Stoppen (fragt nach Bestätigung)
```

## Sicherheitsregeln (beim Ändern beachten)

1. Keine absoluten Pfade als Volume-Source (außer /proc, /sys für node-exporter: explizite Ausnahme)
2. Kein /var/run/docker.sock-Mount — NIEMALS
3. `propagation: rprivate` bei allen Bind-Mounts
4. `read_only: true` für config/ und secrets/
5. `user: "${AGENT_UID}:${AGENT_GID}"` — niemals root
6. Volume-Namen: `${AGENT_NAMESPACE}-pjc3docker-vol-<zweck>`
7. Named Volumes immer mit vollständigem Präfix

## Neuen Service hinzufügen (Muster)

```yaml
# In docker-compose.yml unter services:
meinservice:
  image: meineimage:latest
  restart: unless-stopped
  user: "${AGENT_UID}:${AGENT_GID}"
  volumes:
    - type: volume
      source: meinservice-data
      target: /app/data
  networks:
    - home-net
  security_opt:
    - no-new-privileges:true

# In volumes:
meinservice-data:
  name: "${AGENT_NAMESPACE}-pjc3docker-vol-meinservice"

# In Caddyfile:
# meinservice.local {
#   reverse_proxy meinservice:PORT
#   tls internal
# }
```

## Troubleshooting

- Stack startet nicht → `AGENT_NAMESPACE=CLAUDE make ps` + `make logs`
- Caddy-Fehler → `AGENT_NAMESPACE=CLAUDE make logs` und nach "caddy" filtern
- Volume-Kollision → `docker volume ls | grep CLAUDE-pjc3docker`
- MCP-Server nicht verbunden → `python3 mcp_docker_agent.py` manuell starten
```

- [ ] **Step 2: Committen**

```bash
git add .claude/skills/docker-stack-manager/SKILL.md
git commit -m "docs: skill docker-stack-manager (stack-verwaltung via claude)"
git push
```

---

## Chunk 6: Abschluss + Verifikation

### Task 9: README.md + End-to-End Test

**Files:**
- Create: `/home/ubhp-nova/claude-c/pjc3-docker/README.md`

- [ ] **Step 1: README.md schreiben**

```markdown
# pjc3-docker

Home-Infrastruktur Stack: Caddy, Vaultwarden, Prometheus, Grafana, Loki.
Proxmox-ready. Sicherheitsgehärtet. MCP-verbunden.

## Schnellstart

```bash
# 1. .env vorbereiten
cp .env.example .env
# .env editieren: AGENT_UID, AGENT_GID, ANTHROPIC_API_KEY, Passwörter in secrets/

# 2. Core starten
AGENT_NAMESPACE=CLAUDE make up

# 3. Mit Monitoring
AGENT_NAMESPACE=CLAUDE make up-monitor

# 4. MCP-Agenten-Verwalter aktivieren
python3 mcp_docker_agent.py
```

## Struktur
Siehe CLAUDE.md für vollständige Dokumentation.

## Sicherheit
Alle Volume-Mounts sind read-only, rprivate, non-root. Details: CLAUDE.md.
```

- [ ] **Step 2: Smoke-Test — Compose-Konfiguration validieren**

```bash
cd /home/ubhp-nova/claude-c/pjc3-docker
export AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001
docker compose config --quiet && echo "✓ Core-Stack valide"
docker compose -f docker-compose.yml -f docker-compose.monitor.yml config --quiet && echo "✓ Monitor-Stack valide"
```

Erwartet: beide Zeilen mit `✓`

- [ ] **Step 3: Python-Syntax des MCP-Servers prüfen**

```bash
python3 -m py_compile mcp_docker_agent.py && echo "✓ mcp_docker_agent.py valide"
```

Erwartet: `✓ mcp_docker_agent.py valide`

- [ ] **Step 4: Git-Status prüfen**

```bash
git status
git log --oneline
```

Erwartet: `nothing to commit`, mind. 7 Commits im Log

- [ ] **Step 5: Final Commit + Push**

```bash
git add README.md
git commit -m "docs: readme + smoke-test abgeschlossen"
git push
echo "✓ pjc3-docker fertig"
```

---

## Zusammenfassung

| Was | Wo | Zweck |
|-----|----|----|
| `docker-compose.yml` | Projektroot | Core Stack (Caddy, Vaultwarden) |
| `docker-compose.monitor.yml` | Projektroot | Monitoring opt-in (Prometheus, Grafana, Loki) |
| `Makefile` | Projektroot | Namespace-isolierte Operationen |
| `mcp_docker_agent.py` | Projektroot | FastMCP Agenten-Verwalter |
| `.mcp.json` | Projektroot | MCP-Verknüpfung für Claude |
| `.claude/skills/docker-stack-manager/SKILL.md` | Projektroot | Skill für Claude-Agenten |
| `CLAUDE.md` | Projektroot | Projekt-Regeln |
| GitHub Repo | `pjc3-docker` | Eigenständiges Repo |

**Projektpfad:** `/home/ubhp-nova/claude-c/pjc3-docker/`
(gleiche Ebene wie `pjc3`)
