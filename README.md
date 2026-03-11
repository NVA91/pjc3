# pjc3

Python-Lernprojekt für die Anthropic API mit optionalem Docker-Container-Setup.

## Python-Container nutzen

### 1) Image bauen

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 COMPOSE_PROJECT_NAME=pjc003 docker compose build app
```

### 2) Container starten

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 COMPOSE_PROJECT_NAME=pjc003 docker compose up -d app
```

### 3) Python im Container ausführen

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 COMPOSE_PROJECT_NAME=pjc003 docker compose exec app python --version
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 COMPOSE_PROJECT_NAME=pjc003 docker compose exec app python chatbot.py
```

### 4) Container stoppen

```bash
AGENT_NAMESPACE=CLAUDE AGENT_UID=1001 AGENT_GID=1001 COMPOSE_PROJECT_NAME=pjc003 docker compose down
```

## Harte Guard-Regeln (Host)

Für sichere, projektisolierte Host-Befehle nutze den Guard:

```bash
make guard CMD='ls -la ./docs'
make guard CMD='cat ./README.md'
make guard CMD='grep TODO ./README.md'
```

Der Guard in `safe-project-exec.sh` erzwingt:

- Nur read-only Whitelist-Befehle (`ls`, `cat`, `head`, `tail`, `grep`, `awk`, `sed`)
- Kein Path-Hopping (`..` ist verboten)
- Keine Shell-Operatoren/Chaining (`;`, `&&`, `||`, `|`, `>`, `<`, `$()`, Backticks)
- `grep` nur mit expliziter Flag-Allowlist (`-i`, `-n`, `-c`, `-v`, `-w`, `-x`, `-e`) und nur auf expliziten Dateien (kein `-r`, `-R`, `--recursive`, kein `.`/`/` als Ziel)
- `awk`/`sed`: Blockiert `-f`, `--file` und `-F` (Schutz gegen Flag-Semantik-/Code-File-Missbrauch)
- Zugriff nur innerhalb dieses Projekts (`pjc3`)

## Enthaltene Container-Dateien

- `Dockerfile` (Python 3.12 slim, installiert `requirements.txt`)
- `docker-compose.yml` (Build + Security-Settings + `sleep infinity`)
- `.dockerignore` (kleiner/sicherer Build-Kontext)
- Ordner `data/`, `config/`, `secrets/` als vorbereitete Mount-Ziele
