import subprocess
import sys
import os
from datetime import datetime
import argparse

OUTPUT_FILE = "SYSTEM_VISUALIZATION.md"


def _run(cmd: list) -> str:
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


def get_docker_containers() -> list:
    output = _run(["docker", "ps", "--format", "{{.Names}} ({{.Status}})"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_python_processes() -> list:
    output = _run(["ps", "aux"])
    hits = []
    for line in output.splitlines():
        if "extractor.py" in line and "grep" not in line:
            parts = line.split()
            pid = parts[1] if len(parts) > 1 else "?"
            hits.append(f"extractor.py (PID {pid})")
    return hits


def build_mermaid(containers: list, processes: list, label: str) -> str:
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


def run(label: str = "Snapshot") -> None:
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
    parser = argparse.ArgumentParser(description="System-Radar")
    parser.add_argument("--label", default="Snapshot", help="Zustandsbezeichnung")
    args = parser.parse_args()
    run(args.label)
