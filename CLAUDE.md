# CLAUDE.md — Projekt pjc3

## Zweck
Claude API Lernprojekt — Experimente mit dem Anthropic Python SDK: Chatbots, Tool Use, Streaming, Notebooks und Skripte.

---

## Techstack
- **Python** + venv (`./venv/`) — aktivieren: `source venv/bin/activate`
- **Abhängigkeiten** (`requirements.txt`): `anthropic`, `jupyter`, `python-dotenv`
- **API-Key**: `ANTHROPIC_API_KEY` in `.env` (nicht committed, via `.gitignore` ausgeschlossen)
- **Standardmodell**: `claude-sonnet-4-6`
- Weiteres Modell im Notebook `01`: `claude-opus-4-6` (für Tool Use)
- Weiteres Modell im Notebook `02`: `claude-haiku-4-5-20251001` (für einfache Demos)

---

## Projektstruktur

```
pjc3/
├── 01_getting_started.ipynb   # Tool-Use-Workflow (4 Schritte)
├── 02_messages_format.ipynb   # Messages-API-Format & Konversationshistorie
├── nova_claude.py             # Streaming-Chatbot mit farbiger Ausgabe
├── chatbot.py                 # Einfacher Multi-Turn-Chatbot (kein Streaming)
├── generate_questions.py      # Fragengenerator mit stop_sequences + dotenv
├── requirements.txt           # Python-Abhängigkeiten
├── .gitignore                 # venv/, .env, __pycache__, *.pyc ausgeschlossen
└── CLAUDE.md                  # Diese Datei
```

### Datei-Details

#### `nova_claude.py` — Streaming-Chatbot
- Nutzt `client.messages.create(..., stream=True)` und iteriert über Chunks
- Gibt `content_block_delta`-Events aus (chunk.delta.text)
- Konversationshistorie wird als Liste `conversation` manuell gepflegt
- ANSI-Farben: Benutzereingabe in Blau (`\033[94m`), Antwort in Grün (`\033[92m`)
- **Kein** `load_dotenv()` — `ANTHROPIC_API_KEY` muss vorab in der Shell gesetzt sein

#### `chatbot.py` — Einfacher Multi-Turn-Chatbot
- Blockierendes API-Call (`response.content[0].text`), kein Streaming
- System-Prompt: `"You are a helpful assistant. Be concise and friendly."`
- Konversationshistorie in `conversation_history`; `max_tokens=500`
- **Kein** `load_dotenv()` — API-Key muss in der Shell verfügbar sein

#### `generate_questions.py` — stop_sequences Demo
- Einzige Datei, die `load_dotenv()` aufruft → liest `.env` automatisch
- Demonstriert `stop_sequences`: Generierung stoppt vor Frage `num_questions + 1`
- Funktion `generate_questions(topic, num_questions=3)` — einfach anpassbar
- Standard-Aufruf: Thema `"free will"`, 3 Fragen

#### `01_getting_started.ipynb` — Tool Use (4-Schritte-Workflow)
1. Tool-Funktion schreiben (`get_stock_price` mit Mock-Daten)
2. Tool-Definition (Name, Beschreibung, JSON-Schema) + API-Request senden
3. Tool-Use-Block aus Antwort extrahieren (`stop_reason: "tool_use"`)
4. Tool ausführen → Ergebnis als `tool_result` an Claude zurückgeben
- Modell: `claude-opus-4-6`
- Nutzt `load_dotenv()` + `os.getenv("ANTHROPIC_API_KEY")`

#### `02_messages_format.ipynb` — Messages-API
- Erklärt das `messages`-Format: `role` (`"user"` / `"assistant"`) + `content`
- Zeigt Ein- und Mehr-Nachrichten-Konversationen
- Wichtige Regel: user und assistant müssen sich abwechseln
- Modell: `claude-haiku-4-5-20251001`

---

## Befehle

