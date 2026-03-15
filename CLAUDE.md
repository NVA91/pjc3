# CLAUDE.md — Projekt pjc3

> **Router:** `core.md` — Zentraler Router. Jeder Agent liest diese Datei zuerst.
> **Direktive:** `.claude/agent-directive.md` — Hierarchie, Isolation, Zero Tolerance. Pflichtlektüre vor jeder Aktion.
> **Regeln:** `REGEL.md` — Repo-Grenzen, Verbote, Git-Regeln.

## Aktive Pläne

| Prio | Plan | Nächster Schritt |
|------|------|-----------------|
| 1 | `docs/superpowers/plans/2026-03-15-pyramid-core-migration.md` | **Nächste Session: Design-Spec schreiben** → Checkpoint 0→1 → Phase 1 |
| 2 | `../pjc3-docker/docs/superpowers/plans/2026-03-14-stack-inbetriebnahme.md` | LAN_IP eintragen → Pre-Flight |

**Fortsetzen:** `/weiter`

---

## Workflow-Pflichtregeln (vor jeder Aktion)

- **Repo bestätigen:** Vor Dateiänderungen `pwd` + Top-Level-Files prüfen — nie Repo raten
- **Plan suchen:** Bei Unklarheit zuerst `docs/`, `docs/superpowers/plans/`, `.claude/` durchsuchen, bevor Fragen gestellt werden
- **Plan vor Code:** Niemals direkt implementieren — erst nummerierten Plan vorlegen, Bestätigung abwarten
- **Git-Push:** Nur mit explizit bestätigter Auth (SSH-Key vorhanden?) — nie auf Verdacht pushen
- **Subagent-Driven Development:** Erfordert existierende Plan-Datei — ohne Plan: stopp und Plan zuerst schreiben
- **Session-Ende:** Plan-Status aktualisieren + CLAUDE.md "Aktive Pläne" prüfen — `/weiter` muss funktionieren
- **Secrets:** Immer zuerst lesen vor Schreiben — Datei könnte bereits echten Wert enthalten
- **pjc3-viz1:** TABU — nicht lesen, nicht anfassen, bis explizit freigegeben
- **Reihenfolge:** Aegis Core (pjc3) → Stack (pjc3-docker) → Satellit-Agenten — niemals überspringen

## Zweck
Globale Steuerzentrale — Aegis Core, Skills, Plugins, Commands. Claude API Experimente (SDK, Chatbots, Tool Use, Streaming, Notebooks) laufen hier als Basis.

---

## Umgebungshinweise

- `venv/` existiert **nicht** im Projektordner — `python3` direkt nutzen
- Pyright `reportMissingImports` für `mcp.server.fastmcp`, `dotenv`, `fastmcp` sind Falsch-Alarme (Pakete systemweit installiert)

---

## Techstack
- **Python** systemweit — kein venv, kein activate
- **Abhängigkeiten** (`requirements.txt`): `anthropic`, `jupyter`, `python-dotenv`
- **API-Key**: `ANTHROPIC_API_KEY` in `.env` (nicht committed)
- **Modelle**: `claude-sonnet-4-6` Standard · `claude-opus-4-6` Tool Use · `claude-haiku-4-5-20251001` Demos

---

## Projektstruktur

```
pjc3/
├── 01_getting_started.ipynb   # Tool-Use-Workflow (4 Schritte)
├── 02_messages_format.ipynb   # Messages-API-Format & Konversationshistorie
├── nova_claude.py             # Streaming-Chatbot (kein load_dotenv)
├── chatbot.py                 # Multi-Turn-Chatbot (kein load_dotenv)
├── generate_questions.py      # stop_sequences Demo (load_dotenv)
├── radar.py                   # System-Radar: Docker + Prozesse → Mermaid-Flowchart
├── mcp_gateway.py             # FastMCP ETL-Controller
├── extractor.py               # Dummy-Extraktor (--profile Pfad zur JSON-Datei)
├── profiles/                  # ETL-Profile JSON
├── docker-compose.yml         # Container-Konfiguration mit Sicherheits-Policies
├── Makefile                   # Namespace-isolierte Docker-Operationen (AGENT_NAMESPACE)
├── safe-container-exec.sh     # Wrapper gegen Directory Traversal in Containern
├── safe-project-exec.sh       # Host-Guard: Whitelist read-only Befehle
├── setup-agent-isolation.sh   # Einmalig als root: erstellt UID-isolierte Agent-User
├── statusline-command.sh      # Claude Code Status Line — referenziert in ~/.claude/settings.json
├── struktur_visualizer.py     # ASCII-Tree ~/claude-c/ → STRUKTUR.md (gitignored)
├── docs/superpowers/specs/    # Design-Specs: YYYY-MM-DD-<thema>-design.md
├── SYSTEM_VISUALIZATION.md    # Generierte Datei — nicht committen (.gitignore)
└── requirements.txt
```

