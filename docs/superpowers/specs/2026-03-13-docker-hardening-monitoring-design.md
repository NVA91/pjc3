# Docker Stack — Hardening & Monitoring Template

**Datum:** 2026-03-13
**Status:** Approved
**Projekt:** pjc3 — Agent Container Template
**Scope:** docker-compose.yml erweitern um Security Hardening + Monitoring-Vorbereitung

---

## Ziel

Das bestehende `docker-compose.yml` Template um Security Hardening und Monitoring-Vorbereitung erweitern.
Das Template soll „out of the box" grün aufleuchten und gleichzeitig zeigen, wie es erweitert wird.
Kein cAdvisor — zentraler Prometheus liest bereits via `host.docker.internal:9323`.

---

## Was bleibt (unverändert)

- Non-root User (UID/GID per Namespace: CLAUDE 1001, GRAVITY 1002, NEXUS 1003)
- `no-new-privileges: true`
- Read-only Mounts für `./config` und `./secrets`
- `rprivate` Propagation auf allen Bind-Mounts
- Named Volumes mit Namespace-Präfix (Format: `"${AGENT_NAMESPACE}-${COMPOSE_PROJECT_NAME}-vol-<zweck>"`)
- `tmpfs` für `/app/tmp`

Named Volume YAML (unverändert, muss erhalten bleiben):
```yaml
volumes:
  app-cache:
    name: "${AGENT_NAMESPACE}-${COMPOSE_PROJECT_NAME}-vol-cache"
    driver: local
```

**Achtung `make down`:** Das Makefile nutzt `--volumes` — das löscht Named Volumes beim Herunterfahren.
Für persistente Daten `make down` ohne `--volumes` verwenden oder Volume vor `down` sichern.

---

## Architektur

```
docker-compose.yml (erweitertes Template)
├── app                          ← Agent-Container (Claude/Gravity/Nexus)
│     ├── Security Hardening
│     │     ├── cap_drop: [ALL]             ← alle Capabilities gestrichen
│     │     ├── read_only: true             ← rootfs unveränderlich
│     │     └── mem_limit / cpus            ← via AGENT_MEM_LIMIT / AGENT_CPU_LIMIT
│     ├── Netzwerk
│     │     └── agent-net (internal: true)  ← kein Outbound-Traffic
│     ├── Logging
│     │     └── json-file, max 10MB / 3 Dateien
│     ├── Labels
│     │     └── monitoring.scrape=true, monitoring.port, agent.namespace
│     └── Healthcheck (auskommentiert, 2 Varianten mit # EXTEND: Header)
│           ├── Variante A: HTTP-Prozess (curl /health)
│           └── Variante B: CLI-Prozess (Lock-File-Check)
│
└── networks
      └── agent-net (internal: true)

Monitoring (extern, kein Sidecar):
  Zentraler Prometheus → host.docker.internal:9323 (Docker Daemon Metriken)
```

---

## Neue Env-Variablen

| Variable | Zweck | Default | Vorbedingung |
|----------|-------|---------|--------------|
| `AGENT_MEM_LIMIT` | RAM-Limit pro Container | `512m` | immer aktiv |
| `AGENT_CPU_LIMIT` | CPU-Limit (Anteile) | `0.5` | immer aktiv |
| `AGENT_PORT` | Port für Healthcheck Variante A + Monitoring-Label | `8000` | nur relevant wenn HTTP-Endpoint aktiv |

Bestehende Env-Variablen bleiben unverändert: `AGENT_NAMESPACE`, `AGENT_UID`, `AGENT_GID`, `SERVICE_IMAGE`, `COMPOSE_PROJECT_NAME`.

---

## Security Hardening Details

### Capabilities

```yaml
cap_drop:
  - ALL
# EXTEND: Einzelne Capabilities nur bei nachgewiesenem Bedarf ergänzen:
# cap_add:
#   - NET_BIND_SERVICE   # nur wenn Port < 1024 gebunden werden muss
```

### Read-only Root-Filesystem

```yaml
read_only: true
# tmpfs bereits vorhanden (/app/tmp) — deckt temporäre Schreibzugriffe ab
```

**Hinweis:** `read_only: true` auf Service-Ebene macht das Root-Filesystem unveränderlich,
überschreibt aber **nicht** die Schreibrechte von Bind-Mounts. Der `./data` Bind-Mount
(`/app/data`) bleibt weiterhin schreibbar — das ist beabsichtigt und notwendig für persistente Agent-Daten.

### Ressourcenlimits

```yaml
mem_limit: ${AGENT_MEM_LIMIT:-512m}
cpus: "${AGENT_CPU_LIMIT:-0.5}"
```

Verhindert, dass ein durchdrehender Agent-Prozess den gesamten Host in die Knie zwingt.

