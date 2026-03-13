# pjc3-docker Extensions: Pi-hole, system_wizard, Postgres-Demo

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Voraussetzung:** Plan `2026-03-12-pjc3-docker-setup.md` vollständig abgeschlossen.

**Goal:** Pi-hole mit DNS-01-SSL via Caddy (kein Internet-Expose), `system_wizard()`-Tool im MCP-Agenten, und ein Postgres-Demo-Workflow der zeigt wie der Agent das alles orchestriert.

**Architecture:** Caddy wird mit einem cloudflare-DNS-Plugin custom gebaut (Dockerfile.caddy) — nur so ist DNS-01-Challenge möglich ohne inbound-Traffic. Pi-hole übernimmt den lokalen DNS und löst `*.home.DOMAIN` auf die Caddy-IP auf. `system_wizard()` liest Ports, Container, Secrets-Namen und Caddyfile atomar aus und gibt maschinenlesbares JSON zurück. `create_secret()` schreibt sicher in `./secrets/`.

**Tech Stack:** xcaddy, caddy-dns/cloudflare, pihole/pihole, FastMCP, Python `ss`/`re`/`json`, Docker Compose override pattern

---

## Datei-Struktur (Erweiterungen)

```
pjc3-docker/                           ← bestehendes Repo
├── Dockerfile.caddy                   ← NEU: Custom Caddy mit cloudflare DNS plugin
├── docker-compose.yml                 ← MODIFY: pihole-Service + Caddy build-Direktive
├── Caddyfile                          ← MODIFY: wildcard *.{HOME_DOMAIN}, kein .local mehr
├── config/
│   └── pihole-wildcard.conf           ← NEU: dnsmasq wildcard-Eintrag für *.home.DOMAIN
├── mcp_docker_agent.py                ← MODIFY: +system_wizard(), +create_secret()
└── .env.example                       ← MODIFY: +HOME_DOMAIN, +LAN_IP, +CLOUDFLARE_API_TOKEN
```

---

## Sicherheits-Ausnahmen (dokumentiert)

| Service | Ausnahme | Grund |
|---------|----------|-------|
| Pi-hole | Kein `user:` gesetzt (läuft intern als root) | dnsmasq-Daemon benötigt root für Port 53 |
| Pi-hole | `LAN_IP:53:53/tcp+udp` Port-Expose | DNS muss lokal erreichbar sein |
| Kein Docker-Socket-Mount | — | Promtail/cAdvisor ohne Socket |

---

## Chunk 7: Pi-hole + Caddy Custom Build + DNS-Challenge

### Task 10: Host-Voraussetzungen dokumentieren

**Files:**
- Modify: `CLAUDE.md` → Abschnitt "Host-Setup (einmalig)" hinzufügen

Bevor der Stack läuft, müssen auf dem Ubuntu-Host einmalig zwei Dinge getan werden:

**1. systemd-resolved deaktivieren** (belegt Port 53, blockiert Pi-hole):

- [ ] **Step 1: systemd-resolved stoppen und deaktivieren**

```bash
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
```

- [ ] **Step 2: /etc/resolv.conf auf direkten Nameserver setzen**

```bash
sudo rm /etc/resolv.conf
sudo bash -c 'printf "nameserver 1.1.1.1\nnameserver 8.8.8.8\n" > /etc/resolv.conf'
```

Prüfen:
```bash
cat /etc/resolv.conf
# Erwartet: nameserver 1.1.1.1  (kein symlink mehr)
ss -tlnp | grep :53
# Erwartet: kein Prozess auf Port 53
```

**2. Cloudflare API-Token beschaffen** (für DNS-Challenge):
- Cloudflare Dashboard → "My Profile" → "API Tokens" → "Create Token"
- Template: "Edit zone DNS" → Zone: deine Domain
- Token in `.env` als `CLOUDFLARE_API_TOKEN=...` eintragen (niemals committen)

- [ ] **Step 3: In CLAUDE.md dokumentieren**

Unter `## Host-Setup (einmalig)` eintragen:
```markdown
## Host-Setup (einmalig — als root auf dem Docker-Host)

1. systemd-resolved deaktivieren (Port 53 freigeben für Pi-hole):
   sudo systemctl disable --now systemd-resolved
   sudo rm /etc/resolv.conf
   echo -e "nameserver 1.1.1.1\nnameserver 8.8.8.8" | sudo tee /etc/resolv.conf

2. Cloudflare API-Token in .env:
   CLOUDFLARE_API_TOKEN=...   (Edit zone DNS Berechtigung)
   HOME_DOMAIN=home.example.com
   LAN_IP=192.168.178.100     (IP des Docker-Hosts im LAN)
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: host-setup anleitung (port 53, cloudflare token)"
```

