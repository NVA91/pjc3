# MEMORY: struktur_visualizer.py
# Erweiterungsäste: struktur_visualizer_filter.py (eigene Filterkonfiguration)
# Verknüpft mit: radar.py → gleicher Output-Ansatz (SYSTEM_VISUALIZATION.md)

"""
Rekursiver ASCII-Tree-Generator für ~/claude-c/
Output: STRUKTUR.md (gitignored)
"""

import sys
from pathlib import Path

# Verzeichnisse die ignoriert werden
IGNORE_DIRS = {
    ".git", "venv", "__pycache__", "node_modules",
    ".venv", "dist", "build", ".mypy_cache", ".pytest_cache",
    "cache", ".ruff_cache", "eggs", ".eggs",
}

# Dateien die ignoriert werden
IGNORE_FILES = {
    ".DS_Store", "Thumbs.db", "*.pyc", "*.pyo",
}

def should_ignore(name: str) -> bool:
    if name in IGNORE_DIRS:
        return True
    if name.startswith(".") and name not in {".env.example", ".gitignore", ".mcp.json"}:
        return True
    return False


def build_tree(path: Path, prefix: str = "", is_last: bool = True) -> list[str]:
    lines = []
    connector = "└── " if is_last else "├── "
    lines.append(f"{prefix}{connector}{path.name}/")

    child_prefix = prefix + ("    " if is_last else "│   ")

    try:
        entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        lines.append(f"{child_prefix}└── [Zugriff verweigert]")
        return lines

    visible = [e for e in entries if not should_ignore(e.name)]

    for i, entry in enumerate(visible):
        last = i == len(visible) - 1
        if entry.is_dir():
            lines.extend(build_tree(entry, child_prefix, last))
        else:
            file_connector = "└── " if last else "├── "
            lines.append(f"{child_prefix}{file_connector}{entry.name}")

    return lines


def main():
    root = Path.home() / "claude-c"
    if not root.exists():
        print(f"Fehler: {root} nicht gefunden", file=sys.stderr)
        sys.exit(1)

    lines = [f"# Struktur: {root}\n", "```"]

    try:
        top_entries = sorted(root.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        print("Fehler: Kein Zugriff auf Wurzelverzeichnis", file=sys.stderr)
        sys.exit(1)

    visible = [e for e in top_entries if not should_ignore(e.name)]

    lines.append(f"{root.name}/")
    for i, entry in enumerate(visible):
        last = i == len(visible) - 1
        if entry.is_dir():
            lines.extend(build_tree(entry, "", last))
        else:
            connector = "└── " if last else "├── "
            lines.append(f"{connector}{entry.name}")

    lines.append("```")
    lines.append("")

    output = Path.home() / "claude-c" / "pjc3" / "STRUKTUR.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ Gespeichert: {output}")


if __name__ == "__main__":
    main()
