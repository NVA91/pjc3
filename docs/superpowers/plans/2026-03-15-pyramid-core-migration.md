# Plan: Pyramiden-Architektur — Aegis Core & Satellit-Repos

> **Status:** In Arbeit — Phase 0 ✅ erledigt · Phase 1 läuft
> **Fortsetzen:** `/weiter`

---

## Ziel-Architektur

```
┌─────────────────────────────────────────────┐
│  pjc3/  ← Spitze — global, isoliert         │
│  Plugins (Claude Marketplace), Skills,       │
│  Commands, Aegis Core, Langzeitgedächtnis    │
├─────────────────────────────────────────────┤
│  Aegis Core (core.md)                        │
│  Orchestrator-Agent — routet, delegiert,     │
│  kennt alle Satellit-Repos + ihre Grenzen    │
├──────────────┬──────────────────────────────┤
│  pjc3-docker │  pjc3-viz1  │  weitere...    │
│  Infra-Agent │  Viz-Agent  │  je 1 Agent    │
│  GitHub Repo │  GitHub Rep │  GitHub Repo   │
├─────────────────────────────────────────────┤
│  VS Code Workspace  ← unter pjc3            │
│  Arbeitsplatz nach Repo-Regeln konfiguriert  │
├─────────────────────────────────────────────┤
│  Linux (Host)  ← Basis, unterste Ebene      │
└─────────────────────────────────────────────┘
```

---

## Kernprinzipien

### 1. pjc3 = Globale Steuerzentrale
- Globale Plugins (Claude Marketplace) leben hier
- Skills, Commands, Hooks wirken global nach unten
- Isoliert — kein Satellit-Repo greift hier rein

### 2. Aegis Core — Orchestrator-Agent
- Einziger Eintrittspunkt für repo-übergreifende Aufgaben
- Kennt: Zuständigkeiten aller Repos, aktive Pläne, Grenzen
- Routet: Aufgabe kommt rein → Aegis Core → richtiger Satellit-Agent
- Darf NICHT: selbst in Satellit-Repos schreiben — nur delegieren

### 3. Satellit-Repos — Experten, keine Überschneidungen
- Jedes Repo = 1 Experte, 1 Zuständigkeit, 1 GitHub Repo
- Eigener Agent pro Satellit (`.claude/agents/verwalter.md`)
- Agent kennt nur sein eigenes Repo — greift nicht in andere ein
- Kein grep über Repo-Grenzen

### 4. Dokumentations-Subagent (doc-agent)
- Läuft im Hintergrund jeder Session mit
- Plottet Arbeitsschritte ins Archiv (Langzeitgedächtnis)
- Gedächtnis streng kategorisiert: `arch_`, `project_`, `feedback_`, `reference_`

### 5. Token-Hack — schlankes Context Window
- Temporäre Arbeitsvermerke: nur während der Aufgabe im Kontext
- Aufgabe erledigt → doc-agent trägt ins Archiv → Vermerke löschen
- `/clear` → Context Window leer → Memory-Index gibt präzisen Einstieg
- Kein wildes Suchen — jeder Agent weiß genau wo er sucht

### 6. VS Code Workspace unter pjc3
- `pjc3.code-workspace` nach Repo-Regeln konfiguriert
- Alle Satellit-Repos als Workspace-Folder eingebunden
- Einheitliche Einstellungen, Extensions, Formatierung

---

## Migrations-Phasen

### Phase 0 — Globales Inventar verankern (pjc3) ✅
- [x] **Plugins** (Claude Marketplace): 14 global (settings.json) + 1 lokal (code-helper)
- [x] **MCP Server**: 3 global (memory, deepwiki, ETL_Controller) + 3 cloud (context7, n8n, Notion)
- [x] **Skills**: code-helper + shell-scripting-skill
- [x] Alles in `core.md` eingetragen → Aegis Core kennt alle Plugins, MCP-Server und Skills
- [x] Lücken identifiziert: kein Infra-Skill, kein MCP für pjc3-docker (nicht nötig)

**Ziel:** pjc3 ist die einzige Quelle für globale Plugins, MCP-Server und Skills — kein Tool außerhalb dieser Kontrolle.

### Checkpoint 0→1 — Test & Doku
- [ ] **Test:** `core.md` manuell lesen — sind alle Plugins, MCPs, Skills korrekt gelistet?
- [ ] **Test:** Inventar gegen Live-State prüfen (`~/.claude/settings.json`, `~/.claude.json`, `.claude/skills/`)
- [ ] **Bereinigung:** `github`-Plugin deinstallieren (`~/.claude/plugins/`) — installiert aber nie aktiviert, kein Bedarf
- [ ] **Doku:** `CLAUDE.md` Abschnitt "MCP-Server" mit Inventar abgleichen — Abweichungen korrigieren

---

### Phase 1 — Aegis Core stärken (pjc3)
- [ ] `core.md` Header: `core.md` → **Aegis Core** (Kommentar im Header)
- [ ] Repo-Map vollständig: alle Satellit-Repos mit GitHub-URL + Agent-Pfad + Zuständigkeit
- [ ] Routing-Logik ausformulieren: wann delegiert Aegis Core an welchen Verwalter?
- [ ] Grenzen explizit: was darf Aegis Core nicht selbst tun?

### Checkpoint 1→2 — Test & Doku
- [ ] **Test:** Routing-Logik mit 3 Szenarien durchspielen (pjc3-intern, pjc3-docker, repo-übergreifend)
- [ ] **Test:** Ticket-Format in `core.md` — ist es vollständig und eindeutig?
- [ ] **Doku:** `CLAUDE.md` Abschnitt "Agenten-Hierarchie" gegen `core.md` abgleichen — sync?
- [ ] **Doku:** Memory-Eintrag `arch_hierarchie.md` aktualisieren falls nötig

