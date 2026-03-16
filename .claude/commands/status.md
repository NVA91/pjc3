---
description: Session-Überblick — Pläne, Git, offene Tasks
---

Gib einen kompakten Überblick in 4 Blöcken:

**1. Aktive Pläne**
Lies `/home/ubhp-nova/claude-c/pjc3/CLAUDE.md` → Abschnitt "Aktive Pläne".
Zeige Tabelle: Prio | Plan | Nächster Schritt.

**2. Git-Status**
Führe aus: `git -C /home/ubhp-nova/claude-c/pjc3 log --oneline -5`
Zeige die letzten 5 Commits + aktuellen Branch.

**3. Offene Tasks (Memory)**
Lies `/home/ubhp-nova/.claude/projects/-home-ubhp-nova-claude-c-pjc3/memory/MEMORY.md`.
Zeige nur Einträge unter "Offene Aufgaben" falls vorhanden.

**4. Nächster Schritt**
Eine Zeile: was ist jetzt zu tun (Prio 1 aus den Plänen).

**STOP-Regel:** pjc3-viz1 = TABU.