```bash
# Umgebung vorbereiten
source venv/bin/activate

# API-Key setzen (falls kein load_dotenv)
export ANTHROPIC_API_KEY=sk-ant-...

# Skripte starten
python nova_claude.py        # Streaming-Chatbot
python chatbot.py            # Einfacher Chatbot
python generate_questions.py # stop_sequences Demo

# Notebooks
jupyter notebook
```

---

## API-Key-Handling (wichtig)

| Datei | `load_dotenv()` | Voraussetzung |
|---|---|---|
| `generate_questions.py` | Ja | `.env` mit `ANTHROPIC_API_KEY=...` |
| `01_getting_started.ipynb` | Ja | `.env` mit `ANTHROPIC_API_KEY=...` |
| `02_messages_format.ipynb` | Ja | `.env` mit `ANTHROPIC_API_KEY=...` |
| `nova_claude.py` | **Nein** | `export ANTHROPIC_API_KEY=...` in Shell |
| `chatbot.py` | **Nein** | `export ANTHROPIC_API_KEY=...` in Shell |

`.env`-Beispiel (nicht committen!):
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

---

## Konventionen

- **Modellwahl**: `claude-sonnet-4-6` als Standard, `claude-opus-4-6` für Tool Use, `claude-haiku-4-5-20251001` für schnelle/günstige Demo-Calls
- **Streaming vs. Blocking**: `nova_claude.py` streamt; alle anderen Skripte und Notebooks nutzen blockierende Calls
- **Konversationshistorie**: Manuell als Python-Liste verwaltet (`conversation` / `conversation_history`)
- **Keine externe State-Verwaltung**: Kein Redis, keine DB — alles in-memory pro Session
- **Stop-Sequenzen**: `generate_questions.py` zeigt das Muster `stop_sequences=[f"{n+1}."]`

---

## Git-Workflow

```bash
# Nach freshly Clone
git remote set-head origin main

# Feature-Branch-Entwicklung
git checkout -b claude/<feature-name>
git push -u origin claude/<feature-name>
```

Commit-History (Konvention aus bisherigen Commits):
- `docs:` — CLAUDE.md und Dokumentation
- `Add` — neue Skripte/Notebooks ohne Präfix
- Kurze, beschreibende Commit-Messages auf Englisch

---

## MCP-Server (verfügbar)

| Name | URL / Command | Zweck |
|------|---------------|-------|
| n8n | `https://n8n.novachris.de/mcp-server/http` | Automation, Telegram, PDF |
| filesystem | `@modelcontextprotocol/server-filesystem` | Lokale Dateien |
| memory | `@modelcontextprotocol/server-memory` | Session-Persistenz |

Skill-Entscheidung: MCP vs. REST API → siehe `@.claude/skills/n8n-workflow-manager/SKILL.md`

---

## Docker-Sicherheit: UID-Namespace-Isolation

### Bedrohung
Container-Root (UID 0) kann bei einem Container-Escape direkt auf das Host-Dateisystem
zugreifen. Ohne UID-Mapping hat jeder Container-Prozess effektiv root-Rechte auf dem Host.

### Schutz-Mechanismus: Non-Root User Mapping

**Host-Setup** (einmalig als root, `setup-agent-isolation.sh`):

```bash
sudo bash setup-agent-isolation.sh
```

Erstellt dedizierte System-User ohne Login-Shell:

| Agent | UID:GID | Verzeichnis | Rechte |
|---|---|---|---|
| CLAUDE | 1001:1001 | `/srv/agents/CLAUDE` | `700` (kein Cross-Access) |
| GRAVITY | 1002:1002 | `/srv/agents/GRAVITY` | `700` |
| NEXUS | 1003:1003 | `/srv/agents/NEXUS` | `700` |

**Container-Konfiguration** (`docker-compose.yml`):

```yaml
user: "${AGENT_UID}:${AGENT_GID}"   # Nie root
security_opt:
  - no-new-privileges:true          # Kein setuid/setgid-Escalation
volumes:
  - ./config:/app/config:ro         # Config immer read-only
```

