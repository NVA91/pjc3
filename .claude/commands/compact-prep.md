---
description: Checkliste vor /compact — Plan, CLAUDE.md, Memory sichern
---

Führe diese Checkliste durch, bevor /compact aufgerufen wird:

**1. Plan-Status prüfen**
Lies `/home/ubhp-nova/claude-c/pjc3/CLAUDE.md` → Abschnitt "Aktive Pläne".
Frage: Ist der nächste Schritt für Prio 1 korrekt und aktuell?
Falls nicht → CLAUDE.md aktualisieren, dann committen.

**2. weiter.md prüfen**
Lies `/home/ubhp-nova/claude-c/pjc3/.claude/commands/weiter.md`.
Frage: Verweist sie dynamisch auf CLAUDE.md (kein hardcodierter Pfad)?
Falls hardcodiert → reparieren, dann committen.

**3. Memory-Eintrag**
Prüfe ob in dieser Session Entscheidungen, Erkenntnisse oder Architekturänderungen gemacht wurden.
Falls ja → doc-agent aufrufen oder Eintrag manuell in passendes Memory-File schreiben.

**4. Git-Commit**
Führe aus: `git -C /home/ubhp-nova/claude-c/pjc3 status`
Alle relevanten Änderungen committed? Falls nicht → committen.

**5. Abschluss-Meldung**
Berichte: "Bereit für /compact — [was gesichert wurde]"

**STOP-Regel:** pjc3-viz1 = TABU.