---

## Befehle

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # für Skripte ohne load_dotenv
python nova_claude.py                  # Streaming-Chatbot
python chatbot.py                      # Einfacher Chatbot
python generate_questions.py           # stop_sequences Demo
jupyter notebook                       # Notebooks
python3 struktur_visualizer.py         # ASCII-Tree ~/claude-c/ → STRUKTUR.md
```

---

## API-Key-Handling

- `load_dotenv()`: `generate_questions.py`, Notebooks → lesen `.env` automatisch
- Kein `load_dotenv()`: `nova_claude.py`, `chatbot.py`, `mcp_gateway.py` → `ANTHROPIC_API_KEY` muss in Shell exportiert sein

---

## Konventionen

- **Streaming**: nur `nova_claude.py`; alle anderen blockierend
- **Konversationshistorie**: manuell als Python-Liste (`conversation` / `conversation_history`)
- **Keine externe State-Verwaltung**: alles in-memory pro Session
- **Subprozesse**: immer `sys.executable` statt `"python"` — gleiche Umgebung garantiert

---

## Pre-Flight Master-Skill (Phase 1)

- **Skill**: `.claude/skills/code-helper/SKILL.md`
- **Pflicht**: Intent-Routing → Label ausgeben → ggf. `NOVA_ROADMAP.md` → Implementierung
- **Intents**: `write_code` · `debug` · `review` · `architecture` · `docs` · `explain` · `ops`

---

## Git-Workflow

```bash
git checkout -b claude/<feature-name>
git push -u origin claude/<feature-name>
```

Commit-Konvention: `docs:` Dokumentation · `feat:` neue Funktionalität · kurz, Englisch

---

## MCP-Server (verfügbar)

| Name | Zweck |
|------|-------|
| memory | Session-Persistenz |
| deepwiki | GitHub-Repo-Doku |
| context7 | Bibliotheks-Dokumentation |
| n8n | Automation, Telegram, PDF |
| Notion | Notion-Integration |

**Quellen:** global `~/.claude.json` → `mcpServers` (memory, deepwiki, ETL_Controller) · cloud via claude.ai connector (context7, n8n, Notion)
**Diagnose-Reihenfolge:** zuerst `~/.claude.json` prüfen, dann claude.ai cloud — nicht verwechseln
**Konfiguration:** `~/.claude.json` → globale MCP: Schlüssel `mcpServers` · projektspezifisch: `projects.<pfad>.mcpServers`
**Diagnose:** `ps aux | grep mcp | grep -v grep` · `claude mcp list` (unzuverlässig)

### MCP ETL Controller
- `starte_extraktion(profil_name)` → `radar.py` → `extractor.py` → `radar.py`
- `radar.run(label)` direkt aufrufbar; CLI: `python3 radar.py --label "Zustand"`
- Profile in `profiles/<name>.json`; `SYSTEM_VISUALIZATION.md` wird überschrieben

---

## Docker-Sicherheit — Regeln

**Volumes:**
- Nur relative Pfade (`./config`) — niemals absolute (`/etc`, `/root`)
- Niemals `/var/run/docker.sock` mounten
- Config + Secrets immer `read_only: true` + `propagation: rprivate`
- Secrets ausschließlich unter `/run/secrets`, nie in `environment:`
- Named Volumes: `${AGENT_NAMESPACE}-${COMPOSE_PROJECT_NAME}-vol-<zweck>`

**Container:**
- Niemals `user: root` / `user: "0:0"` — immer UID 1001–1003
- `security_opt: [no-new-privileges:true]` immer setzen
- Zwei Agenten dürfen niemals die gleiche UID teilen
- `cap_drop: [ALL]` immer setzen — auf Service-Level, nicht innerhalb `security_opt`
- `read_only: true` auf Service-Level → rootfs unveränderlich, Bind-Mounts bleiben schreibbar (beabsichtigt)
- Ressourcenlimits: `mem_limit: ${AGENT_MEM_LIMIT:-512m}` + `cpus: "${AGENT_CPU_LIMIT:-0.5}"`
- Netzwerk: `internal: true` auf `agent-net` — kein Outbound-Traffic; Naming: `${AGENT_NAMESPACE}-${COMPOSE_PROJECT_NAME}-net`

**Operationen:**
- Niemals `docker compose down/stop/rm` ohne `-p`-Flag — immer `Makefile` nutzen
- Niemals `docker compose exec` direkt — immer `safe-container-exec.sh`
- `make down` ist **interaktiv** — fragt nach `y`, nicht automatisierbar
- Makefile berechnet `COMPOSE_PROJ` als `${AGENT_NAMESPACE}-pjc003` (`printf '%03d'` padding, nicht `pjc3`)
- `docker compose config --quiet` — YAML-Syntax validieren; Kommentare werden gestripped → `grep -c "EXTEND:" file` für EXTEND-Blöcke

---

## Security

- **sec-guard**: Argument Injection (Flag-Allowlist), Command Injection (Array-Form), Path Traversal (realpath + Base-Check)
- **Bash POSIX ERE**: kein Negative Lookahead (`(?!...)`) — wird still ignoriert. Zwei-Schritt-Check verwenden: erst auf `/` prüfen, dann auf `/app/` gegenchecken
- **Subprozesse**: `sys.executable` statt `"python"` — verhindert stille Fehler durch falsches System-Python

---

## Architektur-Konventionen

### Memory-Anker (Datei-Header)
```python
# MEMORY: dateiname.py
# Erweiterungsäste: dateiname_erweiterung.py
# Wenn X fehlschlägt: Y prüfen
# Verknüpft mit: andere_datei.py → funktion()
```

### Erweiterungsäste
Neue Funktionalität in eigene Dateien (`grafana_tools_prometheus.py` statt alles in `grafana_tools.py`).
Im Memory-Anker der Elterndatei dokumentiert — kein Code, nur Verweis.

### Design-Specs
Pfad: `docs/superpowers/specs/YYYY-MM-DD-<thema>-design.md`
Format: Ziel → Architektur → Dateien → Konfiguration → Claude-Verhalten → Erweiterungsäste → Out of Scope

### Implementation Plans
Pfad: `docs/superpowers/plans/YYYY-MM-DD-<thema>.md`

---

## Monitoring (Docker)

- **cAdvisor ist kein Sidecar** — Host-Daemon; als Sidecar würde jede Instanz dieselben globalen Host-Metriken liefern
- **Kein `/sys` / `/proc` Mount** — verletzt Volume Mount Security Rules; zentraler Prometheus liest via `host.docker.internal:9323`
- **`monitoring.scrape=false`** für CLI-Only-Container ohne HTTP-Endpoint setzen — sonst permanente Prometheus Scrape-Fehler

---

## Satellitenrepos

- `pjc3-docker` — Home-Infrastruktur Stack · GitHub: `git@github.com:NVA91/pjc3-docker.git`
- `pjc3-viz1` — PDF-Analyse + Streamlit · lokal only, kein Remote

---

## Statusline

- Datei: `statusline-command.sh` (in diesem Repo, versioniert)
- Referenz: `~/.claude/settings.json` → `statusLine.command` mit absolutem Pfad
- Kein Symlink — direkter Pfad: `bash /home/ubhp-nova/claude-c/pjc3/statusline-command.sh`

---

## Agenten-Hierarchie

- **Router:** `core.md` — jeder Agent liest hier zuerst (Zuständigkeiten, Ticket-Format)
- **Verwalter:** `.claude/agents/verwalter.md` in jedem Sub-Repo — einziger Eintrittspunkt
- **doc-agent:** `.claude/agents/doc-agent.md` — schreibt Memory, löscht Temp-Notizen nach Aufgabe
- **Guardrail:** Cross-Repo-Writes werden vom Security-Hook geblockt — kein Bug, gewollt
- **Memory-Präfix:** `arch_` für Hierarchie/Routing-Docs · `project_` für Repo-Status

### Migrations-Agenten (temporär vs. dauerhaft)
- `phase-1-agent.md` — temporär, nach Phase 1 archivieren
- `checkpoint.md` — dauerhaft, Wartungszyklen + Verifikation Aegis Core + Verwalter
- Verwalter in Satellit-Repos — dauerhaft, kennt nur sein Repo

### Satellit-Migration — Git-Entkopplung
Vor Verwalter-Anlage: Remote lösen → Verwalter startet sauber → `REPO-STATUS.md` generieren → Remote neu verankern

---

## Nach der Migration

- **Cache-Bereinigung:** `~/.claude/cache/` erst nach Abschluss aller Phasen + Abschluss-Checkpoint leeren — niemals mittendrin
- **Dauer-Tests:** Checkpoint-Agent periodisch laufen lassen — erst einrichten wenn Migration stabil

---

## Bekannte Einschränkungen (Claude Code)

- Langer Paste-Text → in Datei speichern und mit `@/pfad/zur/datei.md` referenzieren
- `nova_claude.py` / `chatbot.py`: `ANTHROPIC_API_KEY` muss vor dem Start in der Shell gesetzt sein
