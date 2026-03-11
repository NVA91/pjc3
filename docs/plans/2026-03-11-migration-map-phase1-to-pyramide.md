# Migration Map — Phase 1 zu MCP-Pyramidenmodell

Ziel: Bestehende Phase-1-Artefakte systematisch auf das zukünftige 5-Layer-Modell abbilden und die Übernahme planbar machen.

## Mapping-Tabelle

| Phase-1-Artefakt (Ist) | Aktueller Ort | Ziel-Layer | Ziel-Artefakt (Soll) | Nächster Migrationsschritt | Done-Kriterium |
|---|---|---|---|---|---|
| Pre-Flight Router | `.claude/skills/code-helper/00-router.md` | Layer 1 (MCP) | `mcp-router.md` | Router-Logik in MCP-Router extrahieren und Intent-Mapping zentralisieren | Intent-Entscheidung läuft zentral über MCP-Router |
| Master-Skill Aktivierung | `.claude/skills/code-helper/SKILL.md` | Layer 1 (MCP) | `mcp.py` + `mcp-router.md` | Skill-Startregeln in Orchestrator-Entrypoint überführen | MCP startet routing-first ohne manuelle Skill-Vorwahl |
| Roadmap-Leitlinie | `NOVA_ROADMAP.md` | Layer 1 + Layer 5 | `mcp-router.md` (Policy-Hook) + `CLAUDE.md` (Leitplanke) | Architektur-Gate als feste Vorbedingung im Router fest verankern | Architekturfragen erzwingen Roadmap-Check vor Ausführung |
| ETL Gateway Tooling | `mcp_gateway.py` | Layer 1 (MCP) | `mcp.py` (Tool-Dispatch) | Bestehende Tool-Endpunkte in MCP-Dispatch-Registry überführen | Tool-Auswahl erfolgt über Intent + Registry statt direktem Aufruf |
| Skill Matrix (Intent-Sicht) | `~/.claude/local-plugins/code-helper/skills/SKILL_MATRIX.md` | Layer 2 + Layer 3 | `subagent/*/subagent-router.md` + `skills/*.md` | Intent-Zuordnung in Subagent-Router und atomare Skills aufteilen | Jeder Intent hat genau einen primären Subagent-Pfad |
| Skill Matrix (Skill-Sicht) | `~/.claude/local-plugins/code-helper/skills/SKILL_MATRIX_BY_SKILL.md` | Layer 2 | `subagent/context.md` | Verantwortungsgrenzen pro Subagent als Context-Verträge übernehmen | Scope-Grenzen je Subagent sind explizit dokumentiert |
| Governance Matrix | `~/.claude/local-plugins/code-helper/skills/SKILL_GOVERNANCE.md` | Layer 4 (Rules) | `global_rules.md` + `domain_rules.md` | Anti-Pattern/Constraints in globale + domänenspezifische Rules splitten | Alle Guard-Regeln liegen als zentrale Rulesets vor |
| Audit Checklist | `docs/audit/AUDIT_CHECKLIST.md` | Layer 4 (Rules) | `global_rules.md` Prüfsektion | Prüfpunkte als Rule-Compliance-Checks referenzieren | Audit-Checks sind direkt aus Rules ableitbar |
| Audit Evidence | `docs/audit/AUDIT_EVIDENCE.md` | Layer 4 + Layer 5 | `domain_rules.md` + `CLAUDE.md` Referenzindex | Nachweisstruktur an neue Layer-Artefakte binden | Evidence verweist nur noch auf Soll-Struktur |
| Audit Runbook | `docs/audit/AUDIT_RUNBOOK.md` | Layer 1–4 | `mcp.py` Betriebsablauf + Rule-Runbook | Ausführungsablauf an MCP-Orchestrierung anpassen | Runbook folgt tatsächlichem MCP-Laufweg |

## Priorisierte Übernahmereihenfolge

1. Layer 1 stabilisieren: `mcp-router.md`, danach `mcp.py` Entry.
2. Layer 2 aufspalten: Subagents mit klaren Domänen und Mini-Routern.
3. Layer 3 atomisieren: Skill-Dateien auf festes ROLE/GOAL/INPUT/TASKS/OUTPUT/RULES-Format bringen.
4. Layer 4 zentralisieren: Guards und Governance in `global_rules.md` + `domain_rules.md` zusammenführen.
5. Layer 5 schärfen: `CLAUDE.md` als unveränderliche Basis konsistent zum MCP-Layer halten.

## Guardrails für die Migration

- Keine Regression bei Security-Guards (`sec-guard`, `mcp-guard`, `system-health`).
- Keine Big-Bang-Migration: nur inkrementelle, testbare Übergänge.
- Jede Übernahme braucht einen sichtbaren Done-Nachweis im Audit-Pack.
