import argparse
import time

parser = argparse.ArgumentParser(description="PDF-Datenextraktor (Dummy)")
parser.add_argument("--profile", required=True, help="Pfad zur Profil-JSON-Datei")
args = parser.parse_args()

print(f"Starte sichere Extraktion fuer Profil: {args.profile}...")
time.sleep(2)
print("Extraktion erfolgreich. Daten in DB gespeichert.")
