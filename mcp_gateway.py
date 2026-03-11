from pathlib import Path
import re
import subprocess

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("ETL_Controller")
PROJECT_ROOT = Path(__file__).resolve().parent
PROFILES_DIR = PROJECT_ROOT / "profiles"


@mcp.tool()
def starte_extraktion(profil_name: str) -> str:
    """Startet extractor.py mit einem sicheren Profil aus profiles/."""
    # Sicherheitsaspekt: Nur erwartete Zeichen erlauben (kein Path Traversal wie ../)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", profil_name or ""):
        return "Fehler: Ungültiger profil_name. Erlaubt sind nur Buchstaben, Zahlen, _ und -."

    profile_path = (PROFILES_DIR / f"{profil_name}.json").resolve()

    # Sicherheitsaspekt: Profil muss innerhalb des profiles-Verzeichnisses liegen
    if profile_path.parent != PROFILES_DIR.resolve():
        return "Fehler: Ungültiger Profilpfad erkannt."

    # Sicherheitsaspekt: Datei muss physisch vorhanden sein, sonst kein Start
    if not profile_path.is_file():
        return f"Fehler: Profil nicht gefunden: {profile_path}"

    cmd = [
        "python",
        "extractor.py",
        "--profile",
        str(profile_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return f"Fehler beim Starten der Extraktion: {exc}"

    if result.returncode == 0:
        output = result.stdout.strip() or "Extraktion erfolgreich gestartet (ohne Ausgabe)."
        return f"Erfolg:\n{output}"

    error_output = (result.stderr or result.stdout).strip() or "Unbekannter Fehler"
    return f"Fehler (Exit-Code {result.returncode}):\n{error_output}"


if __name__ == "__main__":
    mcp.run()