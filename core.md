# core.md — Aegis Core (Zentraler Router)

**Jeder Agent liest diese Datei zuerst.**

---

## Pyramide

```
pjc3/  ← EINZIGE Steuerzentrale
├── pjc3-docker/  → Verwalter: .claude/agents/verwalter.md
└── pjc3-viz1/    → Verwalter: .claude/agents/verwalter.md
```

Kein Agent greift direkt über Repo-Grenzen. Änderungen in Sub-Repos → Ticket an Verwalter.

---

## Zuständigkeiten

| Bereich | Zuständig | Wo |
|---|---|---|
| Claude API, MCP, Chatbots | pjc3 direkt | dieses Repo |
| Home-Infrastruktur, Docker | pjc3-docker Verwalter | `/home/ubhp-nova/claude-c/pjc3-docker/` |
| PDF-Analyse, Streamlit | pjc3-viz1 Verwalter | `/home/ubhp-nova/claude-c/pjc3-viz1/` |
| Langzeitgedächtnis | doc-agent | `.claude/agents/doc-agent.md` |

---

## Ticket-System (Cross-Repo)

Wenn pjc3 etwas in einem Sub-Repo ändern will:

```
TICKET
  Von: pjc3
  An: [pjc3-docker|pjc3-viz1] Verwalter
  Aufgabe: <exakte Beschreibung>
  Dateien: <betroffene Dateien>
  Erwartetes Ergebnis: <Verifikationskriterium>
```

Der Verwalter entscheidet ob das Ticket REGEL.md-konform ist. Bei Konflikt: sofortiger Abbruch.

---

## Langzeitgedächtnis — Kategorien

→ [`/memory/MEMORY.md`](/home/ubhp-nova/.claude/projects/-home-ubhp-nova-claude-c-pjc3/memory/MEMORY.md)

| Kategorie | Dateipräfix | Inhalt |
|---|---|---|
| Projekt-Status | `project_` | Offene Aufgaben, Repo-Status |
| Hierarchie & Routing | `arch_` | Pyramide, Verwalter, Direktiven |
| Skills & Konfiguration | `reference_skills_` | Skill-Pfade, Standards |
| Referenz & Best Practices | `reference_` | Bewährte Muster |

**Regel:** Temporäre Arbeitsvermerke werden nach Aufgabenabschluss gelöscht. Nur finaler Bericht bleibt.

---

## Globales Plugin-Inventar (Marketplace)

> Quelle: `~/.claude/settings.json` → `enabledPlugins` + `~/.claude/local-plugins/`

| Plugin | Quelle | Zweck |
|--------|--------|-------|
| superpowers | claude-plugins-official | Skills, Plans, Brainstorming, Workflows |
| code-review | claude-plugins-official | PR-Reviews, Code-Analyse |
| claude-md-management | claude-plugins-official | CLAUDE.md Audit & Update |
| pr-review-toolkit | claude-plugins-official | PR-Toolset (Tests, Typen, Kommentare) |
| commit-commands | claude-plugins-official | Git commit/push/PR Workflows |
| context7 | claude-plugins-official | Bibliotheks-Dokumentation live |
| agent-sdk-dev | claude-plugins-official | Claude Agent SDK Apps |
| skill-creator | claude-plugins-official | Skill erstellen, evaluieren, deployen |
| plugin-dev | claude-plugins-official | Plugin-Entwicklung (Hooks, Commands, Agents) |
| pyright-lsp | claude-plugins-official | Python LSP / Typchecking |
| security-guidance | claude-plugins-official | Security-Analyse & Guidance |
| qodo-skills | claude-plugins-official | PR-Resolver mit Qodo |
| claude-code-setup | claude-plugins-official | Automation-Empfehlungen für neues Projekt |
| code-helper | local (`~/.claude/local-plugins/`) | Intent-Routing, Code-Klassifikation, NOVA_ROADMAP |
| github | claude-plugins-official | **installiert, nicht aktiviert** — in `settings.json` fehlt der Eintrag |

---

## MCP-Server-Inventar

> Quellen: global `~/.claude.json` → `mcpServers` · cloud via claude.ai

| Name | Konfiguriert in | Zweck |
|------|----------------|-------|
| memory | `~/.claude.json` global | Session-Persistenz (KV-Store) |
| deepwiki | `~/.claude.json` global | GitHub-Repo-Dokumentation |
| ETL_Controller | `~/.claude.json` global | `mcp_gateway.py` → `extractor.py` → Radar |
| context7 | claude.ai cloud connector | Bibliotheks-Doku live abrufen |
| n8n | claude.ai cloud connector | Automation, Telegram, PDF-Workflows |
| Notion | claude.ai cloud connector | Notion-Integration |

**Lücken:** Kein MCP für pjc3-docker (kein Bedarf — Infra-Agent lokal). pjc3-viz1 TABU.

---

## Skills-Inventar

> Quelle: `pjc3/.claude/skills/`

| Skill | Pfad | Zweck |
|-------|------|-------|
| code-helper | `.claude/skills/code-helper/SKILL.md` | Intent-Routing: Label ausgeben, NOVA_ROADMAP checken |
| shell-scripting-skill | `.claude/skills/shell-scripting-skill/SKILL.md` | ETL, CSV, Excel, Diagramme, Shell-Automation |

**code-helper Sub-Skills** (`~/.claude/local-plugins/code-helper/skills/`):

| Sub-Skill | Zweck |
|-----------|-------|
| code-creation | Code-Generierung |
| mcp-guard | MCP-Sicherheit |
| sec-guard | Security-Checks |
| system-health | System-Gesundheit |

> Governance-Docs: `SKILL_GOVERNANCE.md`, `SKILL_MATRIX.md`, `SKILL_MATRIX_BY_SKILL.md`

**Lücken:** Kein dedizierter Skill für Docker/Infra. Kein Skill für MCP-Entwicklung (plugin-dev-Plugin vorhanden). `github`-Plugin nicht aktiviert — Phase 1 klären ob gewünscht.

---

## Abbruch-Befehl

Unklarheit → **STOP** → User melden. Kein Raten. Keine Workarounds.
