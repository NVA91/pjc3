# Migration Agenten-Architektur — Implementierungsplan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Ziel:** 6 isolierte Agenten (Aegis Core, Memory Agent, Forge, Argus Sentinel, Nexus Global, Nexus Projekt) mit Defense-in-Depth (5 Schichten) für die pjc3-Pyramidenarchitektur aufbauen.

**Architektur:** System-Fundament zuerst (AppArmor + POSIX-Rechte als Kern-Isolation), dann Ordnerstruktur und Agenten-Definitionen, zuletzt Hooks. Jede Stufe ist eigenständig verifizierbar bevor die nächste beginnt.

**Tech Stack:** Bash, AppArmor (aa-genprof/apparmor_parser), Claude Code Agent Markdown, Claude Code Hooks (PreToolUse/PostToolUse/SessionEnd)

**Spec:** `docs/superpowers/specs/2026-03-16-migration-agenten-design.md`

---

## Chunk 1: System-Fundament (Stufen 1–2)

> Ziel: POSIX-User + AppArmor-Profile als physische Isolation — unabhängig von Software-Schichten.
> Ausführung: muss als `root` auf dem Host erfolgen.
> Kein Überspringen: Chunk 2 setzt voraus, dass Chunk 1 verifiziert ist.

### Task 1: Agent-User erweitern (POSIX-Rechte)

**Dateien:**
- Modify: `setup-agent-isolation.sh`

> Bestehende User: CLAUDE (1001), GRAVITY (1002), NEXUS (1003).
> Neue User: forge-pjc3-docker (1004), argus (1005), memory-agent (1006).
> Regel: zwei Agenten dürfen niemals die gleiche UID teilen.

- [ ] **Schritt 1: Bestehendes Skript lesen**

  ```bash
  cat /home/ubhp-nova/claude-c/pjc3/setup-agent-isolation.sh
  ```

  Verstehen: welche User existieren, wie wird `create_agent_user` aufgerufen.

- [ ] **Schritt 2: Neue Agent-User eintragen**

  In `setup-agent-isolation.sh` die UID-Kommentar-Tabelle und die Aufrufe erweitern:

  ```bash
  # UID-Mapping (fest — niemals ändern):
  #   CLAUDE:           1001:1001  (bestehend)
  #   GRAVITY:          1002:1002  (bestehend)
  #   NEXUS:            1003:1003  (bestehend)
  #   FORGE-PJC3DOCKER: 1004:1004  (Forge Builder für pjc3-docker)
  #   ARGUS:            1005:1005  (Argus Sentinel Reviewer)
  #   MEMORY-AGENT:     1006:1006  (Memory Agent Knowledge Base)
  ```

  Neue Aufrufe am Ende der Datei (vor dem abschließenden echo):
  ```bash
  create_agent_user "forge-pjc3-docker" 1004 1004
  create_agent_user "argus"            1005 1005
  create_agent_user "memory-agent"     1006 1006
  ```

- [ ] **Schritt 3: Skript ausführen (als root)**

  ```bash
  sudo bash /home/ubhp-nova/claude-c/pjc3/setup-agent-isolation.sh
  ```

  Erwartete Ausgabe: 6x "✅ /srv/agents/<name> (uid:gid, chmod 700)"

- [ ] **Schritt 4: Verifikation**

  ```bash
  ls -lan /srv/agents/
  ```

  Erwartetes Ergebnis: 6 Verzeichnisse mit je dem richtigen Eigentümer (uid 1001–1006), chmod 700.

  > **Hinweis zum Username-Suffix:** Das Skript hängt `-agent` an jeden Basis-Namen an.
  > `create_agent_user "memory-agent" 1006 1006` → User heißt `memory-agent-agent`.
  > Vor diesem Check: `grep "create_agent_user" setup-agent-isolation.sh` ausführen
  > und die tatsächlichen Namen bestätigen.

  ```bash
  id forge-pjc3-docker-agent && id argus-agent && id memory-agent-agent
  ```

  Erwartetes Ergebnis: alle 3 User existieren, keine Login-Shell (`/bin/false`).

- [ ] **Schritt 5: Commit**

  ```bash
  git add setup-agent-isolation.sh
  git commit -m "feat: extend agent isolation — forge, argus, memory-agent UIDs (1004-1006)"
  ```

---

### Task 2: AppArmor-Profile erstellen

**Dateien:**
- Create: `apparmor/forge-pjc3-docker`
- Create: `apparmor/argus-sentinel`
- Create: `apparmor/memory-agent`
- Create: `apparmor/aegis-core`
- Create: `apparmor/nexus-projekt`
- Create: `apparmor/nexus-global`
- Create: `apparmor/README-apparmor.md`

> **Wichtig:** AppArmor-Profile sind System-Dateien. Sie liegen auf dem Host in `/etc/apparmor.d/`.
> Die Quell-Dateien werden im Repo versioniert unter `apparmor/` und dann nach `/etc/apparmor.d/` kopiert.
> Syntax: nur konzeptuell in der Spec — hier werden echte Profile mit korrekter AppArmor-Syntax geschrieben.

- [ ] **Schritt 1: AppArmor-Verzeichnis im Repo anlegen**

  ```bash
  mkdir -p /home/ubhp-nova/claude-c/pjc3/apparmor
  ```

- [ ] **Schritt 2: Forge-Profil schreiben**

  Datei: `apparmor/forge-pjc3-docker`

  ```
  #include <tunables/global>

  profile forge-pjc3-docker /usr/bin/claude flags=(attach_disconnected) {
    #include <abstractions/base>

    # Forge ROOT: voll lesen + schreiben
    /home/ubhp-nova/claude-c/pjc3-docker/  r,
    /home/ubhp-nova/claude-c/pjc3-docker/** rwlk,

    # pjc3/ Kontext: nur lesen (für Regeln, core.md)
    /home/ubhp-nova/claude-c/pjc3/  r,
    /home/ubhp-nova/claude-c/pjc3/** r,

    # Kein Zugriff auf ~/.claude/ oder andere Repos
    deny /home/ubhp-nova/.claude/** rwklx,
    deny /home/ubhp-nova/claude-c/pjc3-viz1/** rwklx,
  }
  ```

- [ ] **Schritt 3: Argus-Profil schreiben**

  Datei: `apparmor/argus-sentinel`

  ```
  #include <tunables/global>

  profile argus-sentinel /usr/bin/claude flags=(attach_disconnected) {
    #include <abstractions/base>

    # Argus darf alles lesen (für Reviews)
    /home/ubhp-nova/claude-c/  r,
    /home/ubhp-nova/claude-c/** r,

    # Schreiben nur in findings/
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/  rw,
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/** rw,

    # Kein Schreiben in ~/.claude/ oder Code
    deny /home/ubhp-nova/.claude/** w,
    deny /home/ubhp-nova/claude-c/pjc3-docker/** w,
  }
  ```

