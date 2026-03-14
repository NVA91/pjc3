# REGEL.md — pjc3 (Hauptrepo)

## Einordnung
Dieses Repo ist das **Hauptrepo** der Claude-Arbeitsumgebung.
Es liegt unter: `/home/ubhp-nova/claude-c/pjc3/`

Alle 3 Repos sind **gleichrangig und unabhängig**:
```
/home/ubhp-nova/claude-c/
├── pjc3/          ← dieses Repo (Hauptrepo: Claude API, Skills, Agents)
├── pjc3-docker/   ← eigenständiges Repo (Home-Infrastruktur)
└── pjc3-viz1/     ← eigenständiges Repo (PDF-Analyse-Tool)
```

---

## Unverbrüchliche Regeln

### Isolation
- Dieses Repo arbeitet **ausschließlich** in `/home/ubhp-nova/claude-c/pjc3/`
- Kein Zugriff auf Dateien anderer Repos ohne explizite Nutzeranweisung
- Keine Symlinks die auf Verzeichnisse **außerhalb** dieses Repos zeigen
- Keine globalen `pip install` — ausschließlich systemweites Python (kein venv hier)

### Cross-Repo-Verbote
- Kein Lesen, Schreiben, Verändern von `pjc3-docker/` oder `pjc3-viz1/` ohne Auftrag
- Kein Kopieren von Konfigurationen zwischen Repos
- Kein Erstellen von Verweisen (Symlink, Hardlink, relative Pfade) auf andere Repos

### Git
- Remote: ausschließlich das GitHub-Repo dieses Projekts
- Branch-Schema: `claude/<feature-name>`
- Commits nur in diesem Repo — kein Cross-Repo-Commit

### Aufgaben
- Offene Aufgaben immer explizit benennen
- Erledigte Aufgaben sofort als erledigt markieren
- Keine Aufgabe gilt als "erledigt" ohne Verifikation

---

## Was dieses Repo enthält
- Claude API Experimente (Notebooks, Chatbots, MCP)
- Globale Skills und Agents für Claude Code (`.claude/`)
- MCP Gateway (`mcp_gateway.py`), Radar (`radar.py`)
- Docker-Template für Agent-Container (`docker-compose.yml`)

---

## Abbruch-Befehl
Bei JEDER Unklarheit zu Architektur, Auftrag oder Kontext: **Arbeit SOFORT einstellen.**
Konflikt an den User melden. Kein Weitermachen auf Verdacht. Keine Workarounds.

## Verstöße
Jede Aktion die gegen diese Regeln verstößt ist **ungültig und rückgängig zu machen**.
Der Nutzer ist sofort zu informieren.
