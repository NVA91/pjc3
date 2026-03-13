# Radar Visualization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Systemzustand visuell als Mermaid-Flowchart überwachen — vor/nach Extraktion.

**Architecture:** `radar.py` fragt Docker-Container und Python-Prozesse sicher per `subprocess.run` (Array-Form) ab, generiert einen Mermaid-`graph TD`-Block und schreibt ihn in `SYSTEM_VISUALIZATION.md`. `mcp_gateway.py` ruft `radar.py` via `sys.executable` zweimal auf: einmal vor, einmal nach `extractor.py`.

**Tech Stack:** Python 3 (stdlib: subprocess, sys, os, datetime), FastMCP, Mermaid.js (Markdown-Ausgabe)

---

## Chunk 1: radar.py

### Task 1: radar.py — Docker-Abfrage

**Files:**
- Create: `radar.py`

- [ ] **Step 1: Datei anlegen, Docker-Abfrage schreiben**

```python
import subprocess
import sys
import os
from datetime import datetime

def _run(cmd: list[str]) -> str:
    """Führt Befehl sicher aus, gibt stdout zurück (leer bei Fehler)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return ""

def get_docker_containers() -> list[str]:
    """Gibt Liste aktiver Docker-Container-Namen zurück."""
    output = _run(["docker", "ps", "--format", "{{.Names}} ({{.Status}})"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]
```

- [ ] **Step 2: Manuell testen**

```bash
source venv/bin/activate
python -c "import radar; print(radar.get_docker_containers())"
```

Erwartet: Liste (leer = kein Docker aktiv, das ist OK).

---

### Task 2: radar.py — Python-Prozess-Abfrage

**Files:**
- Modify: `radar.py`

- [ ] **Step 1: Funktion für aktive Python-Prozesse ergänzen**

```python
def get_python_processes() -> list[str]:
    """Gibt PIDs + Skriptname für laufende extractor.py-Prozesse zurück."""
    output = _run(["ps", "aux"])
    hits = []
    for line in output.splitlines():
        if "extractor.py" in line and "grep" not in line:
            parts = line.split()
            pid = parts[1] if len(parts) > 1 else "?"
            hits.append(f"extractor.py (PID {pid})")
    return hits
```

- [ ] **Step 2: Manuell testen**

```bash
python -c "import radar; print(radar.get_python_processes())"
```

Erwartet: Leere Liste (kein Extraktor läuft gerade).

---

### Task 3: radar.py — Mermaid-Diagramm generieren

**Files:**
- Modify: `radar.py`

- [ ] **Step 1: Diagramm-Generator schreiben**

```python
def build_mermaid(containers: list[str], processes: list[str], label: str) -> str:
    """Erstellt Mermaid graph TD mit Farbmarkierungen."""
    lines = ["graph TD"]
    lines.append(f'    SYS["System — {label}"]')

    if containers:
        lines.append('    SYS --> DOCKER["Docker"]')
        for i, c in enumerate(containers):
            node = f"DC{i}"
            lines.append(f'    DOCKER --> {node}["{c}"]')
            lines.append(f"    style {node} fill:#4CAF50,color:#fff")
    else:
        lines.append('    SYS --> DOCKER_IDLE["Docker: keine Container"]')
        lines.append("    style DOCKER_IDLE fill:#9E9E9E,color:#fff")

    if processes:
        lines.append('    SYS --> PROCS["Python-Prozesse"]')
        for i, p in enumerate(processes):
            node = f"PR{i}"
            lines.append(f'    PROCS --> {node}["{p}"]')
            lines.append(f"    style {node} fill:#4CAF50,color:#fff")
    else:
        lines.append('    SYS --> PROCS_IDLE["Extraktor: inaktiv"]')
        lines.append("    style PROCS_IDLE fill:#9E9E9E,color:#fff")

    return "\n".join(lines)
```

- [ ] **Step 2: Manuell testen**

```bash
python -c "
import radar
d = radar.get_docker_containers()
p = radar.get_python_processes()
print(radar.build_mermaid(d, p, 'Test'))
"
```

Erwartet: Gültiger Mermaid-Block mit grauen Idle-Knoten.

---

### Task 4: radar.py — Datei schreiben + main()

**Files:**
- Modify: `radar.py`

- [ ] **Step 1: Schreibfunktion + Einstiegspunkt ergänzen**

```python
OUTPUT_FILE = "SYSTEM_VISUALIZATION.md"

def run(label: str = "Snapshot") -> None:
    """Erzeugt Snapshot und schreibt SYSTEM_VISUALIZATION.md."""
    containers = get_docker_containers()
    processes = get_python_processes()
    diagram = build_mermaid(containers, processes, label)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""# System Visualization

**Zeitstempel:** {ts}
**Zustand:** {label}

```mermaid
{diagram}
```
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[radar] {OUTPUT_FILE} aktualisiert ({label})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="Snapshot", help="Zustandsbezeichnung")
    args = parser.parse_args()
    run(args.label)
```

- [ ] **Step 2: End-to-End-Test**

```bash
python radar.py --label "Ruhezustand"
cat SYSTEM_VISUALIZATION.md
```

Erwartet: Markdown-Datei mit Mermaid-Block wird ausgegeben.

- [ ] **Step 3: Commit**

```bash
git add radar.py SYSTEM_VISUALIZATION.md
git commit -m "feat: add radar.py system visualization"
```

---

## Chunk 2: mcp_gateway.py anpassen

### Task 5: radar.py vor/nach extractor.py aufrufen

**Files:**
- Modify: `mcp_gateway.py`

- [ ] **Step 1: Zwei radar-Aufrufe in starte_extraktion() einbauen**

Ersetze den `try`-Block in `starte_extraktion()`:

```python
    try:
        # Radar: Vor-Snapshot (Extraktion läuft)
        subprocess.run(
            [sys.executable, "radar.py", "--label", "Extraktion läuft"],
            check=True,
        )

        result = subprocess.run(
            [sys.executable, "extractor.py", "--profile", profil_pfad],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip() or "Extraktion erfolgreich gestartet."

        # Radar: Nach-Snapshot (Ruhezustand)
        subprocess.run(
            [sys.executable, "radar.py", "--label", "Ruhezustand"],
            check=True,
        )

        return f"Erfolg: {output}"
    except subprocess.CalledProcessError as exc:
        fehlermeldung = (exc.stderr or exc.stdout or str(exc)).strip()
        return f"Fehler beim Ausführen der Extraktion: {fehlermeldung}"
```

- [ ] **Step 2: Lokal testen**

```bash
python -c "
import subprocess, sys
subprocess.run([sys.executable, 'mcp_gateway.py', '--help'])
"
```

Oder direkt via MCP-Tool `starte_extraktion` mit Profil `legal` testen.

- [ ] **Step 3: Commit**

```bash
git add mcp_gateway.py
git commit -m "feat: integrate radar.py into mcp_gateway extraction flow"
```
