# Design-Spec: Migration Agenten-Architektur

**Datum:** 2026-03-16
**Status:** Freigegeben — bereit für Implementierungsplan
**Projekt:** pjc3 — Aegis Core & Satellit-Repos

---

## Ziel

Eine vollständig isolierte, mehrstufige Agenten-Architektur aufbauen die:
- Bereiche konsequent einhält (kein Ordner-Hopping)
- Defense in Depth umsetzt (kein Single Point of Failure)
- Token-effizient arbeitet (jeder Agent liest nur was er braucht)
- Im Solo-Admin-Szenario sicher und wartbar bleibt

---

## Architektur — Pyramide

```
┌─────────────────────────────────────────────────────┐
│  GLOBAL (pjc3/)                                      │
│                                                      │
│  ┌──────────────┐    ┌────────────────────────────┐  │
│  │  Aegis Core  │◄──►│  Memory Agent              │  │
│  │  Orchestrator│    │  context7 | Vault | Local  │  │
│  └──────┬───────┘    └────────────────────────────┘  │
│         │  Hooks: PreToolUse / PostToolUse / SessionEnd│
│         │  → Filesystem Boundary erzwungen            │
│         │  → Memory-Checkliste beim Trigger           │
├─────────┼───────────────────────────────────────────┤
│  PROJEKT│                                            │
│  ┌──────▼──────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Forge       │  │Argus        │  │Nexus        │  │
│  │ je Satellit │  │Sentinel     │  │Projekt      │  │
│  │ Builder     │  │Reviewer     │  │Security     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
     + Nexus Global (systemweite Security-Checks)
```

---

## Agenten

### 1. Aegis Core — Orchestrator / Control Plane

**Typ:** Orchestrator
**Datei:** `pjc3/.claude/agents/aegis-core.md`

**Aufgabe:**
- Nimmt Aufträge an, zerlegt in Arbeitspakete, weist Agenten zu
- Generiert Task Envelopes pro Auftrag
- Erzwingt Regeln und Übergaben
- Holt Kontext vom Memory Agent (nicht selbst suchen)

**Darf:**
- Lesen (alle Repos)
- Tasks in `langzeitgedaechnis/tasks/` anlegen
- Agenten starten und stoppen — via Task Envelope + Hook-Dispatch (kein direktes Bash)

**Darf nicht:**
- Direkt Projektcode schreiben
- Global Regeln oder Settings ändern
- Bash direkt ausführen — Agenten-Start läuft über Claude Code Subagent-Dispatch

**Hinweis: Agenten-Start-Mechanismus**
Aegis Core startet Agenten nicht via Bash-Befehl. Er dispatcht Subagenten durch den Claude Code Subagent-Mechanismus (Task Envelope übergeben → Subagent startet mit Envelope als Kontext). Kein Prozess-Management nötig.

**Manifest-Header (Beispiel):**
```
AGENT: Aegis Core
ROLLE: Orchestrator
DARF: lesen, Tasks anlegen, Subagenten dispatchen
DARF NICHT: Projektcode schreiben, globale Settings ändern, Bash direkt
BEI UNKLARHEIT: Memory Agent befragen
```

---

### 2. Memory Agent — Knowledge Base

**Typ:** Memory Agent / Knowledge Base
**Datei:** `pjc3/.claude/agents/memory-agent.md`

**Aufgabe:**
- Erster Ansprechpartner für Aegis Core (Abfragen)
- Verwaltet Langzeitgedächtnis, Projekthistorie, Entscheidungen
- Archiviert bekannte Fehler, Architekturwissen, Aufgaben
- Verdichtet und strukturiert — kein simpler Log-Ordner

**3 Wissensbereiche:**

| Bereich | Quelle | Zugriff |
|---------|--------|---------|
| `context7` | externe Bibliotheks-Doku | MCP-Tool (read) |
| `Vault` | Geheimnisse | read-only, isoliert (kommt später) |
| `Local` | Projektgedächtnis, History, Tasks | read/write |