---

### Phase 2 — Satellit-Agenten anlegen
- [ ] **Git-Entkopplung:** `pjc3-docker` Remote lösen — Verwalter startet in sauberem Zustand
- [ ] `pjc3-docker/.claude/agents/verwalter.md` anlegen — Infra-Experte
- [ ] Verwalter macht Einstandsbericht → `REPO-STATUS.md` generieren
- [ ] **Git-Neuverankerung:** Remote wieder setzen (gleiche URL, neuer Kontext)
- [ ] Jeder Agent: kennt nur sein Repo, lehnt repo-fremde Aufgaben ab

> **Hinweis:** pjc3-viz1 ist TABU — kein Verwalter bis explizit freigegeben.

### Checkpoint 2→3 — Test & Doku
- [ ] **Test:** pjc3-docker Verwalter mit Test-Ticket aktivieren — antwortet korrekt?
- [ ] **Test:** Verwalter reagiert auf repo-fremde Aufgabe → lehnt ab (kein Crash, kein Raten)
- [ ] **Doku:** `pjc3-docker/CLAUDE.md` prüfen — ist Verwalter-Eintrittspunkt dokumentiert?
- [ ] **Doku:** `core.md` Satellit-Map mit tatsächlichem Agent-Pfad aktualisieren

---

### Phase 3 — doc-agent ausbauen
- [ ] `doc-agent` in pjc3 als globalen Subagenten verankern
- [ ] Token-Hack formalisieren: Aufgabe-Ende-Ritual definieren
- [ ] `/clear`-Workflow dokumentieren

### Checkpoint 3→4 — Test & Doku
- [ ] **Test:** doc-agent nach einer Aufgabe starten — schreibt er korrekt ins Memory?
- [ ] **Test:** Temporäre Vermerke werden gelöscht, finale bleiben
- [ ] **Doku:** `/weiter`-Command prüfen — führt nach `/clear` korrekt zum nächsten Schritt?

---

### Phase 4 — VS Code Workspace
- [ ] `pjc3.code-workspace` aufräumen: alle Repos korrekt eingebunden
- [ ] Einstellungen: nach Repo-Regeln (kein wildes Formatieren, kein Auto-Commit)
- [ ] Extensions: minimal, bewusst gewählt

### Checkpoint 4→5 — Test & Doku
- [ ] **Test:** Workspace öffnen — alle Repos sichtbar, keine Fehler?
- [ ] **Doku:** Workspace-Konfiguration in `CLAUDE.md` oder README kurz festhalten

---

### Phase 5 — Linux Host anpassen
- [ ] Host-Konfiguration dokumentieren (was gehört zum Stack, was ist global)
- [ ] Trennung: Host-Dienste vs. pjc3-Stack

### Checkpoint 5 — Abschluss-Test & Doku
- [ ] **Test:** Vollständiger End-to-End-Durchlauf — Aufgabe rein, Aegis Core routet, Verwalter reagiert, doc-agent protokolliert
- [ ] **Doku:** Plan als abgeschlossen markieren, CLAUDE.md "Aktive Pläne" bereinigen
- [ ] **Doku:** Lessons Learned ins Memory schreiben (`project_pyramid_architecture.md` aktualisieren)

---

### Phase 6 — Cache-Bereinigung (nach vollständigem Abschluss)
- [ ] `~/.claude/cache/` leeren — Altlasten, Artefakte, falsche Überbleibsel entfernen
- [ ] Prüfen ob Überbleibsel aus alten Sessions vorhanden sind die nicht ins Inventar passen
- [ ] **Erst ausführen wenn:** alle Phasen + Checkpoint 5 bestanden — niemals mittendrin

**Ziel:** Sauberer Ausgangszustand für Dauer-Tests.

### Phase 7 — Dauer-Tests einrichten (nach Cache-Bereinigung)
- [ ] Checkpoint-Agent mit Zeitplan konfigurieren (periodische Verifikation)
- [ ] Aegis Core + alle Verwalter im Dauer-Test erfassen
- [ ] Fehlschlag-Protokoll definieren: was passiert wenn ein Verwalter nicht antwortet?

---

## Ausführungsreihenfolge

1. **Marketplace Plugins (Phase 0)** — Inventar, alles in pjc3 verankern
2. **Aegis Core (Phase 1)** — Core kennt alle Plugins + Repos + Grenzen
3. **Stack-Inbetriebnahme** — Core kennt pjc3-docker, läuft sauber durch
4. **Phase 2+ (Satellit-Agenten)** — erst wenn Core stabil läuft

## Was NICHT angefasst wird

- `pjc3-viz1` — TABU, nicht lesen, nicht anfassen, bis explizit freigegeben
- Bestehende Funktionalität — Migration ohne Breaking Changes
- Satellit-Repos ohne expliziten Auftrag — Phase 2 erst nach Phase 1

---

## Kritische Dateien

| Datei | Rolle |
|-------|-------|
| `pjc3/core.md` | Aegis Core — wird überarbeitet |
| `pjc3/.claude/agents/doc-agent.md` | Doku-Subagent — wird ausgebaut |
| `pjc3/pjc3.code-workspace` | VS Code Workspace |
| `pjc3-docker/.claude/agents/verwalter.md` | Infra-Agent — neu |
| `pjc3-viz1/.claude/agents/verwalter.md` | Viz-Agent — neu |

---

## Nächster Schritt

**Checkpoint 0→1:** Inventar in `core.md` verifizieren, dann Phase 1 starten.
Kein Überspringen — Checkpoint muss bestanden sein bevor die nächste Phase beginnt.