- [ ] **Schritt 4: Memory-Agent-Profil schreiben**

  Datei: `apparmor/memory-agent`

  ```
  #include <tunables/global>

  profile memory-agent /usr/bin/claude flags=(attach_disconnected) {
    #include <abstractions/base>

    # Lesen: alle Repos (für Kontext-Abfragen)
    /home/ubhp-nova/claude-c/  r,
    /home/ubhp-nova/claude-c/** r,

    # Schreiben: nur local/ und tasks/ im langzeitgedaechnis/
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/local/  rw,
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/local/** rw,
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/  rw,
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/** rw,

    # Kein Schreiben in findings/ (Argus/Nexus-Domäne)
    deny /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/** w,
  }
  ```

- [ ] **Schritt 5: Aegis-Core-Profil schreiben**

  Datei: `apparmor/aegis-core`

  ```
  #include <tunables/global>

  profile aegis-core /usr/bin/claude flags=(attach_disconnected) {
    #include <abstractions/base>

    # Lesen: alle Repos
    /home/ubhp-nova/claude-c/  r,
    /home/ubhp-nova/claude-c/** r,

    # Schreiben: nur tasks/
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/  rw,
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/** rw,

    # Kein direktes Schreiben in Projektcode
    deny /home/ubhp-nova/claude-c/pjc3-docker/** w,
    deny /home/ubhp-nova/claude-c/pjc3-viz1/** rwklx,
  }
  ```

- [ ] **Schritt 6: Nexus-Projekt-Profil schreiben**

  Datei: `apparmor/nexus-projekt`

  ```
  #include <tunables/global>

  profile nexus-projekt /usr/bin/claude flags=(attach_disconnected) {
    #include <abstractions/base>

    # Lesen: nur ROOT (vollständige Isolation)
    /home/ubhp-nova/claude-c/pjc3-docker/  r,
    /home/ubhp-nova/claude-c/pjc3-docker/** r,

    # Schreiben: nur findings/
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/  rw,
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/** rw,

    # Kein Zugriff außerhalb ROOT (außer findings/ Schreiben)
    deny /home/ubhp-nova/claude-c/pjc3/** w,
    deny /home/ubhp-nova/.claude/** rwklx,
  }
  ```

- [ ] **Schritt 7: Nexus-Global-Profil schreiben**

  Datei: `apparmor/nexus-global`

  ```
  #include <tunables/global>

  profile nexus-global /usr/bin/claude flags=(attach_disconnected) {
    #include <abstractions/base>

    # Lesen: ~/.claude/ + alle Repos (Security-Checks erfordern globalen Einblick)
    /home/ubhp-nova/.claude/  r,
    /home/ubhp-nova/.claude/** r,
    /home/ubhp-nova/claude-c/  r,
    /home/ubhp-nova/claude-c/** r,

    # Schreiben: nur findings/
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/  rw,
    /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/** rw,

    # Kein Code-Schreiben
    deny /home/ubhp-nova/.claude/** w,
    deny /home/ubhp-nova/claude-c/pjc3-docker/** w,
  }
  ```

- [ ] **Schritt 8: README für AppArmor-Verzeichnis schreiben**

  Datei: `apparmor/README-apparmor.md`

  ```markdown
  # AppArmor-Profile — pjc3 Agenten-Isolation

  Diese Profile sind Schicht 3 der Defense-in-Depth-Architektur.
  Sie sitzen im Linux-Kernel — kein Prozess kommt daran vorbei.

  ## Deployment

  Profile nach /etc/apparmor.d/ kopieren und laden:
  (Achtung: nur Profil-Dateien kopieren, NICHT die README-Datei)

  ```bash
  sudo cp apparmor/forge-pjc3-docker apparmor/argus-sentinel apparmor/memory-agent \
    apparmor/aegis-core apparmor/nexus-projekt apparmor/nexus-global /etc/apparmor.d/
  sudo apparmor_parser -r /etc/apparmor.d/forge-pjc3-docker
  sudo apparmor_parser -r /etc/apparmor.d/argus-sentinel
  sudo apparmor_parser -r /etc/apparmor.d/memory-agent
  sudo apparmor_parser -r /etc/apparmor.d/aegis-core
  sudo apparmor_parser -r /etc/apparmor.d/nexus-projekt
  sudo apparmor_parser -r /etc/apparmor.d/nexus-global
  ```

  ## Status prüfen

  ```bash
  sudo aa-status | grep -E "forge|argus|memory|aegis|nexus"
  ```

  ## Wichtig
  - Profile sind konzeptuell angepasst — bei echtem Deployment Pfade verifizieren
  - Nach Änderungen: apparmor_parser -r <profil> (kein Neustart nötig)
  - enforce vs. complain: Produktion = enforce; Testen = complain (aa-complain <profil>)
  ```

- [ ] **Schritt 9: Profile nach /etc/apparmor.d/ deployen (als root)**

  Nur Profil-Dateien kopieren — README wird nicht deployed:

  ```bash
  sudo cp /home/ubhp-nova/claude-c/pjc3/apparmor/forge-pjc3-docker /etc/apparmor.d/
  sudo cp /home/ubhp-nova/claude-c/pjc3/apparmor/argus-sentinel /etc/apparmor.d/
  sudo cp /home/ubhp-nova/claude-c/pjc3/apparmor/memory-agent /etc/apparmor.d/
  sudo cp /home/ubhp-nova/claude-c/pjc3/apparmor/aegis-core /etc/apparmor.d/
  sudo cp /home/ubhp-nova/claude-c/pjc3/apparmor/nexus-projekt /etc/apparmor.d/
  sudo cp /home/ubhp-nova/claude-c/pjc3/apparmor/nexus-global /etc/apparmor.d/
  sudo apparmor_parser -r /etc/apparmor.d/forge-pjc3-docker
  sudo apparmor_parser -r /etc/apparmor.d/argus-sentinel
  sudo apparmor_parser -r /etc/apparmor.d/memory-agent
  sudo apparmor_parser -r /etc/apparmor.d/aegis-core
  sudo apparmor_parser -r /etc/apparmor.d/nexus-projekt
  sudo apparmor_parser -r /etc/apparmor.d/nexus-global
  ```

  Erwartete Ausgabe: kein Fehler. Syntax-Fehler werden direkt gemeldet.

- [ ] **Schritt 10: Verifikation**

  ```bash
  sudo aa-status | grep -E "forge-pjc3-docker|argus-sentinel|memory-agent|aegis-core|nexus"
  ```

  Erwartetes Ergebnis: alle 6 Profile in "enforce mode" gelistet.

