import os
import subprocess
import sys

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("ETL_Controller")


@mcp.tool()
def starte_extraktion(profil_name: str) -> str:
    profil_pfad = f"profiles/{profil_name}.json"

    if not os.path.exists(profil_pfad):
        return f"Fehler: Profil-Datei nicht gefunden: {profil_pfad}"

    try:
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

        subprocess.run(
            [sys.executable, "radar.py", "--label", "Ruhezustand"],
            check=True,
        )

        return f"Erfolg: {output}"
    except subprocess.CalledProcessError as exc:
        fehlermeldung = (exc.stderr or exc.stdout or str(exc)).strip()
        return f"Fehler beim Ausführen der Extraktion: {fehlermeldung}"


if __name__ == "__main__":
    mcp.run()