---

### Task 11: Dockerfile.caddy — Custom Build mit Cloudflare DNS

**Files:**
- Create: `Dockerfile.caddy`

- [ ] **Step 1: Dockerfile.caddy schreiben**

```dockerfile
# Dockerfile.caddy — Custom Caddy Build mit cloudflare DNS-01 Plugin
# xcaddy kompiliert Caddy + Plugin in einem Multi-Stage-Build

FROM caddy:2-builder-alpine AS builder

RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare

FROM caddy:2-alpine

# Nur das fertige Binary übernehmen — kein Build-Tooling im finalen Image
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

- [ ] **Step 2: Build testen**

```bash
docker build -f Dockerfile.caddy -t caddy-cloudflare:local .
```

Erwartet: Build läuft durch, letzter Layer: `Successfully tagged caddy-cloudflare:local`

Prüfen ob Plugin enthalten:
```bash
docker run --rm caddy-cloudflare:local caddy list-modules | grep cloudflare
```

Erwartet: `dns.providers.cloudflare`

- [ ] **Step 3: Commit**

```bash
git add Dockerfile.caddy
git commit -m "feat: dockerfile.caddy mit cloudflare dns-01 plugin (xcaddy build)"
```

---

### Task 12: docker-compose.yml erweitern (Caddy build + Pi-hole)

**Files:**
- Modify: `docker-compose.yml` — Caddy-Service auf `build:` umstellen + Pi-hole hinzufügen
- Modify: `.env.example` — neue Variablen
- Create: `config/pihole-wildcard.conf` — dnsmasq Wildcard-Eintrag

- [ ] **Step 1: .env.example erweitern**

Folgende Zeilen anhängen:
```bash
# DNS-Challenge + Subdomain-Routing
HOME_DOMAIN=home.example.com
LAN_IP=192.168.178.100
CLOUDFLARE_API_TOKEN=DEIN_TOKEN_HIER

# Pi-hole
PIHOLE_PASSWORD_FILE=pihole_webpassword
```

- [ ] **Step 2: Caddy-Service in docker-compose.yml auf custom build umstellen**

Den bestehenden `caddy:`-Block **ersetzen**:

```yaml
  caddy:
    # Custom Build mit cloudflare DNS-01 Plugin (Dockerfile.caddy)
    build:
      context: .
      dockerfile: Dockerfile.caddy
    image: caddy-cloudflare:local
    restart: unless-stopped
    ports:
      - "127.0.0.1:80:80"
      - "127.0.0.1:443:443"
    user: "${AGENT_UID}:${AGENT_GID}"
    environment:
      # Cloudflare API-Token via ENV (aus .env, nie hardcoden)
      - CLOUDFLARE_API_TOKEN=${CLOUDFLARE_API_TOKEN}
      - HOME_DOMAIN=${HOME_DOMAIN}
    volumes:
      - type: volume
        source: caddy-data
        target: /data
      - type: volume
        source: caddy-config
        target: /config
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
```

- [ ] **Step 3: Pi-hole-Service hinzufügen**

Nach dem `vaultwarden:`-Block einfügen:

```yaml
  pihole:
    image: pihole/pihole:latest
    restart: unless-stopped
    # SECURITY-EXCEPTION: Pi-hole dnsmasq-Daemon benötigt intern root.
    # Kein user: gesetzt — dokumentierte Ausnahme.
    # Kompensation: no-new-privileges, kein docker.sock-Mount, Port nur auf LAN-IP.
    ports:
      # DNS-Port: nur auf LAN-Interface binden, NICHT auf 0.0.0.0
      - "${LAN_IP}:53:53/tcp"
      - "${LAN_IP}:53:53/udp"
      # HTTP-Admin: NICHT direkt exponiert — nur via Caddy (127.0.0.1)
    environment:
      - WEBPASSWORD_FILE=/run/secrets/pihole_webpassword
      - PIHOLE_DNS_=1.1.1.1;9.9.9.9
      - DNSSEC=true
      - DNSMASQ_LISTENING=all
      - VIRTUAL_HOST=pihole.${HOME_DOMAIN}
    volumes:
      - type: volume
        source: pihole-etc
        target: /etc/pihole
      - type: volume
        source: pihole-dnsmasq
        target: /etc/dnsmasq.d
      # Wildcard-DNS-Config: read-only via config/
      - type: bind
        source: ./config/pihole-wildcard.conf
        target: /etc/dnsmasq.d/99-home-wildcard.conf
        read_only: true
        bind:
          propagation: rprivate
      # Secrets: read-only
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
      - "security.exception=root-required-by-pihole-dnsmasq"