- [ ] **Schritt 11: Manueller Test — kann Forge in pjc3/ schreiben?**

  ```bash
  # Als forge-pjc3-docker-agent-User testen:
  sudo -u forge-pjc3-docker-agent touch /home/ubhp-nova/claude-c/pjc3/test-isolation.txt
  ```

  Erwartetes Ergebnis: `Permission denied` — POSIX + AppArmor blocken.

  ```bash
  # Aber Forge kann in pjc3-docker/ schreiben:
  sudo -u forge-pjc3-docker-agent touch /home/ubhp-nova/claude-c/pjc3-docker/test-forge.txt
  ls -la /home/ubhp-nova/claude-c/pjc3-docker/test-forge.txt
  # Aufräumen:
  sudo rm /home/ubhp-nova/claude-c/pjc3-docker/test-forge.txt
  ```

- [ ] **Schritt 12: Commit**

  ```bash
  git add apparmor/
  git commit -m "feat: AppArmor profile suite — 6 agents, enforce mode, layer 3 isolation"
  ```

---

### Task 3: Langzeitgedächtnis-Ordnerstruktur (Memory Agent Basis)

**Dateien:**
- Create: `langzeitgedaechnis/local/.gitkeep`
- Create: `langzeitgedaechnis/tasks/active/.gitkeep`
- Create: `langzeitgedaechnis/tasks/archive/.gitkeep`
- Create: `langzeitgedaechnis/findings/.gitkeep`
- Create: `langzeitgedaechnis/vault/.gitkeep` (Platzhalter)
- Create: `langzeitgedaechnis/README.md`
- Create: `.claude/hooks/session-end-checklist.md` (Spec Stufe 2: Checkliste definieren)

> Schreibbereiche laut Spec:
> - `local/` + `tasks/` → Memory Agent
> - `findings/` → Argus Sentinel + Nexus
> - `vault/` → Platzhalter, Technologie noch offen

- [ ] **Schritt 1: Ordnerstruktur anlegen**

  ```bash
  mkdir -p /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/local
  mkdir -p /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/active
  mkdir -p /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/archive
  mkdir -p /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings
  mkdir -p /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/vault
  touch /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/local/.gitkeep
  touch /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/active/.gitkeep
  touch /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks/archive/.gitkeep
  touch /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings/.gitkeep
  touch /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/vault/.gitkeep
  ```

- [ ] **Schritt 2: README anlegen**

  Datei: `langzeitgedaechnis/README.md`

  ```markdown
  # Langzeitgedächtnis — pjc3

  Strukturiertes Wissensarchiv für die Pyramidenarchitektur.
  Kein simpler Log-Ordner — jeder Bereich hat einen dedizierten Schreiber.

  ## Bereiche

  | Ordner | Schreiber | Inhalt |
  |--------|-----------|--------|
  | `local/` | Memory Agent | Projektgedächtnis, History, Entscheidungen |
  | `tasks/active/` | Memory Agent + Aegis Core | Aktive Task Envelopes |
  | `tasks/archive/` | Memory Agent | Abgeschlossene Tasks |
  | `findings/` | Argus Sentinel, Nexus Global, Nexus Projekt | Review- und Security-Findings |
  | `vault/` | Vault (Platzhalter) | Geheimnisse — Technologie noch offen |

  ## Regeln

  - Memory Agent schreibt NICHT in `findings/`
  - Argus/Nexus schreiben NICHT in `local/` oder `tasks/`
  - Findings werden SOFORT eingetragen — nicht auf /clear warten
  - Vault-Inhalte: read-only für alle außer Vault-Integration
  ```

- [ ] **Schritt 3: SessionEnd-Checklisten-Datei anlegen (Spec Stufe 2)**

  Datei: `.claude/hooks/session-end-checklist.md`

  ```markdown
  # SessionEnd-Checkliste — Memory Agent

  Diese Datei wird vom SessionEnd-Hook referenziert.
  Memory Agent MUSS alle Punkte bestätigen bevor /clear ausgeführt wird.

  ## Pflichtschritte

  - [ ] Offene Tasks archivieren: `langzeitgedaechnis/tasks/active/` → `tasks/archive/`
  - [ ] Entscheidungen verdichten und in `langzeitgedaechnis/local/` eintragen
  - [ ] Bekannte Fehler dokumentieren: `local/fehler-archiv.md`
  - [ ] Veraltete Archive aufräumen (alte Tasks löschen wenn obsolet)
  - [ ] Bestätigung ausgeben: "Memory Agent: SessionEnd ✅ — /clear darf starten"

  ## Format für Bestätigung

  Memory Agent gibt als letzte Zeile aus:
  `MEMORY-AGENT-SESSIONEND: OK`
  ```

- [ ] **Schritt 4: Verifikation**

  ```bash
  find /home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis -type f | sort
  find /home/ubhp-nova/claude-c/pjc3/.claude/hooks -type f 2>/dev/null | sort
  ```

  Erwartetes Ergebnis: 5 `.gitkeep` + 1 `README.md` + 1 `session-end-checklist.md`

- [ ] **Schritt 5: Commit**

  ```bash
  git add langzeitgedaechnis/ .claude/hooks/session-end-checklist.md
  git commit -m "feat: langzeitgedaechnis structure + SessionEnd checklist (stage 2 complete)"
  ```

---

## Chunk 2: Agenten + Hooks (Stufen 3–8)

> Voraussetzung: Chunk 1 vollständig verifiziert (POSIX-User + AppArmor aktiv + Ordner vorhanden).
> Ziel: Alle 6 Agenten als Claude Code Agent-Definitionen + 3 Hooks.

### Task 4: Aegis Core Agent-Definition

**Dateien:**
- Create: `pjc3/.claude/agents/aegis-core.md`

