#!/usr/bin/env python3
# LADESTUFE 3 — RESSOURCE
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: CSV-Datei lesen, filtern, transformieren und schreiben.
#               Standardbibliothek — kein pip-Install erforderlich.
# VERWENDUNG:   python csv_verarbeitung.py <modus> <eingabe.csv> [ausgabe.csv] [optionen]
#
# Modi:
#   lesen    <datei>                         → Alle Zeilen als Dicts ausgeben (stdout)
#   filtern  <datei> <spalte> <wert>         → Nur Zeilen, wo spalte == wert
#   spalten  <datei> <sp1,sp2,...>           → Nur gewählte Spalten behalten
#   sortieren <datei> <spalte> [--abst]     → Sortieren nach Spalte (--abst = absteigend)
#   info     <datei>                         → Statistik: Zeilen, Spalten, Encoding-Check

import csv
import sys
from pathlib import Path


def _oeffne(pfad: str) -> Path:
    p = Path(pfad)
    if not p.exists():
        print(f"FEHLER: Datei nicht gefunden: {pfad}", file=sys.stderr)
        sys.exit(1)
    return p


def lese_csv(pfad: str) -> list[dict]:
    """Liest CSV sicher als Liste von Dicts (utf-8, dann latin-1 als Fallback)."""
    p = _oeffne(pfad)
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with p.open(newline="", encoding=encoding) as f:
                daten = list(csv.DictReader(f))
            return daten
        except UnicodeDecodeError:
            continue
    print(f"FEHLER: Encoding konnte nicht bestimmt werden: {pfad}", file=sys.stderr)
    sys.exit(1)


def schreibe_csv(daten: list[dict], pfad: str) -> None:
    """Schreibt Liste von Dicts als CSV (utf-8, mit Header)."""
    if not daten:
        print("WARNUNG: Keine Daten zum Schreiben.", file=sys.stderr)
        return
    felder = list(daten[0].keys())
    ziel = Path(pfad)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with ziel.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=felder)
        writer.writeheader()
        writer.writerows(daten)
    print(f"OK | Geschrieben: {ziel.resolve()} ({len(daten)} Zeilen)")


def cmd_lesen(args: list[str]) -> None:
    if len(args) < 1:
        print("VERWENDUNG: lesen <datei.csv>", file=sys.stderr); sys.exit(1)
    daten = lese_csv(args[0])
    if not daten:
        print("INFO: CSV ist leer oder hat nur einen Header.")
        return
    for i, zeile in enumerate(daten, 1):
        print(f"[{i:>4}] {dict(zeile)}")
    print(f"\nGesamt: {len(daten)} Zeilen | Spalten: {list(daten[0].keys())}")


def cmd_filtern(args: list[str]) -> None:
    if len(args) < 3:
        print("VERWENDUNG: filtern <datei.csv> <spalte> <wert> [ausgabe.csv]", file=sys.stderr); sys.exit(1)
    daten = lese_csv(args[0])
    spalte, wert = args[1], args[2]
    if spalte not in (daten[0].keys() if daten else []):
        print(f"FEHLER: Spalte '{spalte}' nicht in CSV. Verfügbar: {list(daten[0].keys())}", file=sys.stderr)
        sys.exit(1)
    gefiltert = [z for z in daten if z.get(spalte, "").strip() == wert.strip()]
    print(f"INFO: {len(gefiltert)} von {len(daten)} Zeilen entsprechen '{spalte} == {wert}'")
    if len(args) >= 4:
        schreibe_csv(gefiltert, args[3])
    else:
        for z in gefiltert:
            print(dict(z))


def cmd_spalten(args: list[str]) -> None:
    if len(args) < 2:
        print("VERWENDUNG: spalten <datei.csv> <sp1,sp2,...> [ausgabe.csv]", file=sys.stderr); sys.exit(1)
    daten = lese_csv(args[0])
    gewaehlt = [s.strip() for s in args[1].split(",")]
    if daten:
        fehler = [s for s in gewaehlt if s not in daten[0]]
        if fehler:
            print(f"FEHLER: Unbekannte Spalten: {fehler}. Verfügbar: {list(daten[0].keys())}", file=sys.stderr)
            sys.exit(1)
    reduziert = [{s: z[s] for s in gewaehlt} for z in daten]
    print(f"INFO: {len(reduziert)} Zeilen, Spalten: {gewaehlt}")
    if len(args) >= 3:
        schreibe_csv(reduziert, args[2])
    else:
        for z in reduziert:
            print(dict(z))


def cmd_sortieren(args: list[str]) -> None:
    if len(args) < 2:
        print("VERWENDUNG: sortieren <datei.csv> <spalte> [--abst] [ausgabe.csv]", file=sys.stderr); sys.exit(1)
    daten = lese_csv(args[0])
    spalte = args[1]
    absteigend = "--abst" in args
    ausgabe = next((a for a in args[2:] if not a.startswith("--")), None)

    def sort_key(z):
        v = z.get(spalte, "")
        try:
            return (0, float(v))
        except (ValueError, TypeError):
            return (1, str(v).lower())

    sortiert = sorted(daten, key=sort_key, reverse=absteigend)
    richtung = "absteigend" if absteigend else "aufsteigend"
    print(f"INFO: {len(sortiert)} Zeilen, sortiert nach '{spalte}' ({richtung})")
    if ausgabe:
        schreibe_csv(sortiert, ausgabe)
    else:
        for z in sortiert:
            print(dict(z))


def cmd_info(args: list[str]) -> None:
    if len(args) < 1:
        print("VERWENDUNG: info <datei.csv>", file=sys.stderr); sys.exit(1)
    p = _oeffne(args[0])
    daten = lese_csv(args[0])
    groesse_kb = p.stat().st_size / 1024
    spalten = list(daten[0].keys()) if daten else []
    print(f"Datei:    {p.resolve()}")
    print(f"Größe:    {groesse_kb:.1f} KB")
    print(f"Zeilen:   {len(daten)} (ohne Header)")
    print(f"Spalten:  {len(spalten)}")
    print(f"Namen:    {spalten}")


BEFEHLE = {
    "lesen":     cmd_lesen,
    "filtern":   cmd_filtern,
    "spalten":   cmd_spalten,
    "sortieren": cmd_sortieren,
    "info":      cmd_info,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in BEFEHLE:
        print(f"VERWENDUNG: python csv_verarbeitung.py <modus> [...]")
        print(f"Modi: {', '.join(BEFEHLE.keys())}")
        sys.exit(1)

    modus = sys.argv[1]
    BEFEHLE[modus](sys.argv[2:])
