# Audit Evidence Register (Phase 1)

## Zweck
Zentrale Nachweisliste für Governance-Audits.

## Primäre Artefakte
- `NOVA_ROADMAP.md` — strategische Leitlinie (Single Source of Truth).
- `.claude/skills/code-helper/00-router.md` — Pre-Flight Router-Regeln.
- `.claude/skills/code-helper/SKILL.md` — Aktivierungslogik des Master-Skills.
- `CLAUDE.md` — dokumentierter Pflichtablauf inkl. Intent-Schema.

## Matrix-Nachweise
- `~/.claude/local-plugins/code-helper/skills/SKILL_MATRIX.md` — Intent-Perspektive.
- `~/.claude/local-plugins/code-helper/skills/SKILL_MATRIX_BY_SKILL.md` — Skill-Perspektive.
- `~/.claude/local-plugins/code-helper/skills/SKILL_GOVERNANCE.md` — Grenzen & Anti-Pattern.

## Sicherheits-/Betriebsnachweise
- `mcp_gateway.py` — FastMCP-Gateway mit sicherem Subprocess-Aufruf (Array-Form, Error-Handling).
- `~/.claude.json` — lokaler MCP-Server-Eintrag für `etl_controller`.
- `~/.claude_memory.jsonl` — persistierte Regel `Regel_Architektur_Roadmap`.

## Audit-Status (aktuell)
- Routing: vorhanden
- Governance-Matrix: vorhanden
- Completeness-Check: bestanden
- Test-Readiness: vorbereitet