- [ ] **Schritt 1: Agent-Datei schreiben**

  Datei: `.claude/agents/aegis-core.md`

  ```markdown
  ---
  name: Aegis Core
  description: Orchestrator — nimmt Aufträge an, delegiert an Satellit-Agenten. Erster Ansprechpartner für repo-übergreifende Aufgaben. Dispatcht Subagenten via Task Envelope.
  ---

  # Aegis Core — Orchestrator / Control Plane

  ```
  AGENT: Aegis Core
  ROLLE: Orchestrator
  DARF: lesen (alle Repos), Tasks in langzeitgedaechnis/tasks/ anlegen, Subagenten dispatchen
  DARF NICHT: Projektcode schreiben, globale Settings ändern, Bash direkt ausführen
  BEI UNKLARHEIT: Memory Agent befragen
  HILFE: [Memory Agent] [Argus Sentinel nach Forge-Abschluss]
  ```

  ## Aufgabe

  Nimmt Aufträge an, zerlegt in Arbeitspakete, weist Agenten zu.
  Holt Kontext vom Memory Agent — sucht nicht selbst.
  Generiert Task Envelopes pro Auftrag.
  Erzwingt Regeln und Übergaben.

  ## Task Envelope — Template

  Für jeden Auftrag eine Datei anlegen unter:
  `langzeitgedaechnis/tasks/active/task-YYYY-MM-DD-NNN.md`

  ```
  TASK-ENVELOPE
    ID:        task-YYYY-MM-DD-NNN
    Agent:     [Forge/pjc3-docker | Argus Sentinel | Nexus Projekt | ...]
    Aufgabe:   <exakte Beschreibung>
    Scope:     /home/ubhp-nova/claude-c/<satellit-repo>/
    Regeln:    [link zu REGEL.md des Repos]
    Tools:     [Nexus-Projekt für Security-Check | Argus für Review]
    Übergabe:  [Argus Sentinel prüft Ergebnis | none]
    Offen:     nein / ja → Aegis Core fragen
  ```

  Nach Abschluss: Envelope nach `langzeitgedaechnis/tasks/archive/` verschieben.

  ## Routing-Logik

  | Aufgabe | Delegiert an |
  |---------|-------------|
  | Code in pjc3-docker/ | Forge/pjc3-docker |
  | Review nach Forge-Abschluss | Argus Sentinel |
  | Security-Check (Projekt) | Nexus Projekt |
  | Security-Check (global) | Nexus Global |
  | Kontext / History | Memory Agent |

  ## Abbruch-Befehl

  Bei Unklarheit → **STOPP** → User melden. Kein Raten.

  ## Hinweis: Agenten-Start

  Aegis Core startet Agenten NICHT via Bash.
  Dispatch = Task Envelope übergeben → Subagent startet mit Envelope als Kontext.
  Kein Prozess-Management nötig.
  ```

- [ ] **Schritt 2: Verifikation**

  ```bash
  head -5 /home/ubhp-nova/claude-c/pjc3/.claude/agents/aegis-core.md
  ```

  Erwartetes Ergebnis: YAML-Frontmatter mit `name: Aegis Core` sichtbar.

- [ ] **Schritt 3: Commit**

  ```bash
  git add .claude/agents/aegis-core.md
  git commit -m "feat: Aegis Core agent definition — orchestrator with task envelope template"
  ```

---

### Task 5: Memory Agent Definition

**Dateien:**
- Create: `pjc3/.claude/agents/memory-agent.md`

- [ ] **Schritt 1: Agent-Datei schreiben**

  Datei: `.claude/agents/memory-agent.md`

  ```markdown
  ---
  name: Memory Agent
  description: Knowledge Base — erster Ansprechpartner für Aegis Core bei Abfragen. Verwaltet Langzeitgedächtnis, Projekthistorie, Entscheidungen, Fehler-Archiv. Schreibt in local/ und tasks/, NICHT in findings/.
  ---

  # Memory Agent — Knowledge Base

  ```
  AGENT: Memory Agent
  ROLLE: Knowledge Base
  DARF: lesen (alle Repos), schreiben in langzeitgedaechnis/local/ + tasks/
  DARF NICHT: Source Code ändern, außerhalb langzeitgedaechnis/ schreiben, in findings/ schreiben
  BEI UNKLARHEIT: STOPP → Aegis Core fragen
  MCP: context7 (externe Bibliotheks-Doku, read), Vault (kommt später, read-only)
  ```

  ## Aufgabe

  - Erster Ansprechpartner für Aegis Core (Abfragen, Kontext)
  - Verwaltet Langzeitgedächtnis, Projekthistorie, Entscheidungen
  - Archiviert bekannte Fehler, Architekturwissen, Task-History
  - Verdichtet und strukturiert — kein simpler Log-Ordner

  ## 3 Wissensbereiche

  | Bereich | Quelle | Zugriff |
  |---------|--------|---------|
  | `context7` | externe Bibliotheks-Doku | MCP-Tool (read) |
  | `Vault` | Geheimnisse | read-only, isoliert (Platzhalter) |
  | `Local` | Projektgedächtnis, History, Tasks | read/write |

  ## Schreibbereiche

  | Ordner | Erlaubt | Verboten |
  |--------|---------|---------|
  | `langzeitgedaechnis/local/` | ✅ schreiben | — |
  | `langzeitgedaechnis/tasks/` | ✅ schreiben | — |
  | `langzeitgedaechnis/findings/` | ❌ | Argus/Nexus-Domäne |
  | Außerhalb langzeitgedaechnis/ | ❌ | nie |

  ## SessionEnd-Checkliste

  Vor jedem /clear — dieser Check MUSS abgeschlossen sein:

  ```
  [ ] Offene Tasks archivieren (tasks/active/ → tasks/archive/)
  [ ] Entscheidungen verdichten und in local/ eintragen
  [ ] Bekannte Fehler dokumentieren (local/fehler-archiv.md)
  [ ] Aufgaben-Archiv aufräumen (alte löschen wenn obsolet)
  [ ] Bestätigung ausgeben: "Memory Agent: SessionEnd ✅ — /clear darf starten"
  ```
  ```

- [ ] **Schritt 2: Verifikation**

  ```bash
  grep -n "DARF NICHT" /home/ubhp-nova/claude-c/pjc3/.claude/agents/memory-agent.md
  ```

  Erwartetes Ergebnis: Zeile mit "findings/" als verbotener Schreibbereich.

- [ ] **Schritt 3: Commit**

  ```bash
  git add .claude/agents/memory-agent.md
  git commit -m "feat: Memory Agent definition — knowledge base with SessionEnd checklist"
  ```

---

### Task 6: Forge Builder Definition (pjc3-docker)

**Dateien:**
- Create: `pjc3-docker/.claude/agents/forge.md`

> Forge ist je Satellit eine eigene Datei. Dieser Task erstellt die erste Instanz für pjc3-docker.
> Für weitere Satelliten: gleiche Struktur, ROOT anpassen.

- [ ] **Schritt 1: .claude/agents/ Verzeichnis in pjc3-docker sicherstellen**

  ```bash
  ls /home/ubhp-nova/claude-c/pjc3-docker/.claude/agents/ 2>/dev/null || \
  mkdir -p /home/ubhp-nova/claude-c/pjc3-docker/.claude/agents/
  ```