**SessionEnd-Checkliste (Hook-Trigger vor /clear):**
```
[ ] Offene Tasks archivieren (langzeitgedaechnis/tasks/)
[ ] Entscheidungen verdichten und eintragen
[ ] Bekannte Fehler dokumentieren
[ ] Aufgaben-Archiv aufräumen (alte löschen, neue anlegen)
[ ] Bestätigung → /clear darf starten
```

**Schreibbereiche im `langzeitgedaechnis/`:**
- `local/` — Projektgedächtnis, History, Entscheidungen (Memory Agent)
- `tasks/` — Task-Archive, aktive Envelopes (Memory Agent)
- `findings/` — Review- und Security-Findings (Argus + Nexus, NICHT Memory Agent)

**Darf nicht:**
- Direkt Source Code ändern
- Außerhalb von `langzeitgedaechnis/` schreiben
- In `findings/` schreiben — das ist Argus/Nexus-Domäne

---

### 3. Forge — Builder / Project Worker (je Satellit)

**Typ:** Builder
**Datei:** je Satellit z.B. `pjc3-docker/.claude/agents/forge.md`

**Aufgabe:**
- Implementiert Features, erstellt Dateien, passt Projektcode an
- Arbeitet frei — aber ausschließlich innerhalb seines Repos

**Manifest-Header (Beispiel Forge/pjc3-docker):**
```
AGENT: Forge/pjc3-docker
ROLLE: Builder
ROOT: /home/ubhp-nova/claude-c/pjc3-docker/
DARF: lesen + schreiben innerhalb ROOT, Bash innerhalb ROOT
DARF NICHT: außerhalb ROOT, Memory Agent direkt schreiben,
            globale Regeln ändern
BEI UNKLARHEIT: STOPP → Ticket an Aegis Core, nicht raten
HILFE: [Aegis Core] [Nexus-Projekt] [Argus nach Abschluss]
```

**Darf nicht:**
- Außerhalb von ROOT arbeiten
- Globale Regeln oder Settings ändern
- Direkt in Memory Agent schreiben
- Bei Unklarheit raten oder improvisiern — immer STOPP

---

### 4. Argus Sentinel — Independent Reviewer

**Typ:** Reviewer (kein Schreibrecht auf Code)
**Datei:** `pjc3/.claude/agents/argus-sentinel.md`

**Aufgabe:**
- Review nach jedem Forge-Abschluss
- Architekturprüfung, Stilprüfung, Übergabeprüfung, Diff-Analyse

**Trigger-Mechanismus:**
PostToolUse-Hook erkennt Forge-Abschluss → benachrichtigt Aegis Core → Aegis Core dispatcht Argus als Subagenten. Argus ist kein direkter Hook-Handler sondern wird von Aegis Core gerufen. Hook → Aegis Core → Argus.

**Darf:**
- Lesen (alle Repos)
- Review-Berichte schreiben
- Findings direkt in `langzeitgedaechnis/findings/` schreiben (eigener Schreibbereich, nicht über Memory Agent)

**Darf nicht:**
- Produktionscode ändern
- Tasks anlegen oder Agenten steuern
- In `langzeitgedaechnis/local/` oder `tasks/` schreiben (nur Memory Agent)

---

### 5. Nexus Global — Global Security Agent

**Typ:** Security (global)
**Datei:** `pjc3/.claude/agents/nexus-global.md`

**Aufgabe:**
- Systemweite Sicherheitsprüfungen: `~/.claude/`, `pjc3/`, globale Hooks, Settings
- Trigger: bei Änderungen an globalem Bereich
- Security-Finding → `langzeitgedaechnis/findings/` (sofort)

**Lese-Scope:** `~/.claude/`, `pjc3/` vollständig + Satellit-Repos read-only (Security-Checks erfordern Einblick in alle Repos — bewusste Ausnahme, nur lesen)

**Darf nicht:** Code ändern, in Satellit-Repos schreiben, Settings ändern

---

### 6. Nexus Projekt — Project Security Agent (je Satellit)

