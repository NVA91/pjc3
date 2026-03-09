---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: container-skill
description: >
  Agenten in kurzlebigen Docker-Containern: node:20-slim (Debian, kein Alpine),
  Non-Root-User (useradd -m -u 1001), UID-Passthrough (-u $(id -u):$(id -g)),
  ephemere Dateisysteme (--rm), Volume-Mounts mit Schreibrecht-Kontrolle,
  YOLO-Modus (--dangerously-skip-permissions) in Docker Desktop Sandboxes / MicroVMs.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Container-Ausführung
    description: >
      Agenten in kurzlebigen Docker-Containern: node:20-slim (Debian, kein Alpine),
      Non-Root-User (useradd -m -u 1001), UID-Passthrough (-u $(id -u):$(id -g)),
      ephemere Dateisysteme (--rm), Volume-Mounts mit Schreibrecht-Kontrolle,
      YOLO-Modus (--dangerously-skip-permissions) in Docker Desktop Sandboxes / MicroVMs

triggers:
  # Container-Ausführung / Docker / Agent-Isolation
  - Dockerfile für Agenten-Ausführung erstellen (node:20-slim, Non-Root)
  - Warum Alpine für NPM-Agenten ungeeignet ist (musl libc Linker-Fehler)
  - Non-Root-User im Container anlegen (useradd -m -u 1001)
  - Docker-Basis-Image für CLI-Agenten wählen und sichern
  - docker run mit UID-Passthrough (-u $(id-u):$(id-g)) konfigurieren
  - Read-Only-Filesystem-Fehler durch fehlenden UID-Passthrough debuggen
  - Kurzlebige Container mit --rm und Volume-Mount für Workspace aufsetzen
  - Agenten-Dateisystem nach Session-Ende rückstandslos verwerfen
  - --dangerously-skip-permissions für autonome Write-Ops im Container aktivieren
  - YOLO-Modus: Code schreiben, Container bauen und E2E-Tests in MicroVM ausführen
  - Docker Desktop Sandboxes / MicroVMs für isolierte Agenten-Umgebungen einrichten

resources:
  - resources/docker_agent_run.sh
---

# LADESTUFE 2 — INSTRUKTIONEN
# Wird on-demand geladen, sobald semantische Übereinstimmung mit den Triggern
# erkannt wird (via `cat SKILL.md` im Hintergrund). Moderat: < 5.000 Token.
# Definiert Prozessschritte, Regeln und Leitplanken — kein vollständiger Code.

## Arbeitsweise (Reihenfolge einhalten)

1. **Anforderung klären** — Zieldatei, Pfad und Umfang mit dem Nutzer bestätigen, bevor irgendetwas geschrieben oder ausgeführt wird.
2. **Ressource auswählen** — Passende Ressource aus `resources/` benennen; der Nutzer entscheidet, ob sie ausgeführt wird.
3. **Dry-Run zuerst** — Destruktive oder schreibende Operationen immer zuerst simulieren (`--dry-run`, `echo`-Modus oder Ausgabe nach stdout).
4. **Freigabe einholen** — Vor jeder Dateiänderung: Zielpfad anzeigen, Bestätigung abwarten.
5. **Ausführen & protokollieren** — Ausgabe (stdout/stderr) dem Nutzer vollständig zeigen.

---

## Ladestufe-Übersicht

| Stufe | Komponente | Zeitpunkt | Token-Belastung | Funktionale Bedeutung |
|---|---|---|---|---|
| 1 | Metadaten (YAML-Frontmatter) | Initial beim Session-Start | ~100 Token | Trigger-Mechanismus: Relevanz-Bewertung durch das Modell |
| 2 | Instruktionen (diese Datei) | On-Demand bei semantischer Übereinstimmung | < 5.000 Token | Prozessschritte, Regeln, Leitplanken |
| 3 | Ressourcen (externe Skripte) | Bei explizitem Aufruf während der Ausführung | Nur stdout wird verrechnet | Skripte laufen in Sandbox; Quellcode belastet Kontextfenster nicht |

---

## Agenten-Ausführung in leichtgewichtigen Containern

Agenten-Prozesse werden in kurzlebige, ephemere Docker-Container ausgelagert.
Das Container-Dateisystem wird nach Beendigung der Session rückstandslos verworfen (`--rm`).
Diese Architektur verhindert persistente Seiteneffekte und Konfigurationsdrift.

### Basis-Image-Wahl: node:20-slim (Debian) — NICHT Alpine