---

## Netzwerk-Isolation

```yaml
networks:
  agent-net:
    internal: true
    name: "${AGENT_NAMESPACE}-${COMPOSE_PROJECT_NAME}-net"
```

`internal: true` — kein Outbound-Traffic aus dem Container.
Jeder Namespace bekommt sein eigenes Netz (Naming via Präfix verhindert Kollisionen).

---

## Logging

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```

Verhindert unbegrenztes Log-Wachstum. Logs bleiben über `docker logs` erreichbar.

---

## Monitoring Labels

```yaml
labels:
  - "agent.namespace=${AGENT_NAMESPACE}"
  - "project.name=${COMPOSE_PROJECT_NAME}"
  - "agent.uid=${AGENT_UID}"
  - "monitoring.scrape=true"         # auf false setzen bei CLI-Only-Containern (kein HTTP-Endpoint)
  - "monitoring.port=${AGENT_PORT:-8000}"
```

Kein cAdvisor-Sidecar — Docker-Daemon-Metriken laufen bereits über `host.docker.internal:9323`.

**Wichtig:** `monitoring.scrape=true` bedeutet, dass Prometheus versucht Port `AGENT_PORT` zu scrapen.
Für CLI-Agenten ohne HTTP-Endpoint (z.B. `chatbot.py`, `nova_claude.py`) muss `monitoring.scrape=false` gesetzt werden, um permanente Scrape-Fehler in Prometheus zu vermeiden.

**Netzwerk-Topologie:** Mit `internal: true` auf `agent-net` kann Prometheus den Container-Port nur erreichen, wenn es selbst dem `agent-net` beigetreten ist. Aktuell scrapt der zentrale Prometheus **ausschließlich** Docker-Daemon-Metriken via `host.docker.internal:9323` — die `monitoring.port` Labels sind für **Phase 2** vorgesehen (wenn ein dediziertes `monitoring-net` neben `agent-net` existiert). Bis dahin: Labels setzen, scraping bleibt deaktiviert.

---

## Healthcheck (auskommentiert)

Das Template dokumentiert zwei Varianten als `# EXTEND:` Blöcke.
Der Container läuft out-of-the-box ohne aktiven Healthcheck (`sleep infinity`).

```yaml
# EXTEND: Healthcheck einkommentieren passend zum Agent-Typ
#
# Variante A: HTTP-Prozess (z.B. mcp_gateway.py mit FastMCP)
# healthcheck:
#   test: ["CMD", "curl", "-f", "http://localhost:${AGENT_PORT:-8000}/health"]
#   interval: 30s
#   timeout: 5s
#   retries: 3
#   start_period: 10s
#
# Variante B: CLI-Prozess (z.B. nova_claude.py, chatbot.py)
# Prüft ob Hauptprozess noch aktiv ist via Lock-File-Timestamp
# healthcheck:
#   test: ["CMD", "sh", "-c", "test -f /app/tmp/agent.lock"]
#   interval: 30s
#   timeout: 5s
#   retries: 3
#   start_period: 10s
```

---

## Was bewusst weggelassen wurde

| Komponente | Grund |
|-----------|-------|
| cAdvisor Sidecar | Host-Daemon, kein Sidecar-Tool — würde N-fach dieselben globalen Metriken liefern |
| `/sys` + `/proc` Mounts | Verletzung der Volume Mount Security Rules (CLAUDE.md) |
| `/var/run/docker.sock` Mount | Explizit verboten (CLAUDE.md) |
| AppArmor / Seccomp Profile | Out of scope für dieses Template — separater Erweiterungsast |
| Prometheus im selben Compose | Zentraler Core-Stack übernimmt das |

---

## Erweiterungsäste (vorbereitet, nicht implementiert)

| Datei / Konfiguration | Zweck | Trigger |
|----------------------|-------|---------|
| `seccomp-profile.json` | Syscall-Filterung per Agent | wenn erhöhte Isolation nötig |
| `apparmor-profile` | Mandatory Access Control | bei produktionsreifen Agenten |
| Healthcheck Variante A aktiv | HTTP-Check für mcp_gateway | wenn FastMCP-Endpoint läuft |
| Healthcheck Variante B aktiv | Lock-File-Check für CLI-Agenten | wenn Prozess-Monitoring nötig |

---

## Verknüpfung zur Architektur-Pyramide

- **Phase 1 (Kalibrierung):** Template-Hardening, Monitoring-Labels — kein Overhead
- **Phase 2 (Nova Framework):** Healthchecks aktivieren, Ressourcenlimits pro Agent anpassen
- **Phase 3 (Nova Universe):** Seccomp/AppArmor-Profile per Agent-Rolle
