# Docker Hardening & Monitoring Template — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `docker-compose.yml` um Security Hardening (cap_drop, read_only, Ressourcenlimits, Netzwerk-Isolation) und Monitoring-Vorbereitung (Labels, Logging, kommentierte Healthchecks) erweitern.

**Architecture:** Alle Änderungen erfolgen ausschließlich in `docker-compose.yml`. Kein neuer Code, kein Sidecar. Das Template bleibt out-of-the-box lauffähig — neue Features werden als `# EXTEND:` Kommentarblöcke dokumentiert.

**Tech Stack:** Docker Compose v2, YAML

**Spec:** `docs/superpowers/specs/2026-03-13-docker-hardening-monitoring-design.md`

---

## Chunk 1: Security Hardening

### Task 1: Capabilities droppen

**Files:**
- Modify: `docker-compose.yml` — `security_opt` Block erweitern

- [ ] **Step 1: Aktuellen Stand lesen**

```bash
grep -n "security_opt\|cap_drop\|cap_add" docker-compose.yml
```
Erwartung: Nur `no-new-privileges:true`, kein `cap_drop`.

- [ ] **Step 2: `cap_drop` unter `security_opt` ergänzen**

Nach `security_opt:` Block in `docker-compose.yml` folgendes hinzufügen (direkt nach `- no-new-privileges:true`):

```yaml
    cap_drop:
      - ALL
    # EXTEND: Einzelne Capabilities nur bei nachgewiesenem Bedarf ergänzen:
    # cap_add:
    #   - NET_BIND_SERVICE   # nur wenn Port < 1024 gebunden werden muss
```

- [ ] **Step 3: Syntax validieren**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config --quiet
```
Erwartung: Kein Fehler, kein Output.

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: drop all capabilities in agent container template"
```

---

### Task 2: Read-only Root-Filesystem

**Files:**
- Modify: `docker-compose.yml` — nach `user:` Zeile

- [ ] **Step 1: `read_only: true` nach `user:` ergänzen**

```yaml
    read_only: true
    # Hinweis: read_only:true macht das rootfs unveränderlich,
    # überschreibt aber NICHT Schreibrechte von Bind-Mounts.
    # ./data bleibt weiterhin schreibbar (beabsichtigt).
    # Temporäre Schreibzugriffe → /app/tmp (tmpfs, bereits konfiguriert)
```

- [ ] **Step 2: Syntax validieren**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config --quiet
```
Erwartung: Kein Fehler.

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: set read-only root filesystem in agent container"
```

---

### Task 3: Ressourcenlimits

**Files:**
- Modify: `docker-compose.yml` — nach `read_only:` Zeile

- [ ] **Step 1: Ressourcenlimits ergänzen**

```yaml
    mem_limit: ${AGENT_MEM_LIMIT:-512m}
    cpus: "${AGENT_CPU_LIMIT:-0.5}"
```

- [ ] **Step 2: Ressourcenlimit-Hinweis in Header-Kommentar einfügen**

Nur diesen Absatz einfügen — **nach** der `make up` Verwendungszeile und **vor** dem `UID-Mapping` Abschnitt. Den Rest des Headers nicht anfassen, nicht duplizieren.

```yaml
#
# Optionale Ressourcenlimits (Defaults: 512m RAM, 0.5 CPU):
#   AGENT_MEM_LIMIT=256m AGENT_CPU_LIMIT=0.25 ... make up
```

Der Header soll danach so aussehen:
```yaml
# Verwendung:
#   AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
#     SERVICE_IMAGE=myimage:latest make up
#
# Optionale Ressourcenlimits (Defaults: 512m RAM, 0.5 CPU):
#   AGENT_MEM_LIMIT=256m AGENT_CPU_LIMIT=0.25 ... make up
#
# UID-Mapping (fest, nie überschneiden):
#   CLAUDE:  1001:1001
#   GRAVITY: 1002:1002
#   NEXUS:   1003:1003
```

- [ ] **Step 3: Syntax validieren**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config --quiet
```
Erwartung: Kein Fehler.

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add memory and CPU resource limits to agent template"
```

---

## Chunk 2: Netzwerk-Isolation

### Task 4: agent-net mit internal: true

**Files:**
- Modify: `docker-compose.yml` — Service `networks:` + Top-Level `networks:` Sektion

- [ ] **Step 1: Service-Level `networks:` ergänzen**

Im `app` Service nach `labels:` hinzufügen:

```yaml
    networks:
      - agent-net
```

- [ ] **Step 2: Top-Level `networks:` Sektion ergänzen**

Am Ende der Datei, nach der `volumes:` Sektion:

```yaml
networks:
  agent-net:
    internal: true
    name: "${AGENT_NAMESPACE}-${COMPOSE_PROJECT_NAME}-net"
    # internal: true — kein Outbound-Traffic aus dem Container
    # Jeder Namespace bekommt sein eigenes Netz (Naming verhindert Kollisionen)
    #
    # EXTEND: Für Phase 2 (Prometheus-Scraping) zweites Netz ergänzen:
    # monitoring-net:
    #   internal: true
    #   name: "${AGENT_NAMESPACE}-${COMPOSE_PROJECT_NAME}-monitoring-net"
```

- [ ] **Step 3: Syntax validieren**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config --quiet
```
Erwartung: Kein Fehler.

- [ ] **Step 4: Container testweise starten und Netz prüfen**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  make up
docker inspect $(docker compose -p CLAUDE-pjc003 ps -q app) \
  --format '{{json .NetworkSettings.Networks}}' | jq 'keys'
```
Erwartung: `["CLAUDE-pjc003-net"]` (Makefile berechnet `pjc003` aus `basename $PWD | sed 's/pjc//'`).