**Typ:** Security (projektspezifisch)
**Datei:** je Satellit z.B. `pjc3-docker/.claude/agents/nexus-projekt.md`

**Aufgabe:**
- Projektspezifische Sicherheitsprüfungen innerhalb ROOT
- Parallel zu Forge oder auf Anfrage von Aegis Core
- Security-Finding → `langzeitgedaechnis/findings/` (sofort, nicht warten auf /clear)

**Vollständige Isolation:** darf nicht außerhalb ROOT lesen oder schreiben

---

## Task Envelope

Aegis Core generiert pro Auftrag einen Task Envelope:

```
TASK-ENVELOPE
  ID:        task-YYYY-MM-DD-NNN
  Agent:     Forge/pjc3-docker
  Aufgabe:   <exakte Beschreibung>
  Scope:     /home/ubhp-nova/claude-c/pjc3-docker/
  Regeln:    [link REGEL.md]
  Tools:     [Nexus-Projekt für Security-Check]
  Übergabe:  Argus Sentinel prüft Ergebnis
  Offen:     nein / ja → Aegis Core fragen
```

**Speicherort:**
- Aktiv während Ausführung: `langzeitgedaechnis/tasks/active/task-YYYY-MM-DD-NNN.md`
- Nach Abschluss archiviert: `langzeitgedaechnis/tasks/archive/`
- Envelope-Datei als offener Punkt markiert (Format YAML vs. Markdown-Header noch offen)

Agent liest **nur seinen Envelope** — kein globaler Kontext, kein Suchen.

---

## Defense in Depth — 5 Schichten

### Schicht 1 — Software: PreToolUse Hook
Prüft Schreibzugriff vor Ausführung gegen ROOT des Agents.
Schwäche: Software-Schicht — kann bei Fehlkonfiguration fehlen.

### Schicht 2 — OS: POSIX Dateisystem-Rechte
Agent-User (UID 1001–1003) haben physisch keine Schreibrechte außerhalb ihres Repos.
Kernel blockiert — unabhängig vom Hook.

### Schicht 3 — Kernel: AppArmor Profile
Ein AppArmor-Profil pro Agent-Typ. Sitzt im Linux-Kernel — kein Prozess kommt daran vorbei.

**Konzeptuelles Beispiel** (vereinfacht — kein Copy-Paste, echte Syntax in eigener Implementierungs-Spec):
```
# Profil: forge-pjc3-docker (konzeptuell)
allow /home/ubhp-nova/claude-c/pjc3-docker/**  rw
allow /home/ubhp-nova/claude-c/pjc3/**          r
deny  /home/ubhp-nova/.claude/**                (kein Zugriff)
deny  /home/ubhp-nova/claude-c/pjc3/**          w  (lesen ja, schreiben nein)
```
Enforcement durch AppArmor — unabhängig von Hooks oder Agent-Verhalten.

### Schicht 4 — Container: Docker (zusätzliche Härtung)

**Anwendbarkeit:** Docker ist zusätzliche Härtung wenn Forge-Arbeit containerisiert läuft. Nicht-containerisierte Claude Code Subagenten verlassen sich auf Schichten 1–3. Docker erhöht die Sicherheit, ist aber kein Ersatz für Schicht 2+3.
```yaml
user: "1001:1001"
read_only: true
security_opt:
  - no-new-privileges:true
  - apparmor:forge-pjc3-docker
cap_drop: [ALL]
volumes:
  - ./pjc3-docker:/workspace:rw
  - ../pjc3:/context/pjc3:ro
```

### Schicht 5 — Audit: Argus Sentinel
Findet Verstöße, schreibt Finding direkt → `langzeitgedaechnis/findings/` → Aegis Core liest Findings und stoppt Agent bei Bedarf.

**Übersicht:**
```
Angriff / Fehler          │ stoppt durch
──────────────────────────┼──────────────────────────
Hook deaktiviert          │ Schicht 2 + 3
Falscher Pfad im Code     │ Schicht 1 + 2
Container-Ausbruch        │ Schicht 3 + 4
Agent schreibt zu viel    │ Schicht 5 (Argus)
Unbemerkte Änderung       │ Schicht 5 (Audit-Log)
```