```

Und in `volumes:` am Ende hinzufügen:
```yaml
  pihole-etc:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-pihole-etc"
  pihole-dnsmasq:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-pihole-dnsmasq"
```

- [ ] **Step 4: config/pihole-wildcard.conf erstellen**

```
# dnsmasq Wildcard-Eintrag
# Alle *.home.DOMAIN-Anfragen → lokale Caddy-IP auflösen
# Wert wird via .env gesetzt → LAN_IP muss hier hardcoded sein (dnsmasq kennt keine ENV-Vars)
# WICHTIG: Nach IP-Änderung diese Datei aktualisieren!
address=/.home.example.com/192.168.178.100
```

**Hinweis:** Der Platzhalterwert `192.168.178.100` muss durch die echte LAN-IP ersetzt werden.
dnsmasq liest keine ENV-Vars — der Wert muss manuell oder via Setup-Skript eingetragen werden.

- [ ] **Step 5: Compose-Konfiguration validieren**

```bash
export AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001
export HOME_DOMAIN=home.example.com LAN_IP=192.168.178.100
export CLOUDFLARE_API_TOKEN=dummy
docker compose config --quiet && echo "✓ Core-Stack valide"
```

Erwartet: `✓ Core-Stack valide`

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml .env.example config/pihole-wildcard.conf
git commit -m "feat: pihole dns-container + caddy custom build (cloudflare dns-01)"
```

---

### Task 13: Caddyfile — Wildcard-Cert + Subdomain-Routing

**Files:**
- Modify: `Caddyfile` — vollständig ersetzen (kein .local mehr, echte Subdomains)

- [ ] **Step 1: Caddyfile neu schreiben**

```caddyfile
# Caddyfile — Wildcard SSL via Cloudflare DNS-01 Challenge
# Kein inbound-Traffic nötig. Caddy holt Cert direkt bei Let's Encrypt via DNS API.
# HOME_DOMAIN wird als Umgebungsvariable übergeben (docker-compose environment:)

{
  # Globaler ACME-DNS-Solver: Cloudflare
  # Überschreibt den Standard HTTP-01-Challenge für alle tls-Blöcke
  acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}

# Wildcard-Zertifikat für *.home.DOMAIN
# Alle Subdomains teilen sich dieses eine Cert (kein Cert pro Service nötig)
*.{$HOME_DOMAIN} {
  tls {
    dns cloudflare {env.CLOUDFLARE_API_TOKEN}
  }

  # Pi-hole Admin
  @pihole host pihole.{$HOME_DOMAIN}
  handle @pihole {
    reverse_proxy pihole:80
  }

  # Vaultwarden
  @vault host vault.{$HOME_DOMAIN}
  handle @vault {
    reverse_proxy vaultwarden:80
  }

  # Grafana (Monitor-Profil)
  @grafana host grafana.{$HOME_DOMAIN}
  handle @grafana {
    reverse_proxy grafana:3000
  }

  # Prometheus (Monitor-Profil — optional basicauth empfohlen)
  @prometheus host prometheus.{$HOME_DOMAIN}
  handle @prometheus {
    reverse_proxy prometheus:9090
  }

  # Unbekannte Subdomain → 404
  handle {
    respond "Not Found" 404
  }
}
```

- [ ] **Step 2: Caddyfile-Syntax prüfen**

```bash
docker run --rm \
  -e CLOUDFLARE_API_TOKEN=dummy \
  -e HOME_DOMAIN=home.example.com \
  -v "$PWD/Caddyfile:/etc/caddy/Caddyfile:ro" \
  caddy-cloudflare:local \
  caddy validate --config /etc/caddy/Caddyfile
```

Erwartet: `Valid configuration`

- [ ] **Step 3: Commit**

```bash
git add Caddyfile
git commit -m "feat: caddyfile wildcard-ssl dns-01 (*.home.domain, kein .local)"
```

---

## Chunk 8: system_wizard() + create_secret() Tool

### Task 14: system_wizard() in mcp_docker_agent.py

**Files:**
- Modify: `mcp_docker_agent.py` — zwei neue Tools anhängen

