# Grafana Assistant — Design Spec

**Datum:** 2026-03-13
**Status:** Approved
**Projekt:** pjc3 — Claude API Lernprojekt
**Architektur-Phase:** Phase 1 (Kalibrierung) → Vorbereitung Phase 2

---

## Ziel

Ein on-demand Grafana-Assistent, der über Claude Tool Use und MCP erreichbar ist.
Hauptaufgaben: Dashboards erstellen, erklären, verbessern. Alerts nur auf Anfrage.
Kein Dauerbetrieb, kein Overhead-Monster — erweiterbar durch klar benannte Äste.

---

## Architektur

```
Claude Code (oben)
    └── mcp_gateway.py          ← grafana_assistent(aufgabe) MCP-Tool
            └── grafana_assistant.py    ← Standalone-Skript + importierbares Modul
                    ├── grafana_tools.py        ← Grafana REST API Funktionen
                    └── grafana_templates.py    ← Dashboard-Templates (Python-Dicts)
                            └── [Erweiterungsäste nach Bedarf]
```

---

## Dateien & Zweck

### `grafana_assistant.py` — Einstiegspunkt

- Standalone-Aufruf: `python grafana_assistant.py`
- Wird von `mcp_gateway.py` als Modul importiert
- Claude (`claude-opus-4-6`, Tool Use, Adaptive Thinking)
- Verhalten vor jeder Aktion:
  1. Aufgabe verstehen, max. 2 Rückfragen stellen
  2. Aufgabenliste ausgeben (`[ ] ...`)
  3. Schritt für Schritt ausführen, jeden Schritt bestätigen
- Lädt `GRAFANA_URL` + `GRAFANA_TOKEN` aus `.env` via `load_dotenv()`

### `grafana_tools.py` — Grafana REST API

```
# MEMORY: grafana_tools.py
# Erweiterungsäste: grafana_tools_prometheus.py, grafana_tools_loki.py
# Wenn Verbindung fehlschlägt: GRAFANA_URL + GRAFANA_TOKEN in .env prüfen
# Verknüpft mit: mcp_gateway.py → grafana_assistent(), grafana_templates.py
```

| Tool | Funktion | Fallback-Hinweis |
|------|----------|-----------------|
| `list_dashboards()` | Alle Dashboards auflisten | → GRAFANA_URL + Token prüfen |
| `get_dashboard(uid)` | Dashboard-JSON lesen + erklären | → UID aus list_dashboards |
| `get_alerts()` | Alert-Status abfragen | → nur auf Anfrage |
| `create_dashboard(template, vars)` | Dashboard via Template erstellen | → Template-Name muss existieren |
| `update_panel(uid, panel_id, changes)` | Einzelnes Panel anpassen | → Dashboard muss existieren |

### `grafana_templates.py` — Dashboard-Templates

```
# MEMORY: grafana_templates.py
# Erweiterungsäste: grafana_templates_network.py, grafana_templates_agents.py
# Format: Python-Dicts, direkt an Grafana API übergebar (kein YAML-Parser nötig)
# Verknüpft mit: grafana_tools.py → create_dashboard()
```

| Template | Diagrammtyp | Zweck |
|----------|-------------|-------|
| `system_overview` | Time series | CPU, RAM, Disk |
| `container_status` | Stat + Table | Docker-Container-Gesundheit |
| `agent_activity` | Bar chart | MCP/Agent-Aufrufe |
| `alert_summary` | Alert list | Aktive Alerts |
| `custom_blank` | Leer | Freie Erweiterung |

### `mcp_gateway.py` — Erweiterung (1 neues Tool)

Neues MCP-Tool wird ergänzt:
```python
@mcp.tool()
def grafana_assistent(aufgabe: str) -> str:
    """Grafana Dashboard erstellen, anpassen oder erklären."""
```

---

## Modell & Konfiguration

**Claude-Modell:** `claude-opus-4-6`, `thinking: {type: "adaptive"}`

`.env` (nicht committed):
```
GRAFANA_URL=http://localhost:3000
GRAFANA_TOKEN=glsa_...
```

`.env.example` (committed, als Dokumentation):
```
GRAFANA_URL=http://localhost:3000
GRAFANA_TOKEN=glsa_HIER_TOKEN_EINTRAGEN
```

**Token erstellen:** Grafana → Profile → Service Accounts → Token generieren (Rolle: Editor)

> ⚠️ `grafana_assistant.py` nutzt `load_dotenv()`.
> `mcp_gateway.py` nutzt **kein** `load_dotenv()` — Token muss in Shell exportiert sein (Projektkonvention).

**Fehlerbehandlung bei Verbindungsproblemen:**
- HTTP 401/403 → Hinweis: Token prüfen / neu generieren
- HTTP 404 → Hinweis: UID oder Dashboard existiert nicht
- Connection Error → Hinweis: `GRAFANA_URL` prüfen, Grafana läuft?
- Jeder Tool-Fehler gibt einen deutschen Hinweis zurück, Claude erklärt nächsten Schritt

---

## Claude-Verhalten (Tool Use Flow)

1. Nutzer beschreibt Aufgabe auf Deutsch
2. Claude stellt **Rückfragen** (Datasource? Zeitraum? Panel-Typ?) — Richtlinie: so wenig wie nötig, keine Endlosschleifen
3. Claude gibt Aufgabenliste aus:
   ```
   [ ] Vorhandene Dashboards prüfen
   [ ] Template auswählen: container_status
   [ ] Dashboard erstellen
   [ ] Ergebnis erklären
   ```
4. Claude führt Tools aus, meldet Fortschritt
5. Bei Fehler: deutscher Hinweis auf Ursache + konkreter nächster Schritt

**Alert-Scope:** `get_alerts()` ist **read-only** — nur Abfragen, kein Erstellen/Bestätigen von Alerts.
Erweiterung (acknowledge, create) → separater Ast `grafana_tools_alerts.py` bei Bedarf.

---

## Erweiterungsäste (vorbereitet, nicht implementiert)

| Datei | Zweck | Trigger |
|-------|-------|---------|
| `grafana_tools_prometheus.py` | PromQL-Queries | wenn Prometheus Datasource |
| `grafana_tools_loki.py` | Log-Panel-Abfragen | wenn Loki vorhanden |
| `grafana_templates_network.py` | Netzwerk-Dashboards | Caddy/Pi-hole Integration |
| `grafana_templates_agents.py` | Agent-Views | Nova-Framework Phase 2 |

---

## Nicht im Scope (bewusst ausgelassen)

- Dauerbetrieb / kontinuierliches Alert-Monitoring
- YAML-Template-Format (Python-Dicts reichen)
- Eigener MCP-Server-Prozess (mcp_gateway.py reicht)
- Prometheus/Loki-Integration (Erweiterungsast)

---

## Verknüpfung zur Architektur-Pyramide

- **Phase 1:** Tool Use Skript + MCP-Tool in bestehendem Gateway
- **Phase 2:** Erweiterungsäste nach Bedarf, Agent-spezifische Templates
- **Phase 3:** Grafana als Observability-Layer für das Nova Universe