- [ ] **Step 5: Container wieder stoppen**

> ⚠️ **Interaktiver Schritt** — der Shell-Prompt fragt nach Bestätigung. Nicht automatisierbar (sicherheitsbedingt so gewollt). Manuell `y` eingeben.

```bash
AGENT_NAMESPACE=CLAUDE make down
```

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add isolated agent-net with internal:true"
```

---

## Chunk 3: Monitoring-Vorbereitung

### Task 5: Logging-Konfiguration

**Files:**
- Modify: `docker-compose.yml` — nach `labels:` Block

- [ ] **Step 1: `logging` Block ergänzen**

```yaml
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        # Logs bleiben über `docker logs` erreichbar
        # Verhindert unbegrenztes Log-Wachstum auf dem Host
```

- [ ] **Step 2: Syntax validieren**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config --quiet
```
Erwartung: Kein Fehler.

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add json-file log rotation to agent template"
```

---

### Task 6: Monitoring-Labels

**Files:**
- Modify: `docker-compose.yml` — bestehenden `labels:` Block erweitern

- [ ] **Step 1: Monitoring-Labels ergänzen**

Den bestehenden `labels:` Block erweitern:

```yaml
    labels:
      - "agent.namespace=${AGENT_NAMESPACE}"
      - "project.name=${COMPOSE_PROJECT_NAME}"
      - "agent.uid=${AGENT_UID}"
      # Monitoring Labels — für zentralen Prometheus (Phase 2)
      # Hinweis: monitoring.scrape=false setzen für CLI-Only-Container
      # (kein HTTP-Endpoint → sonst permanente Scrape-Fehler in Prometheus)
      - "monitoring.scrape=true"
      - "monitoring.port=${AGENT_PORT:-8000}"
```

- [ ] **Step 2: Syntax validieren**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config --quiet
```
Erwartung: Kein Fehler.

- [ ] **Step 3: Labels im laufenden Container prüfen**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  make up
docker inspect $(docker compose -p CLAUDE-pjc003 ps -q app) \
  --format '{{json .Config.Labels}}' | jq
```
Erwartung: `monitoring.scrape`, `monitoring.port`, `agent.namespace` sind sichtbar.

- [ ] **Step 4: Container stoppen**

```bash
AGENT_NAMESPACE=CLAUDE make down
```

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add monitoring labels for Prometheus service discovery"
```

---

### Task 7: Healthcheck-Blöcke (auskommentiert)

**Files:**
- Modify: `docker-compose.yml` — nach `command:` Zeile

- [ ] **Step 1: Kommentierte Healthcheck-Blöcke ergänzen**

```yaml
    # EXTEND: Healthcheck einkommentieren passend zum Agent-Typ.
    # start_period bei Bedarf erhöhen (z.B. 30s für Agents mit API-Warmup).
    #
    # Variante A: HTTP-Prozess (z.B. mcp_gateway.py mit FastMCP-Endpoint)
    # Vorbedingung: AGENT_PORT muss gesetzt sein und /health-Endpunkt existieren.
    # healthcheck:
    #   test: ["CMD", "curl", "-f", "http://localhost:${AGENT_PORT:-8000}/health"]
    #   interval: 30s
    #   timeout: 5s
    #   retries: 3
    #   start_period: 10s
    #
    # Variante B: CLI-Prozess (z.B. nova_claude.py, chatbot.py)
    # Vorbedingung: Agent muss /app/tmp/agent.lock aktuell halten.
    # healthcheck:
    #   test: ["CMD", "sh", "-c", "test -f /app/tmp/agent.lock"]
    #   interval: 30s
    #   timeout: 5s
    #   retries: 3
    #   start_period: 10s
```

- [ ] **Step 2: Syntax validieren**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config --quiet
```
Erwartung: Kein Fehler.

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "docs: add commented healthcheck variants to agent template"
```

---

## Abschluss

### Task 8: Vollständiger Smoke-Test

- [ ] **Step 1: Template komplett ausgeben und prüfen**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  docker compose config
```
Checkliste (in `config`-Output sichtbar):
- `cap_drop: [ALL]` vorhanden
- `read_only: true` vorhanden
- `mem_limit` + `cpus` vorhanden
- `networks: agent-net` im Service vorhanden
- `internal: true` im Top-Level-Netz vorhanden
- `logging: driver: json-file` vorhanden
- `monitoring.scrape` Label vorhanden

> Hinweis: `docker compose config` streift YAML-Kommentare. Kommentar-Blöcke (`# EXTEND:`) separat prüfen:

```bash
grep -c "EXTEND: Healthcheck" docker-compose.yml   # Erwartung: 1
grep -c "cap_add:" docker-compose.yml               # Erwartung: 1 (auskommentiert)
```

- [ ] **Step 2: Container starten, Status prüfen, stoppen**

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 \
  SERVICE_IMAGE=python:3.12-slim \
  make up
AGENT_NAMESPACE=CLAUDE make ps
AGENT_NAMESPACE=CLAUDE make down
```
Erwartung: Container startet, Status `Up`, sauberer Stop.

- [ ] **Step 3: Abschluss verifizieren**

Alle Änderungen wurden bereits pro Task committed. Prüfen ob git sauber ist:

```bash
git status
```
Erwartung: `nothing to commit, working tree clean`

```bash
git log --oneline -7
```
Erwartung: 7 Commits sichtbar (Tasks 1-7 + Basis).