- [ ] **Step 1: Imports am Dateianfang prüfen/ergänzen**

Sicherstellen dass diese Imports vorhanden sind:
```python
import json
import re
import secrets as secrets_module
```
`re` und `json` zur bestehenden Import-Liste hinzufügen (oben in der Datei).

- [ ] **Step 2: system_wizard() Tool schreiben**

Nach dem bestehenden `stack_info()`-Tool einfügen:

```python
@mcp.tool()
def system_wizard() -> str:
    """
    Maschinenlesbarer Systemreport (JSON) für den Agenten.

    Liefert:
    - used_ports: Alle belegten TCP/UDP-Ports auf dem Host
    - containers: Laufende pjc3docker-Container mit State
    - secrets_present: Dateinamen in ./secrets/ (kein Inhalt!)
    - caddy_routes: Im Caddyfile vergebene Domains/Subdomains
    - warnings: Fehlende Konfiguration oder Probleme

    Typischer Einsatz: Vor dem Starten eines neuen Services prüfen ob
    Port frei, Secrets vorhanden und Caddy-Route noch nicht vergeben.
    """
    report: dict = {
        "used_ports": [],
        "containers": [],
        "secrets_present": [],
        "caddy_routes": [],
        "warnings": [],
    }

    # --- 1. Belegte Ports (TCP + UDP) ---
    for flag in ("-tlnp", "-ulnp"):
        result = subprocess.run(
            ["ss", flag],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines()[1:]:  # Header überspringen
            parts = line.split()
            if len(parts) < 5:
                continue
            # Spalte 4 = "Local Address:Port"
            addr = parts[4]
            port_str = addr.rsplit(":", 1)[-1]
            if port_str.isdigit():
                port = int(port_str)
                if port not in report["used_ports"]:
                    report["used_ports"].append(port)
    report["used_ports"].sort()

    # --- 2. Laufende Container im pjc3docker-Stack ---
    result = subprocess.run(
        [
            "docker", "compose",
            "-p", f"{AGENT_NAMESPACE}-pjc3docker",
            "ps", "--format", "json",
        ],
        cwd=str(PROJECT_DIR),
        capture_output=True, text=True, timeout=15,
    )
    for line in result.stdout.splitlines():
        try:
            c = json.loads(line)
            report["containers"].append({
                "name":    c.get("Name", ""),
                "service": c.get("Service", ""),
                "state":   c.get("State", ""),
                "status":  c.get("Status", ""),
            })
        except (json.JSONDecodeError, KeyError):
            pass

    # --- 3. Secrets-Verzeichnis (nur Dateinamen, nie Inhalt lesen) ---
    secrets_dir = PROJECT_DIR / "secrets"
    if secrets_dir.exists():
        report["secrets_present"] = sorted(
            f.name
            for f in secrets_dir.iterdir()
            if f.is_file() and f.name != ".gitkeep"
        )
    else:
        report["warnings"].append("secrets/-Verzeichnis fehlt — bitte anlegen")

    # --- 4. Caddyfile-Routen (vergebene Domains) ---
    caddyfile = PROJECT_DIR / "Caddyfile"
    if caddyfile.exists():
        content = caddyfile.read_text(encoding="utf-8")
        # Matche Zeilenanfänge mit Domain-ähnlichem Pattern (wildcard, subdomain, ENV-Var)
        raw_matches = re.findall(
            r"^([\w\.\*\-]+|\*\.\{[^\}]+\}|\{[^\}]+\})\s*\{",
            content,
            re.MULTILINE,
        )
        # Interne Caddy-Direktiven herausfiltern
        _caddy_keywords = {
            "handle", "tls", "header", "route", "encode", "respond",
            "basicauth", "file_server", "redir", "rewrite", "log",
        }
        report["caddy_routes"] = [
            r for r in raw_matches if r.lower() not in _caddy_keywords
        ]
    else:
        report["warnings"].append("Caddyfile nicht gefunden")

    return json.dumps(report, indent=2, ensure_ascii=False)
```

- [ ] **Step 3: Manueller Smoke-Test (ohne MCP-Server starten)**

```bash
cd /home/ubhp-nova/claude-c/pjc3-docker
python3 -c "
import mcp_docker_agent as a
print(a.system_wizard())
"
```

Erwartet: Valides JSON mit `used_ports`, `containers`, `secrets_present`, `caddy_routes`.
Bei leerem Stack: `containers: []`, `secrets_present: []` ist korrekt.

---