---

## Capability-Matrix

| Agent | Read | Write | Bash | MCP |
|-------|------|-------|------|-----|
| Aegis Core | alle Repos | nur Tasks-Ordner | nein | nein |
| Memory Agent | alle | nur Local | nein | ja (context7, Vault) |
| Forge | ROOT | ROOT | ja (in ROOT) | nein |
| Argus Sentinel | alle | nur Findings | nein | nein |
| Nexus Global | global + Satelliten (r) | nur findings/ | read-only: ls,cat,find,grep | nein |
| Nexus Projekt | ROOT | nur findings/ | read-only: ls,cat,find,grep | nein |

---

## Implementierungsreihenfolge

**Kein Überspringen — jede Stufe muss stabil sein bevor die nächste beginnt.**

```
Stufe 1 — Fundament (Defense in Depth)
  → AppArmor-Profile anlegen (je Agent-Typ)
  → POSIX-Rechte setzen (setup-agent-isolation.sh erweitern)
  → Verifikation: Admin prüft manuell — kann Forge-User in pjc3/ schreiben? → Nein ✓
    (Ergebnis wird in Stufe 2 vom Memory Agent archiviert, nicht hier)

Stufe 2 — Memory Agent
  → Ordnerstruktur: langzeitgedaechnis/ mit Local / Vault-Platzhalter
  → Checkliste für SessionEnd-Hook definieren
  → Verifikation: Memory Agent schreibt korrekt vor /clear ✓

Stufe 3 — Hooks
  → PreToolUse: Filesystem Boundary
  → PostToolUse: Argus-Trigger nach Forge-Abschluss
  → SessionEnd: Memory-Sammel-Loop mit Checkliste
  → Verifikation: Hook blockiert Schreiben außerhalb ROOT ✓

Stufe 4 — Aegis Core
  → Manifest-Header + Task Envelope Template
  → Routing-Logik dokumentieren
  → Verifikation: 3 Test-Szenarien durchspielen ✓

Stufe 5 — Forge/pjc3-docker (erster Builder)
  → Manifest-Header + ROOT-Definition
  → Läuft innerhalb des fertigen Fundaments
  → Verifikation: Forge schreibt nur in ROOT ✓

Stufe 6 — Argus Sentinel
  → Erst wenn Forge operativ (braucht etwas zum prüfen)
  → Verifikation: Finding landet in langzeitgedaechnis/findings/ ✓

Stufe 7 — Nexus Projekt
  → Security-Layer je Satellit
  → Verifikation: Finding sofort in Memory Agent ✓

Stufe 8 — Nexus Global
  → Zuletzt — wenn alles andere stabil läuft
  → Verifikation: systemweite Checks ohne Fehlalarme ✓
```

---

## Offene Punkte (später klären)

```
[ ] Task Envelope — genaues Dateiformat (YAML? Markdown-Header?)
[ ] SessionEnd-Trigger (Memory Agent Checkliste) — Favorit: vor /clear; exakter Hook-Mechanismus offen
[ ] PostToolUse-Trigger (Argus-Start nach Forge) — Hook → Aegis Core → Argus Dispatch; exakte Hook-Konfiguration offen
[ ] Vault — Technologie noch nicht festgelegt (Vaultwarden-Integration?)
[ ] Sub-Agenten unter Aegis Core — wann, wie viele?
[ ] NOVA_ROADMAP.md — Klarstellungs-Vermerk: Datei ist universelle Vision/Blaupause,
    Begriffe wie "Aegis Core" sind generisch (kein Eigenname), Namen pro Projekt frei wählbar.
    Einmalig am Session-Ende eintragen.
```

---

## Nicht in Scope

- pjc3-viz1 — TABU bis explizit freigegeben
- Nexus Global — Implementierung erst in Stufe 8
- Vault-Integration — Platzhalter, eigene Design-Spec wenn bereit
- Breaking Changes an bestehender Funktionalität
