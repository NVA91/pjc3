---
name: code-helper
description: >
  Pre-Flight Master-Skill für alle neuen Aufgaben. Erzwingt zuerst Intent-Routing,
  optionalen Roadmap-Check für Architekturentscheidungen und erst danach Ausführung.
categories:
  - name: Routing
    description: Intent-Klassifikation, Scope-Check, Ausführungsstart
triggers:
  - Neue Aufgabe starten
  - Unklare Anfrage klassifizieren
  - Vor Codeänderungen Intent festlegen
  - Architektur- oder Strategieentscheidung treffen
  - Expliziter Aufruf via /code-helper
resources:
  - 00-router.md
---

## Aktivierungsregel
Wende diesen Skill am Beginn jeder neuen Aufgabe an.

## Ausführungsregel
1. Nutze zuerst `00-router.md` als Pre-Flight-Check.
2. Gib als erste sichtbare Zeile ein Intent-Label im Format `[Intent: ...]` aus.
3. Falls Intent `architecture` oder strategischer Scope: lies zuerst `NOVA_ROADMAP.md`.
4. Starte erst danach Umsetzung, Tools oder Codeänderungen.

## Priorität
Dieser Skill hat Vorrang vor optionalen Stil- oder Komfort-Regeln,
wenn eine neue Aufgabe beginnt und noch kein Intent gesetzt wurde.
