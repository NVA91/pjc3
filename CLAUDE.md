# CLAUDE.md — Projekt pjc3

## Zweck
Claude API Lernprojekt — Experimente mit dem Anthropic Python SDK: Chatbots, Tool Use, Streaming, Notebooks und Skripte.

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

**Operationen:**
- Niemals `docker compose down/stop/rm` ohne `-p`-Flag — immer `Makefile` nutzen
- Niemals `docker compose exec` direkt — immer `safe-container-exec.sh`

---

## Security

- **sec-guard**: Argument Injection (Flag-Allowlist), Command Injection (Array-Form), Path Traversal (realpath + Base-Check)
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

---

## Schwesterprojekt

- `pjc3-docker` (`/home/ubhp-nova/claude-c/pjc3-docker/`) — Home-Infrastruktur Stack (Caddy, Pi-hole, Vaultwarden, MCP-Agent)
- GitHub: `git@github.com:NVA91/pjc3-docker.git`

---

## Bekannte Einschränkungen (Claude Code)

- Langer Paste-Text → in Datei speichern und mit `@/pfad/zur/datei.md` referenzieren
- `nova_claude.py` / `chatbot.py`: `ANTHROPIC_API_KEY` muss vor dem Start in der Shell gesetzt sein