| Kriterium | `node:20-slim` (Debian) | `node:20-alpine` (Alpine) |
|---|---|---|
| **C-Bibliothek** | glibc (GNU standard) | musl libc |
| **Native NPM-Pakete** | Vollständig kompatibel | Häufig Linker-Fehler bei nativen Modulen |
| **CLI-Agenten** (z.B. `@anthropic-ai/claude-code`) | Problemlos | Kryptische Fehler möglich |
| **Image-Größe** | ~200 MB (slim) | ~100 MB |
| **Empfehlung** | **Pflicht für NPM-CLI-Agenten** | Nur für einfache Node.js-Anwendungen |

**Warum musl libc Probleme macht:**
Native NPM-Pakete (`*.node`-Binaries) werden gegen glibc kompiliert. Alpine's musl libc ist
nicht ABI-kompatibel — beim Laden der Binary tritt ein Linker-Fehler auf:
`Error loading shared library libstdc++.so.6: No such file or directory`.
Workarounds (Kompatibilitäts-Pakete, Cross-Compilation) sind fragil und nicht produktionsgeeignet.

### Sicherheitskonformes Dockerfile (Standard-Template)

```dockerfile
# PFLICHT: node:20-slim (Debian-basiert) — KEIN Alpine (musl libc Inkompatibilität)
FROM node:20-slim

# Non-Root-User anlegen: UID 1001 (feste Zuweisung, nicht root)
# -m → Home-Verzeichnis anlegen (/home/claude)
# -u 1001 → feste UID, entspricht CLAUDE-Agent-Konvention aus CLAUDE.md
RUN useradd -m -u 1001 claude

# CLI-Agent global installieren (als root, vor USER-Wechsel)
RUN npm install -g @anthropic-ai/claude-code

# Workspace-Verzeichnis vorbereiten
WORKDIR /workspace

# Wechsel zum Non-Root-User VOR dem Entrypoint — kritisch für Sicherheit
USER claude

ENTRYPOINT ["claude"]
```

**Warum `USER claude` vor `ENTRYPOINT`?**
Wird der ENTRYPOINT als root ausgeführt, hat ein kompromittierter Agent-Prozess
effektive root-Rechte im Container. Der Wechsel zu UID 1001 reduziert den
Privilege-Level auf das absolute Minimum — konsistent mit dem UID-Namespace-
Isolations-Prinzip aus CLAUDE.md (Gebot UID-Namespace-Isolation).

### Laufzeit-Orchestrierung: docker run mit UID-Passthrough

```bash
# PFLICHT-Kommando für Lese- und Schreiboperationen:
docker run --rm \
  -v "$(pwd):/workspace" \
  -u "$(id -u):$(id -g)" \
  claude-agent-image \
  <claude-argumente>
```

**Parameter-Erklärung:**

| Parameter | Wert | Zweck |
|---|---|---|
| `--rm` | — | Container-Dateisystem nach Beendigung löschen (ephemer) |
| `-v "$(pwd):/workspace"` | Host-CWD → `/workspace` | Agent kann Host-Dateien lesen und schreiben |
| `-u "$(id -u):$(id -g)"` | Host-UID:GID | UID-Passthrough — kritisch für Schreibrecht |

**Warum `-u $(id -u):$(id -g)` kritisch ist:**

```
Ohne -u:
  Container läuft als UID 1001 (claude)
  Host-Dateien gehören UID 1000 (lokaler User)
  → Schreibzugriff verweigert: "Read-Only Filesystem"-Fehler
  → Agent kann keine Dateien im gemounteten Volume erzeugen/ändern

Mit -u $(id-u):$(id-g):
  Container übernimmt Host-UID und Host-GID
  → Dateieigentümer stimmt überein → Vollständiger Lese-/Schreibzugriff
  → Neu erzeugte Dateien gehören dem Host-User (kein sudo nötig)
```

**Fehler-Diagnose — "Read-Only Filesystem" im Container:**

```
Symptom: agent error: EROFS: read-only file system, open '/workspace/output.json'
Ursache:  -u-Flag fehlt → Container-UID ≠ Host-Datei-UID
Fix:      docker run ... -u "$(id -u):$(id -g)" ...
```

### Erweitertes Run-Kommando (mit Umgebungsvariablen)

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -u "$(id -u):$(id -g)" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  --network host \
  claude-agent-image \
  --print "Analysiere /workspace/daten.csv und schreibe Ergebnis nach /workspace/ergebnis.json"