**Wie es zusammenwirkt:**

| Schicht | Mechanismus | Schutz |
|---|---|---|
| User-Mapping | Container läuft als UID 1001–1003 | Kein root auf dem Host |
| `chmod 700` | Verzeichnis nur für eigene UID lesbar | Kein Cross-Agent-Zugriff |
| `no-new-privileges` | Blockiert Privilege Escalation via setuid | Kein nachträglicher root-Gain |
| Config `read_only` | Volume-Mount schreibgeschützt | Container kann Config nicht manipulieren |

### Wichtige Regel für AI-Assistenten
- **Niemals** `user: root` oder `user: "0:0"` in `docker-compose.yml` setzen
- UID-Zuweisungen sind **fest** — zwei Agenten dürfen niemals die gleiche UID teilen
- `setup-agent-isolation.sh` nur als root auf dem Docker-Host ausführen, nicht im Container

---

## Docker-Sicherheit: Cross-Project Contamination

### Bedrohung
`docker compose down` **ohne** `-p`-Flag terminiert alle Container **aller** Agenten auf dem Host —
nicht nur die des aktuellen Projekts. In Multi-Agenten-Umgebungen kann ein einzelner Fehler
den Betrieb anderer Projekte zerstören.

### Schutz-Mechanismus: `Makefile`
Das `Makefile` erzwingt namespace-isolierte Docker-Operationen:

```bash
# Immer mit explizitem AGENT_NAMESPACE starten
AGENT_NAMESPACE=myagent make up
AGENT_NAMESPACE=myagent make down   # Fragt zur Bestätigung
AGENT_NAMESPACE=myagent make ps
AGENT_NAMESPACE=myagent make logs
```

**Wie es funktioniert:**

| Mechanismus | Beschreibung |
|---|---|
| `AGENT_NAMESPACE` Pflichtfeld | `make` bricht ab, wenn Variable nicht gesetzt ist (`$(error ...)`) |
| `COMPOSE_PROJ` Präfix | Jeder Docker-Aufruf nutzt `-p $(AGENT_NS)-pjc$(PROJ_ID)` — kein globaler Default |
| `down` mit Bestätigung | Interaktiver `read`-Prompt verhindert versehentliches Ausführen |
| Audit-Logging | Jede Operation wird nach `/var/log/docker-projects/$(AGENT_NS)/audit.log` geschrieben |
| `logs` JSON-annotiert | Log-Zeilen werden via `jq` mit `agent` und `project` angereichert |

### Fachbegriffe

- **Compose Project Scope**: Logische Docker-Ressourcen-Gruppierung unter eindeutigem Präfix (`-p`-Flag).
  Netzwerke, Volumes und Container sind nur innerhalb dieses Scopes sichtbar und werden nur von
  Befehlen mit passendem `-p`-Flag betroffen.

- **Blast Radius Containment**: Architekturprinzip, das Fehlerauswirkungen auf einen klar definierten
  Scope begrenzt. Ein Fehler in Projekt `agentA-pjc001` kann Projekt `agentB-pjc002` nicht treffen.

### Wichtige Regel für AI-Assistenten
**Niemals** `docker compose down`, `docker compose stop` oder `docker compose rm` ohne `-p`-Flag
in diesem Repository ausführen. Immer das `Makefile` nutzen oder explizit `-p <compose-project>` angeben.

---

## Bekannte Einschränkungen (Claude Code)

- Langer Paste-Text erscheint als `[Pasted text #N +M lines]` — Inhalt kommt nicht bei Claude an
  → Workaround: Text in Datei speichern und mit `@/pfad/zur/datei.md` referenzieren
- `nova_claude.py` und `chatbot.py` haben kein `load_dotenv()` — bei diesen Skripten muss `ANTHROPIC_API_KEY` bereits in der Shell gesetzt sein
