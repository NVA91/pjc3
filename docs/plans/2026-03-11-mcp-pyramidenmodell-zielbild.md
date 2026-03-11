# MCP Pyramidenmodell — Zielbild für zukünftige Übernahme

Dieses Dokument beschreibt das zukünftige Zielbild, das mit dem aktuellen Phase-1-Stand (Router + Governance + Guards) abgeglichen und schrittweise übernommen werden soll.

## Layer 1: MCP (Master Control Program)

**Rolle:** Router + Orchestrator auf höchster Ebene.
**Aufgabe:** User-Input annehmen, Intent bestimmen, Subagent wählen, Ergebnis aggregieren, finale Antwort liefern.

```text
MCP-Pseudocode:
1. input = user_message
2. intent = router_prompt(input)  # -> "codegen", "debug", "deploy"
3. subagent = select_subagent(intent)
4. result = subagent.process(input, context)
5. return format_result(result)
```

**Ziel-Dateien:** `mcp.py`, `mcp-router.md`

## Layer 2: Subagents (Spezialisierte Agenten)

**Rolle:** Teamlead pro Domäne; ruft passende Skills auf.

**Beispiele:**
- CodeGenAgent: `write_code`, `write_tests`, `refactor_code`
- DebugAgent: `fix_bug`, `explain_log`
- DevOpsAgent: `setup_tool`, `plan_task`, `deploy_infra`
- DocsAgent: `explain_concept`, `write_docs`

**Struktur pro Subagent:**
```text
subagent/
├── subagent-router.md
├── context.md
└── skills/
```

## Layer 3: Skills (Atomare Fähigkeiten)

**Rolle:** Spezifische Prompt-Templates mit festem Input/Output.

**Beispiele:**
```text
skills/
├── fix_bug.md
├── write_code.md
├── setup_tool.md
├── explain_log.md
└── refactor_code.md
```

**Skill-Format:**
```text
ROLE: [Role Definition]
GOAL: [One Sentence Goal]
INPUT: [Expected Input Format]
TASKS: [1-5 Numbered Steps]
OUTPUT: [Strict Output Format]
RULES: [Constraints/Limits]
```

## Layer 4: Rules (Verhaltensregeln)

**Rolle:** Harte Constraints und Best Practices für alle Skills/Subagents.

**Core Rules:**
1. Antworte immer strukturiert nach Output-Format.
2. Keine Halluzinationen, nur Input-basiert.
3. Maximal 500 Wörter pro Antwort.
4. Deutsche Sprache, englische Fachbegriffe.
5. Bei Unklarheit Rückfrage statt blindes Arbeiten.
6. Entscheidungen loggen: `[Intent: X] [Skill: Y]`.

**Ziel-Dateien:** `global_rules.md`, `domain_rules.md`

## Layer 5: Claude.md (System-Prompt Basis)

**Rolle:** Unveränderliche Identität und Verhaltensgrundsätze.

**Leitbild (gekürzt):**
- Präziser Technical Assistant
- Command-line first, token-effizient
- Security first (Least Privilege)
- Vollständige, nachvollziehbare Lösungen

**Pyramiden-Reihenfolge:**
1. MCP
2. Subagent
3. Skill
4. Rules
5. Claude.md

## Abgleich mit aktuellem Stand (Phase 1)

- Bereits vorhanden: Pre-Flight Router, Skill-Matrizen, Governance-Dokumente, Memory-Regel zur Roadmap.
- Nächster Ausbaupfad: Router-Intent -> Subagent-Router -> atomare Skills -> zentrale Rulesets.
- Übernahmeprinzip: Schrittweise Migration, ohne bestehende Guard-Sicherheit zu verlieren.