```

**Sicherheits-Hinweise zum erweiterten Kommando:**
- `-e ANTHROPIC_API_KEY` → API-Key als Umgebungsvariable (kein File-Mount, da Claude Code ihn aus `$env` liest)
- `--network host` → Nur wenn Agent externe APIs aufrufen muss; andernfalls weglassen
- `--network none` → Vollständige Netzwerk-Isolation für rein lokale Verarbeitungsaufgaben

### Pflicht-Ablauf für Container-Agenten-Setup

1. **Image wählen** — `node:20-slim` (Pflicht); Alpine explizit ablehnen
2. **Non-Root-User** — `useradd -m -u 1001 claude`; UID mit CLAUDE.md-Konvention abgleichen
3. **Schreibrecht-Test** — `docker run --rm -v "$(pwd):/workspace" -u "$(id -u):$(id -g)" image touch /workspace/test.txt`
4. **Ephemer-Verhalten prüfen** — `--rm` Flag bestätigen; kein named Volume für Session-Daten
5. **API-Key** — Nur über `-e`-Flag übergeben; kein Hardcoding in Dockerfile oder Image

### YOLO-Modus: --dangerously-skip-permissions in Docker-Isolierung

Für autonome Write-Operationen (Code schreiben, Dateien erzeugen, Pakete installieren)
muss die interaktive Bestätigungslogik des Agenten deaktiviert werden.

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -u "$(id -u):$(id -g)" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  --network none \
  claude-agent-image \
  --dangerously-skip-permissions \
  --print "Schreibe Unit-Tests für alle Funktionen in /workspace/src/"
```

**Warum `--dangerously-skip-permissions` im Container architektonisch sicher ist:**

```
Ohne Docker:
  Agent läuft direkt auf Host → skip-permissions = voller Systemzugriff
  → GEFÄHRLICH auf der Entwicklerworkstation

Mit Docker:
  Agent läuft in isoliertem Container-FS
  → skip-permissions = Vollzugriff nur innerhalb des Containers
  → Host-System bleibt durch Docker-Isolationsgrenze geschützt
  → Container-FS wird nach Beendigung verworfen (--rm)
  → Primärer Schutzmechanismus = Docker-Isolation, nicht Permission-Dialog
```

**Wann YOLO-Modus angemessen ist:**

| Szenario | YOLO | Grund |
|---|---|---|
| Autonome Code-Generierung in Container | ✓ | Docker ist Sicherheitsgrenze |
| E2E-Tests in MicroVM ausführen | ✓ | Isoliertes Dateisystem |
| Direkter Einsatz auf Entwickler-Host | ✗ | Kein primärer Schutz |
| Produktionsserver | ✗ | Niemals |

### Docker Desktop Sandboxes / MicroVMs

Moderne Erweiterung: Docker Desktop Sandboxes implementieren spezialisierte MicroVMs,
die über Standard-Container-Isolation hinausgehen.

| Feature | Standard-Docker-Container | Docker Desktop Sandbox (MicroVM) |
|---|---|---|
| **Dateisystem-Isolation** | Container-FS (Overlay) | Vollständig isoliertes VM-Dateisystem |
| **Netzwerk-Kontrolle** | Bridge / host / none | Konfigurierbare Netzwerkzugriffsregeln pro VM |
| **Docker-Daemon** | Shared Host-Daemon | Privater Docker-Daemon pro Sandbox |
| **YOLO-Modus** | Architektonisch vertretbar | Vollständig sicher (MicroVM-Grenze) |
| **Use Case** | Standard-Agenten-Ausführung | "YOLO-Modus"-Agenten, CI/CD-Pipelines |

**YOLO-Modus in MicroVM — Maximale Autonomie:**
Der Agent kann in Höchstgeschwindigkeit Code schreiben, Container bauen und
End-to-End-Tests ausführen, ohne jegliches Risiko für die Entwicklerworkstation.
Die MicroVM-Grenze bildet eine härtere Isolationsschicht als Standard-Container.

---

## Sicherheitsregeln — niemals verletzen

- **Kein Dateizugriff ohne Freigabe**: Keine Datei öffnen, lesen oder schreiben ohne explizite Nutzererlaubnis.
- **Keine hardcodierten absoluten Pfade** außer `/tmp` — immer relative Pfade oder konfigurierbare Variablen.
- **Kein `rm -rf` ohne Guard** — immer `confirm()`-Pattern oder `--dry-run` vorschalten.
- **Variablen immer quoten**: `"$var"` statt `$var` (verhindert Wordsplitting und Globbing).
- **`set -euo pipefail` + `IFS=$'\n\t'`** in jedem Bash-Skript als erste ausführbare Zeile.
- **Temp-Files**: Nur via `mktemp` + `trap 'rm -f "$tmp"' EXIT`.

---

## Verwandte Ressourcen

| Ressource | Ladestufe | Kategorie | Inhalt |
|---|---|---|---|
| `resources/docker_agent_run.sh` | 3 | Container-Ausführung | node:20-slim Dockerfile + docker run (UID-Passthrough, YOLO-Modus, MicroVM-Hinweise) |
| `CLAUDE.md` → Docker-Sicherheit | — | — | Immutable Config, Volume Mounts, UID-Isolation |