- [ ] **Schritt 2: Forge-Agent schreiben**

  Datei: `/home/ubhp-nova/claude-c/pjc3-docker/.claude/agents/forge.md`

  ```markdown
  ---
  name: Forge
  description: Builder für pjc3-docker — implementiert Features, erstellt Dateien, passt Projektcode an. Arbeitet ausschließlich innerhalb ROOT. Bei Unklarheit: STOPP, kein Raten.
  ---

  # Forge — Builder / Project Worker

  ```
  AGENT: Forge/pjc3-docker
  ROLLE: Builder
  ROOT: /home/ubhp-nova/claude-c/pjc3-docker/
  DARF: lesen + schreiben innerhalb ROOT, Bash innerhalb ROOT
  DARF NICHT: außerhalb ROOT, Memory Agent direkt schreiben,
              globale Regeln oder Settings ändern
  BEI UNKLARHEIT: STOPP → Ticket an Aegis Core, nicht raten
  HILFE: [Aegis Core] [Nexus Projekt für Security-Check] [Argus nach Abschluss]
  ```

  ## Aufgabe

  Implementiert Features, erstellt Dateien, passt Projektcode innerhalb ROOT an.
  Arbeitet frei — aber ausschließlich innerhalb ROOT.

  ## Boundary-Regeln (absolut)

  1. Kein Lesen oder Schreiben außerhalb ROOT (außer core.md lesen für Kontext)
  2. Kein direktes Schreiben in `langzeitgedaechnis/` — Memory Agent ist zuständig
  3. Keine globalen Settings, Hooks oder Regeln ändern
  4. Bei Unklarheit: **STOPP** → Ticket an Aegis Core, nicht improvisieren

  ## Abschluss-Signal

  Nach Abschluss eines Tasks: explizit melden:
  "Forge/pjc3-docker: Task [ID] abgeschlossen — bereit für Argus-Review"

  Aegis Core triggert dann den Argus Sentinel Review.
  ```

- [ ] **Schritt 3: Commit (im pjc3-docker Repo)**

  ```bash
  cd /home/ubhp-nova/claude-c/pjc3-docker
  git add .claude/agents/forge.md
  git commit -m "feat: Forge agent definition — builder for pjc3-docker, strict ROOT boundary"
  cd /home/ubhp-nova/claude-c/pjc3
  ```

---

### Task 7: Argus Sentinel Definition

**Dateien:**
- Create: `pjc3/.claude/agents/argus-sentinel.md`

- [ ] **Schritt 1: Agent-Datei schreiben**

  Datei: `.claude/agents/argus-sentinel.md`

  ```markdown
  ---
  name: Argus Sentinel
  description: Independent Reviewer — prüft nach jedem Forge-Abschluss. Architektur, Stil, Übergabe, Diff-Analyse. Schreibt Findings direkt in langzeitgedaechnis/findings/. Kein Schreibrecht auf Produktionscode.
  ---

  # Argus Sentinel — Independent Reviewer

  ```
  AGENT: Argus Sentinel
  ROLLE: Reviewer (kein Schreibrecht auf Code)
  DARF: lesen (alle Repos), Findings in langzeitgedaechnis/findings/ schreiben
  DARF NICHT: Produktionscode ändern, Tasks anlegen, Agenten steuern,
              in langzeitgedaechnis/local/ oder tasks/ schreiben
  TRIGGER: Aegis Core dispatcht nach Forge-Abschluss
  ```

  ## Aufgabe

  Review nach jedem Forge-Abschluss:
  - Architekturprüfung (hält sich der Code an die Spec?)
  - Stilprüfung (CLAUDE.md Konventionen)
  - Übergabeprüfung (Task Envelope Kriterien erfüllt?)
  - Diff-Analyse (was hat sich geändert, warum?)

  ## Finding-Format

  Findings sofort in `langzeitgedaechnis/findings/` schreiben:
  Dateiname: `finding-YYYY-MM-DD-NNN-<kurzbeschreibung>.md`

  ```
  # Finding: [Kurzbeschreibung]

  **Datum:** YYYY-MM-DD
  **Agent:** Argus Sentinel
  **Task-ID:** task-YYYY-MM-DD-NNN
  **Severity:** [info | warning | critical]

  ## Befund
  [Was wurde gefunden]

  ## Empfehlung
  [Was sollte getan werden]

  ## Status
  [offen | an Aegis Core eskaliert | erledigt]
  ```

  ## Trigger-Mechanismus

  Argus wird NICHT direkt gerufen. Ablauf:
  1. Forge meldet Abschluss
  2. PostToolUse-Hook benachrichtigt Aegis Core
  3. Aegis Core dispatcht Argus als Subagent mit Task-ID

  Argus startet mit Task Envelope als Kontext — liest nur was er braucht.
  ```

- [ ] **Schritt 2: Verifikation**

  ```bash
  grep -c "DARF NICHT" /home/ubhp-nova/claude-c/pjc3/.claude/agents/argus-sentinel.md
  ```

  Erwartetes Ergebnis: mindestens 1 (Verbote sind explizit).

- [ ] **Schritt 3: Commit**

  ```bash
  git add .claude/agents/argus-sentinel.md
  git commit -m "feat: Argus Sentinel definition — reviewer with findings/ write access only"
  ```

---

### Task 8: Nexus Projekt Definition (pjc3-docker)

**Dateien:**
- Create: `pjc3-docker/.claude/agents/nexus-projekt.md`

- [ ] **Schritt 1: Agent-Datei schreiben**

  Datei: `/home/ubhp-nova/claude-c/pjc3-docker/.claude/agents/nexus-projekt.md`

  ```markdown
  ---
  name: Nexus Projekt
  description: Security Agent für pjc3-docker — projektspezifische Sicherheitsprüfungen innerhalb ROOT. Vollständige Isolation. Findings sofort in langzeitgedaechnis/findings/ — nicht warten auf /clear.
  ---

  # Nexus Projekt — Project Security Agent

  ```
  AGENT: Nexus Projekt/pjc3-docker
  ROLLE: Security (projektspezifisch)
  ROOT: /home/ubhp-nova/claude-c/pjc3-docker/
  DARF: lesen innerhalb ROOT, Findings in langzeitgedaechnis/findings/ schreiben
        Bash read-only: ls, cat, find, grep (nur innerhalb ROOT)
  DARF NICHT: außerhalb ROOT lesen oder schreiben, Code ändern
  TRIGGER: parallel zu Forge oder auf Anfrage von Aegis Core
  ```

  ## Aufgabe

  Projektspezifische Sicherheitsprüfungen:
  - Secrets in Code (hartcodierte Keys, Passwörter)
  - Docker-Security-Regeln (CLAUDE.md: kein root, cap_drop ALL, etc.)
  - Datei-Permissions innerhalb ROOT
  - Dependency-Vulnerabilities (requirements.txt, package.json)

  ## Finding-Format

  Findings SOFORT in `langzeitgedaechnis/findings/` (nicht warten auf /clear):
  Dateiname: `finding-YYYY-MM-DD-NNN-security-<beschreibung>.md`
  Format: identisch zu Argus (Datum, Agent, Severity, Befund, Empfehlung, Status)

  ## Isolation — absolut

  Nexus Projekt darf NICHT außerhalb ROOT lesen oder schreiben.
  Ausnahme: `langzeitgedaechnis/findings/` (Schreiben von Findings — bewusste Ausnahme).
  ```