### Task 15: create_secret() Tool

- [ ] **Step 1: create_secret() schreiben**

Nach `system_wizard()` einfügen:

```python
@mcp.tool()
def create_secret(name: str) -> str:
    """
    Erzeugt ein kryptografisch sicheres Zufalls-Passwort und
    schreibt es als Secret-Datei in ./secrets/<name>.

    Args:
        name: Dateiname des Secrets (z.B. 'postgres_password', 'grafana_admin_pass').
              Nur Buchstaben, Ziffern, Unterstriche und Bindestriche erlaubt.

    Returns:
        JSON mit {"created": "<name>", "path": "./secrets/<name>"}
        NIEMALS den generierten Wert zurückgeben.
    """
    import re as _re

    # Eingabevalidierung: verhindert Path-Traversal und Shell-Injection
    if not _re.fullmatch(r"[a-zA-Z0-9_\-]{1,64}", name):
        return json.dumps({
            "error": f"Ungültiger Name '{name}'. Erlaubt: a-z, A-Z, 0-9, _ und - (max 64 Zeichen)."
        })

    secrets_dir = PROJECT_DIR / "secrets"
    secrets_dir.mkdir(exist_ok=True)

    target = secrets_dir / name

    if target.exists():
        return json.dumps({
            "error": f"Secret '{name}' existiert bereits. Lösche es zuerst manuell wenn du es ersetzen willst."
        })

    # 32 Byte → 43 Zeichen URL-safe Base64 (keine Sonderzeichen die Configs brechen)
    password = secrets_module.token_urlsafe(32)
    target.write_text(password, encoding="utf-8")

    return json.dumps({
        "created": name,
        "path": f"./secrets/{name}",
        "note": "Passwort gesetzt. Inhalt NICHT geloggt. Mit system_wizard() verifizieren."
    })
```

- [ ] **Step 2: Syntax prüfen**

```bash
python3 -m py_compile mcp_docker_agent.py && echo "✓ valide"
```

Erwartet: `✓ valide`

- [ ] **Step 3: Commit**

```bash
git add mcp_docker_agent.py
git commit -m "feat: system_wizard() + create_secret() tools im mcp-agenten-verwalter"
git push
```

---

## Chunk 9: Postgres-Demo — Agent-Workflow dokumentieren

### Task 16: docker-compose.override.yml Muster + Agent-Workflow

**Files:**
- Create: `docker-compose.override.example.yml` — Vorlage für neue Projekte
- Modify: `CLAUDE.md` — Abschnitt "Agent-Workflow: neuen Service hinzufügen"

Der Agent-Workflow für "Postgres für mein neues Projekt":

```
Nutzer: "Setz mir eine lokale Postgres-DB für projekt-x auf"

Agent:
  1. system_wizard()
     → used_ports: [80, 443, 53, ...] — Port 5432 FREI ✓
     → secrets_present: ["pihole_webpassword", "vw_admin_token"]
        "postgres_password" FEHLT → muss erst erstellt werden
     → caddy_routes: ["*.{$HOME_DOMAIN}"]

  2. create_secret("postgres_password")
     → {"created": "postgres_password", "path": "./secrets/postgres_password"}

  3. system_wizard() (erneut — Verifikation)
     → secrets_present: [..., "postgres_password"] ✓

  4. Gibt docker-compose.override.yml-Snippet zurück (nicht selbst schreiben)
     → Nutzer fügt es ein und ruft stack_start('core') auf

  5. stack_start('core')
     → Stack neu starten mit Postgres
```

- [ ] **Step 1: docker-compose.override.example.yml schreiben**

```yaml
# docker-compose.override.example.yml
#
# Vorlage für eigene Projekte. Kopieren:
#   cp docker-compose.override.example.yml docker-compose.override.yml
#
# Docker Compose lädt docker-compose.override.yml automatisch zusätzlich
# zur docker-compose.yml — kein extra -f Flag nötig.
#
# Pattern: Neuer Service + Named Volume + Caddy-Route (via Caddyfile)

# === BEISPIEL: PostgreSQL für projekt-x ===
services:
  postgres-projektx:
    image: postgres:16-alpine
    restart: unless-stopped
    user: "${AGENT_UID}:${AGENT_GID}"
    environment:
      # Secret-Datei statt Klartext-ENV (OCI-Konvention)
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
      - POSTGRES_DB=projektx
      - POSTGRES_USER=projektx
    volumes:
      - type: volume
        source: postgres-projektx-data
        target: /var/lib/postgresql/data
      - type: bind
        source: ./secrets
        target: /run/secrets
        read_only: true
        bind:
          propagation: rprivate
    # Port NUR auf localhost binden — kein LAN-Zugriff auf DB-Port
    ports:
      - "127.0.0.1:5432:5432"
    networks:
      - home-net
    security_opt:
      - no-new-privileges:true
    labels:
      - "agent.namespace=${AGENT_NAMESPACE}"

volumes:
  postgres-projektx-data:
    name: "${AGENT_NAMESPACE}-pjc3docker-vol-postgres-projektx"

# Caddyfile-Erweiterung (manuell in Caddyfile einfügen — nicht hier):
#
# @pgadmin host pgadmin.{$HOME_DOMAIN}
# handle @pgadmin {
#   reverse_proxy pgadmin:80
# }
```