- [ ] **Schritt 2: Commit (im pjc3-docker Repo)**

  ```bash
  cd /home/ubhp-nova/claude-c/pjc3-docker
  git add .claude/agents/nexus-projekt.md
  git commit -m "feat: Nexus Projekt security agent — pjc3-docker scope, findings/ output"
  cd /home/ubhp-nova/claude-c/pjc3
  ```

---

### Task 9: Nexus Global Definition

**Dateien:**
- Create: `pjc3/.claude/agents/nexus-global.md`

> Laut Spec: Nexus Global erst in Stufe 8 — nach allem anderen. Datei jetzt anlegen, aber erst aktivieren wenn alle anderen Agenten stabil laufen.

- [ ] **Schritt 1: Agent-Datei schreiben**

  Datei: `.claude/agents/nexus-global.md`

  ```markdown
  ---
  name: Nexus Global
  description: Global Security Agent — systemweite Sicherheitsprüfungen (~/.claude/, pjc3/, globale Hooks). Liest alle Repos (read-only). Schreibt nur in findings/. ERST AKTIVIEREN wenn alle anderen Agenten stabil laufen (Stufe 8).
  ---

  # Nexus Global — Global Security Agent

  ```
  AGENT: Nexus Global
  ROLLE: Security (global)
  LESE-SCOPE: ~/.claude/ + pjc3/ vollständig + Satellit-Repos read-only
  DARF: lesen (global + Satelliten), Findings in langzeitgedaechnis/findings/ schreiben
        Bash read-only: ls, cat, find, grep
  DARF NICHT: Code ändern, in Satellit-Repos schreiben, Settings ändern
  TRIGGER: bei Änderungen an globalem Bereich (~/.claude/, pjc3/ Hooks/Settings)
  STATUS: INAKTIV bis Stufe 8 explizit freigegeben
  ```

  ## Aufgabe

  Systemweite Sicherheitsprüfungen:
  - `~/.claude/` Settings und Hooks auf Anomalien
  - Globale AppArmor-Profile (vollständig und aktiv?)
  - Satellit-Repo-Grenzen (kein Cross-Repo-Schreiben?)
  - Bekannte Fehlkonfigurationen in pjc3/ global

  ## Aktivierungs-Bedingung

  Nexus Global startet erst wenn:
  - [ ] Alle Stufen 1–7 vollständig verifiziert
  - [ ] Kein anderer Agent aktiv mit unverifizierten Schreibzugriffen
  - [ ] Admin-Bestätigung: "Nexus Global freigeben"

  ## Finding-Format

  Identisch zu Nexus Projekt / Argus Sentinel.
  ```

- [ ] **Schritt 2: Commit**

  ```bash
  git add .claude/agents/nexus-global.md
  git commit -m "feat: Nexus Global definition — system-wide security, inactive until stage 8"
  ```

---

### Task 10: PreToolUse Hook — Filesystem Boundary

**Dateien:**
- Create: `pjc3/.claude/hooks/pre-tool-use-boundary.sh`
- Modify: `pjc3/.claude/settings.json` (Hook registrieren)

> Schicht 1 der Defense-in-Depth: Software-Layer.
> Prüft Schreibzugriff vor Ausführung gegen ROOT des aktiven Agents.
> Schwäche: kann bei Fehlkonfiguration fehlen — deshalb POSIX + AppArmor als Backup.

> **Design-Prerequisite — Agent-Identität im Hook:**
> Claude Code Hooks kennen KEINE Variable `CLAUDE_AGENT_NAME`. Die dokumentierten Variablen
> sind: `CLAUDE_TOOL_NAME`, `CLAUDE_TOOL_INPUT`, `CLAUDE_SESSION_ID`.
> Der Hook kann nicht direkt wissen, welcher Agent aktiv ist.
>
> **Gewählte Lösung (Session-Scope-Datei):**
> Jeder Agent schreibt beim Start seinen Namen in `/tmp/claude-active-agent-<SESSION_ID>`.
> Der Hook liest diese Datei. Wenn die Datei fehlt → kein Agent aktiv → kein Check.
> Die Session-Scope-Datei wird bei Stop-Event automatisch gelöscht.
>
> Diese Lösung ist pragmatisch und funktional. Elegantere Alternativen (z.B. AppArmor allein)
> sind in Schicht 2+3 bereits abgedeckt — der Hook ist Schicht 1 als zusätzliche Linie, kein SPOF.

- [ ] **Schritt 1: Hook-Skript schreiben**

  Datei: `.claude/hooks/pre-tool-use-boundary.sh`

  ```bash
  #!/bin/bash
  # pre-tool-use-boundary.sh — Filesystem Boundary Enforcement
  # PreToolUse-Hook: blockt Schreibzugriff außerhalb des Agent-ROOT
  #
  # Umgebungsvariablen (von Claude Code gesetzt):
  #   CLAUDE_TOOL_NAME    — Name des aufgerufenen Tools
  #   CLAUDE_TOOL_INPUT   — JSON-Input des Tools (enthält file_path, command, etc.)
  #   CLAUDE_SESSION_ID   — Session-ID (für Session-Scope-Datei)
  #
  # Agent-Identität: aus /tmp/claude-active-agent-<SESSION_ID> (vom Agenten gesetzt)

  set -euo pipefail

  TOOL="${CLAUDE_TOOL_NAME:-}"
  SESSION="${CLAUDE_SESSION_ID:-default}"
  AGENT_FILE="/tmp/claude-active-agent-${SESSION}"

  # Nur Schreib-Tools prüfen
  WRITE_TOOLS=("Write" "Edit" "Bash" "NotebookEdit")
  is_write_tool=false
  for wt in "${WRITE_TOOLS[@]}"; do
    if [[ "$TOOL" == "$wt" ]]; then
      is_write_tool=true
      break
    fi
  done

  if [[ "$is_write_tool" == "false" ]]; then
    exit 0  # Kein Schreib-Tool — kein Check nötig
  fi

  # Agent-Identität aus Session-Scope-Datei lesen
  if [[ ! -f "$AGENT_FILE" ]]; then
    exit 0  # Kein aktiver Agent registriert — kein Check (direkter Nutzer-Aufruf)
  fi

  AGENT=$(cat "$AGENT_FILE" 2>/dev/null || echo "")
  if [[ -z "$AGENT" ]]; then
    exit 0
  fi

  # ROOT je Agent bestimmen
  declare -A AGENT_ROOTS
  AGENT_ROOTS["Forge"]="/home/ubhp-nova/claude-c/pjc3-docker"
  AGENT_ROOTS["Nexus Projekt"]="/home/ubhp-nova/claude-c/pjc3-docker"
  AGENT_ROOTS["Memory Agent"]="/home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis"
  AGENT_ROOTS["Aegis Core"]="/home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/tasks"
  AGENT_ROOTS["Argus Sentinel"]="/home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings"
  AGENT_ROOTS["Nexus Global"]="/home/ubhp-nova/claude-c/pjc3/langzeitgedaechnis/findings"

  AGENT_ROOT="${AGENT_ROOTS[$AGENT]:-}"

  if [[ -z "$AGENT_ROOT" ]]; then
    exit 0  # Unbekannter Agent-Name — kein Check
  fi

  # Pfad aus Tool-Input extrahieren (stdin in Claude Code Hooks — CLAUDE_TOOL_INPUT als Fallback)
  INPUT="${CLAUDE_TOOL_INPUT:-}"
  TARGET_PATH=$(echo "$INPUT" | python3 -c "
  import json, sys
  try:
    d = json.load(sys.stdin)
    print(d.get('file_path', d.get('command', '')))
  except:
    print('')
  " 2>/dev/null || true)

  if [[ -z "$TARGET_PATH" ]]; then
    exit 0  # Kein Pfad erkennbar — AppArmor hält den Rest
  fi

  # Realpath auflösen (verhindert ../ Traversal)
  REAL_TARGET=$(realpath -m "$TARGET_PATH" 2>/dev/null || echo "$TARGET_PATH")

  # Boundary-Check
  if [[ "$REAL_TARGET" != "$AGENT_ROOT"* ]]; then
    echo "BOUNDARY VIOLATION: $AGENT versucht ausserhalb ROOT zu schreiben"
    echo "   ROOT: $AGENT_ROOT"
    echo "   Ziel: $REAL_TARGET"
    echo "   Tool: $TOOL"
    exit 1  # Hook-Exit 1 = Tool-Aufruf wird blockiert
  fi

  exit 0
  ```