- [ ] **Step 2: In CLAUDE.md dokumentieren**

Abschnitt `## Agent-Workflow: Neuen Service hinzufügen` anhängen:

```markdown
## Agent-Workflow: Neuen Service hinzufügen

1. `system_wizard()` aufrufen → Port-Check, Secret-Check, Route-Check
2. Falls Secret fehlt: `create_secret("mein_secret_name")` aufrufen
3. `system_wizard()` wiederholen → Verifikation
4. `docker-compose.override.example.yml` als Vorlage: Service-Block in
   `docker-compose.override.yml` einfügen
5. Subdomain in `Caddyfile` hinzufügen (Agent zeigt Snippet)
6. `stack_start('core')` → Stack neu starten
7. `stack_status()` → Läuft der neue Container?
```

- [ ] **Step 3: Smoke-Test: Agent-Workflow manuell nachspielen**

```bash
cd /home/ubhp-nova/claude-c/pjc3-docker
python3 -c "
import mcp_docker_agent as a
import json

# Schritt 1: Wizard
report = json.loads(a.system_wizard())
print('Ports belegt:', report['used_ports'][:5], '...')
print('Secrets:', report['secrets_present'])
print('Caddy-Routes:', report['caddy_routes'])

# Schritt 2: Secret erstellen (Test-Secret)
result = json.loads(a.create_secret('test_postgres_password'))
print('Secret erstellt:', result)

# Schritt 3: Verifikation
report2 = json.loads(a.system_wizard())
assert 'test_postgres_password' in report2['secrets_present'], 'Secret fehlt!'
print('✓ Secret in Wizard sichtbar')

# Aufräumen
import os
os.remove('./secrets/test_postgres_password')
print('✓ Test-Secret entfernt')
"
```

Erwartet:
```
Ports belegt: [53, 80, 443, ...] ...
Secrets: []
Caddy-Routes: ['*.{$HOME_DOMAIN}']
Secret erstellt: {"created": "test_postgres_password", ...}
✓ Secret in Wizard sichtbar
✓ Test-Secret entfernt
```

- [ ] **Step 4: Commit + Push**

```bash
git add docker-compose.override.example.yml CLAUDE.md
git commit -m "docs: agent-workflow postgres-demo + override.yml vorlage"
git push
```

---

## Zusammenfassung der Erweiterungen

| Was | Datei | Zweck |
|-----|-------|-------|
| `Dockerfile.caddy` | neu | xcaddy + cloudflare DNS-01 Plugin |
| `docker-compose.yml` | erweitert | Pi-hole + Caddy custom build |
| `Caddyfile` | ersetzt | Wildcard `*.home.DOMAIN` mit echtem SSL |
| `config/pihole-wildcard.conf` | neu | dnsmasq: `*.home.DOMAIN` → LAN-IP |
| `mcp_docker_agent.py` | erweitert | `system_wizard()` + `create_secret()` |
| `docker-compose.override.example.yml` | neu | Vorlage für eigene Services |
| `CLAUDE.md` | erweitert | Host-Setup + Agent-Workflow |

**DNS-Flow nach Setup:**
```
Gerät im LAN
  → DNS-Anfrage: vault.home.example.com
  → Pi-hole: *.home.example.com → 192.168.178.100 (Caddy)
  → Caddy: TLS terminieren (Wildcard-Cert von Let's Encrypt via DNS-01)
  → reverse_proxy vaultwarden:80
  → Browser: https://vault.home.example.com ✓ (gültiges Zertifikat, kein .local-Kampf)
```

**Kein eingehender Internet-Traffic nötig** — DNS-01 Challenge läuft nur ausgehend zu Cloudflare API.