- [ ] **Schritt 2: Hook ausführbar machen**

  ```bash
  chmod +x /home/ubhp-nova/claude-c/pjc3/.claude/hooks/pre-tool-use-boundary.sh
  ```

- [ ] **Schritt 3: Hook in settings.json registrieren**

  Aktuelle `pjc3/.claude/settings.json` lesen, dann Hook-Eintrag hinzufügen:

  ```json
  {
    "enabledPlugins": {
      "qodo-skills@claude-plugins-official": true,
      "claude-code-setup@claude-plugins-official": true
    },
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "",
          "hooks": [
            {
              "type": "command",
              "command": "bash /home/ubhp-nova/claude-c/pjc3/.claude/hooks/pre-tool-use-boundary.sh"
            }
          ]
        }
      ]
    }
  }
  ```

- [ ] **Schritt 4: Verifikation — Hook-Syntax**

  ```bash
  python3 -m json.tool /home/ubhp-nova/claude-c/pjc3/.claude/settings.json > /dev/null && echo "JSON valid"
  ```

  Erwartetes Ergebnis: "JSON valid"

- [ ] **Schritt 5: Commit**

  ```bash
  git add .claude/hooks/pre-tool-use-boundary.sh .claude/settings.json
  git commit -m "feat: PreToolUse boundary hook — layer 1 filesystem enforcement"
  ```

---

### Task 10b: PostToolUse Hook — Argus-Trigger Stub (Stufe 3)

**Dateien:**
- Create: `pjc3/.claude/hooks/post-tool-use-argus.sh`
- Modify: `pjc3/.claude/settings.json` (Hook registrieren)

> Spec Stufe 3: "PostToolUse: Argus-Trigger nach Forge-Abschluss"
> Der exakte Dispatch-Mechanismus (Hook → Aegis Core → Argus) ist als offener Punkt in der Spec.
> Dieser Task implementiert einen Stub — der Hook existiert und ist registriert, die eigentliche
> Dispatch-Logik wird in einer separaten Design-Spec ausgearbeitet.
> Ziel: Stufe 3 ist nach diesem Task vollständig registriert (alle 3 Hooks vorhanden).

- [ ] **Schritt 1: Stub-Hook schreiben**

  Datei: `.claude/hooks/post-tool-use-argus.sh`

  ```bash
  #!/bin/bash
  # post-tool-use-argus.sh — PostToolUse Hook (Stub)
  # Trigger: nach jedem Tool-Aufruf durch Forge-Agent
  #
  # Status: STUB — Dispatch-Logik (Hook → Aegis Core → Argus) noch offen.
  # Wenn Forge-Agent aktiv und Task abgeschlossen, hier Aegis Core benachrichtigen.
  #
  # Vollständige Implementierung: eigene Design-Spec ("PostToolUse-Argus-Dispatch")

  TOOL="${CLAUDE_TOOL_NAME:-}"
  SESSION="${CLAUDE_SESSION_ID:-default}"
  AGENT_FILE="/tmp/claude-active-agent-${SESSION}"

  # Nur aktiv wenn Forge-Agent läuft
  if [[ ! -f "$AGENT_FILE" ]]; then
    exit 0
  fi

  AGENT=$(cat "$AGENT_FILE" 2>/dev/null || echo "")
  if [[ "$AGENT" != "Forge" ]]; then
    exit 0
  fi

  # TODO: Dispatch-Logik implementieren
  # echo "[PostToolUse] Forge completed $TOOL — Aegis Core notify for Argus review"
  exit 0
  ```

- [ ] **Schritt 2: Hook ausführbar machen**

  ```bash
  chmod +x /home/ubhp-nova/claude-c/pjc3/.claude/hooks/post-tool-use-argus.sh
  ```

- [ ] **Schritt 3: PostToolUse in settings.json eintragen**

  `settings.json` `hooks`-Block um PostToolUse ergänzen:

  ```json
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash /home/ubhp-nova/claude-c/pjc3/.claude/hooks/post-tool-use-argus.sh"
          }
        ]
      }
    ],
    "Stop": [...]
  }
  ```

- [ ] **Schritt 4: Commit**

  ```bash
  git add .claude/hooks/post-tool-use-argus.sh .claude/settings.json
  git commit -m "feat: PostToolUse stub hook — argus trigger placeholder (Stufe 3 complete)"
  ```

---

### Task 11: SessionEnd Hook — Memory Agent Checkliste

**Dateien:**
- Create: `pjc3/.claude/hooks/session-end-memory.sh`
- Modify: `pjc3/.claude/settings.json` (Hook registrieren)

> Trigger: vor /clear → Memory Agent bekommt Checkliste → bestätigt → /clear startet.
> Technischer Mechanismus (SessionEnd-Hook) ist als offener Punkt in der Spec markiert.
> Implementierung hier: Checkliste als Prompt-Datei die der Memory Agent lesen muss.

- [ ] **Schritt 1: Checklisten-Datei aus Task 3 verifizieren**

  Die Checklisten-Datei wurde bereits in Task 3 (Schritt 3) angelegt.
  Sicherstellen dass sie vorhanden und korrekt ist:

  ```bash
  cat /home/ubhp-nova/claude-c/pjc3/.claude/hooks/session-end-checklist.md
  ```

  Erwartetes Ergebnis: Datei existiert mit `MEMORY-AGENT-SESSIONEND: OK` als letzter Zeile.
  Falls die Datei fehlt → Task 3 Schritt 3 nachholen.

- [ ] **Schritt 2: SessionEnd-Hook schreiben**

  Datei: `.claude/hooks/session-end-memory.sh`

  ```bash
  #!/bin/bash
  # session-end-memory.sh — SessionEnd Hook
  # Erinnert den Nutzer an die Memory-Agent-Checkliste vor /clear
  #
  # Hinweis: Claude Code SessionEnd-Hook läuft nach der letzten Antwort.
  # Dieser Hook gibt eine Erinnerung aus — der Memory Agent muss manuell
  # dispatcht werden (automatisches Dispatching noch offen als Design-Punkt).

  echo ""
  echo "════════════════════════════════════════════"
  echo "  SESSION-ENDE — Memory Agent Checkliste"
  echo "════════════════════════════════════════════"
  echo ""
  echo "  Vor /clear den Memory Agent dispatchen:"
  echo "  → Offene Tasks archivieren"
  echo "  → Entscheidungen verdichten"
  echo "  → Fehler dokumentieren"
  echo "  → Bestätigung abwarten: MEMORY-AGENT-SESSIONEND: OK"
  echo ""
  echo "  Checkliste: .claude/hooks/session-end-checklist.md"
  echo "════════════════════════════════════════════"
  ```

- [ ] **Schritt 3: Hook ausführbar machen**

  ```bash
  chmod +x /home/ubhp-nova/claude-c/pjc3/.claude/hooks/session-end-memory.sh
  ```

- [ ] **Schritt 4: SessionEnd-Hook in settings.json eintragen**

  `settings.json` `hooks`-Block um SessionEnd ergänzen:

  ```json
  "hooks": {
    "PreToolUse": [...],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash /home/ubhp-nova/claude-c/pjc3/.claude/hooks/session-end-memory.sh"
          }
        ]
      }
    ]
  }
  ```

  > Hinweis: Claude Code verwendet "Stop" für Session-Ende-Events, nicht "SessionEnd".

- [ ] **Schritt 5: Commit**

  ```bash
  git add .claude/hooks/session-end-memory.sh .claude/hooks/session-end-checklist.md .claude/settings.json
  git commit -m "feat: SessionEnd hook — memory agent checklist reminder before /clear"
  ```

---

### Task 12: Plan-Datei aktualisieren + CLAUDE.md

**Dateien:**
- Modify: `docs/superpowers/plans/2026-03-15-pyramid-core-migration.md`
- Modify: `CLAUDE.md`

> Die Agenten-Architektur war ein neuer Designbereich — der ursprüngliche Migrationsplan kennt diesen Implementierungsplan noch nicht.

- [ ] **Schritt 1: Migrationsplan-Status aktualisieren**

  In `docs/superpowers/plans/2026-03-15-pyramid-core-migration.md`:

  Unter `### Phase 1` einen Hinweis eintragen:
  ```markdown
  > **Agenten-Architektur:** Implementierungsplan in `docs/superpowers/plans/2026-03-16-migration-agenten-implementierung.md`
  > Stufen 1–8 aus Design-Spec `docs/superpowers/specs/2026-03-16-migration-agenten-design.md`
  ```

- [ ] **Schritt 2: CLAUDE.md Aktive Pläne aktualisieren**

  In `CLAUDE.md` den Abschnitt "Aktive Pläne" erweitern:

  ```markdown
  | 1 | `docs/superpowers/plans/2026-03-16-migration-agenten-implementierung.md` | **Nächste Session: Chunk 1 (System-Fundament)** |
  ```

- [ ] **Schritt 3: Commit**

  ```bash
  git add docs/superpowers/plans/2026-03-15-pyramid-core-migration.md CLAUDE.md
  git commit -m "docs: link agenten-implementierung plan in migration plan + CLAUDE.md"
  ```

---

## Offene Punkte (aus Spec — nicht in diesem Plan)

Diese Punkte sind als offen markiert und werden in separaten Design-Specs geklärt:

| Punkt | Status |
|-------|--------|
| Task Envelope — genaues Dateiformat (YAML vs. Markdown-Header) | Offen — Template als Markdown-Header implementiert, YAML optional später |
| PostToolUse-Trigger (Argus nach Forge) — exakte Hook-Konfiguration | Offen — Argus-Trigger-Mechanismus beschrieben aber Hook noch nicht implementiert |
| Vault — Technologie noch offen (Vaultwarden?) | Platzhalter angelegt |
| NOVA_ROADMAP.md Klarstellungs-Vermerk | Am Session-Ende einmalig eintragen |

---

## Verifikationsmatrix (Abschluss-Check)

Nach vollständiger Implementierung aller Tasks.
Stufen entsprechen der Spec-Implementierungsreihenfolge (Stufe 1–8).

| Spec-Stufe | Verifikation | Erwartetes Ergebnis |
|-----------|-------------|-------------------|
| Stufe 1 (POSIX) | `ls -lan /srv/agents/` | 6 Verzeichnisse, uid 1001–1006, chmod 700 |
| Stufe 1 (POSIX-Test) | `sudo -u forge-pjc3-docker-agent touch /pjc3/test.txt` | Permission denied |
| Stufe 1 (AppArmor) | `sudo aa-status \| grep -E "forge-pjc3-docker\|argus\|memory-agent"` | 6 Profile in enforce mode |
| Stufe 2 (Ordner) | `find langzeitgedaechnis -type f \| sort` | 5 .gitkeep + README.md + session-end-checklist.md |
| Stufe 3 (Hooks) | `python3 -m json.tool .claude/settings.json` | JSON valid, PreToolUse + PostToolUse + Stop registriert |
| Stufe 4 (Aegis Core) | `head -3 .claude/agents/aegis-core.md` | YAML Frontmatter mit `name: Aegis Core` |
| Stufe 5 (Forge) | `head -3 pjc3-docker/.claude/agents/forge.md` | YAML Frontmatter mit `name: Forge` |
| Stufe 6 (Argus) | `head -3 .claude/agents/argus-sentinel.md` | YAML Frontmatter mit `name: Argus Sentinel` |
| Stufe 7 (Nexus Projekt) | `head -3 pjc3-docker/.claude/agents/nexus-projekt.md` | YAML Frontmatter mit `name: Nexus Projekt` |
| Stufe 8 (Nexus Global) | `grep "STATUS: INAKTIV" .claude/agents/nexus-global.md` | Zeile gefunden — noch nicht aktiviert |
