#!/usr/bin/env python3
# LADESTUFE 3 — RESSOURCE | KATEGORIE: Vision
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: Visuelle Dokumentenanalyse via Claude Vision API.
#               Keine simple OCR — kontextuelles Reasoning über Bilder.
#               Kein Hardcoding von API-Keys. Kein load_dotenv().
# VERWENDUNG:
#   python vision_dokument.py beschreiben  <bild.[png|jpg|webp]>
#   python vision_dokument.py rechnung     <bild.[png|jpg|webp]> [--format json|markdown]
#   python vision_dokument.py diagramm     <bild.[png|jpg|webp]> [--format json|markdown]
#   python vision_dokument.py screenshot   <bild.[png|jpg|webp]>
#   python vision_dokument.py batch        <verzeichnis/> <modus> [--ausgabe datei.jsonl]
# VORAUSSETZUNG:
#   export ANTHROPIC_API_KEY=sk-ant-...
#   pip install anthropic
# MODELL: claude-sonnet-4-6 (Standard aus CLAUDE.md)

from __future__ import annotations

import sys
import os
import base64
import json
from pathlib import Path
from datetime import datetime
from mimetypes import guess_type

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# =============================================================================
# KONFIGURATION
# =============================================================================

MODELL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
BILD_ENDUNGEN = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

# Konfidenz-Schwelle: Unterhalb dieser Grenze → Nutzer zur manuellen Prüfung auffordern
KONFIDENZ_SCHWELLE = 0.70


# =============================================================================
# UTILITIES
# =============================================================================

def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _log(modus: str, msg: str) -> None:
    print(f"[{_ts()}] [{modus}] {msg}", file=sys.stderr)

def _ok(msg: str) -> None:
    print(f"OK  | {msg}", file=sys.stderr)

def _warn(msg: str) -> None:
    print(f"WRN | {msg}", file=sys.stderr)

def _err(msg: str, code: int = 1) -> None:
    print(f"ERR | {msg}", file=sys.stderr)
    sys.exit(code)

def _pruefe_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key or not key.startswith("sk-ant-"):
        _err(
            "ANTHROPIC_API_KEY nicht gesetzt oder ungültig.\n"
            "    Ausführen: export ANTHROPIC_API_KEY=sk-ant-...\n"
            "    Hinweis: vision_dokument.py nutzt kein load_dotenv()."
        )
    return key

def _lade_bild(pfad: str) -> tuple[str, str]:
    """
    Lädt ein Bild als base64-String.
    Returns: (base64_data, media_type)
    """
    p = Path(pfad)
    if not p.exists():
        _err(f"Bilddatei nicht gefunden: {pfad}")
    if p.suffix.lower() not in BILD_ENDUNGEN:
        _err(f"Nicht unterstütztes Format: {p.suffix} | Erlaubt: {BILD_ENDUNGEN}")

    mime, _ = guess_type(str(p))
    if not mime:
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"

    data = base64.standard_b64encode(p.read_bytes()).decode("utf-8")
    _log("Vision", f"Bild geladen: {p.name} ({p.stat().st_size / 1024:.1f} KB | {mime})")
    return data, mime

def _bild_nachricht(bild_data: str, mime: str, prompt: str) -> list[dict]:
    """Erstellt die messages-Liste mit Bild-Block für die Claude API."""
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime,
                        "data": bild_data,
                    },
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]

def _api_aufruf(messages: list[dict], system: str = "") -> str:
    """Führt einen Claude API-Aufruf aus und gibt den Text-Response zurück."""
    key = _pruefe_api_key()
    client = anthropic.Anthropic(api_key=key)

    kwargs = {
        "model": MODELL,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text


# =============================================================================
# MODUS 1: BESCHREIBEN — Allgemeine kontextuelle Bildbeschreibung
# Nutzt denselben Reasoning-Apparat wie Textverarbeitung.
# =============================================================================

PROMPT_BESCHREIBEN = """Analysiere dieses Bild präzise und kontextuell.

Struktur deiner Antwort:
## Überblick
Ein Satz: Was zeigt das Bild?

## Detailanalyse
- Hauptelemente und ihre räumliche Anordnung
- Relevante Text- und Zahlenwerte (falls vorhanden)
- Visuelle Hierarchie und Beziehungen zwischen Elementen

## Geschäftlicher Kontext
Was ist die strategische oder operative Bedeutung dieses Bildes?
Welche Entscheidungen oder Aktionen legt es nahe?

## Einschränkungen
Was kann nicht sicher erkannt werden (Qualität, Auflösung, Mehrdeutigkeiten)?"""

def modus_beschreiben(pfad: str) -> str:
    _log("Beschreiben", f"Analysiere: {pfad}")
    bild, mime = _lade_bild(pfad)
    nachrichten = _bild_nachricht(bild, mime, PROMPT_BESCHREIBEN)
    ergebnis = _api_aufruf(nachrichten)
    print(ergebnis)
    return ergebnis


# =============================================================================
# MODUS 2: RECHNUNG — Strukturierte Rechnungsextraktion → JSON
# Schema entspricht dem Standard aus SKILL.md.
# =============================================================================

SYSTEM_RECHNUNG = (
    "Du bist ein präziser Datenextraktions-Assistent für Buchhaltungsdokumente. "
    "Antworte ausschließlich mit validem JSON, kein Markdown, keine Erklärungen. "
    "Fehlende Felder mit null befüllen. Geldbeträge als Dezimalzahl (float)."
)

PROMPT_RECHNUNG = """Extrahiere alle relevanten Informationen aus diesem Dokument
und gib sie als JSON-Objekt mit exakt diesem Schema zurück:

{
  "dokument_typ": "rechnung | quittung | lieferschein | gutschrift | unbekannt",
  "rechnungsnummer": null,
  "datum": null,
  "faellig_am": null,
  "lieferant": {
    "name": null,
    "adresse": null,
    "telefon": null,
    "email": null,
    "ust_id": null,
    "steuernummer": null,
    "iban": null
  },
  "empfaenger": {
    "name": null,
    "adresse": null,
    "kundennummer": null
  },
  "positionen": [
    {
      "pos": 1,
      "beschreibung": null,
      "menge": null,
      "einheit": null,
      "einzelpreis": null,
      "gesamtpreis": null,
      "mwst_satz": null
    }
  ],
  "zwischensumme_netto": null,
  "mwst_betrag": null,
  "gesamtbetrag_brutto": null,
  "waehrung": "EUR",
  "zahlungsbedingungen": null,
  "bestellreferenz": null,
  "konfidenz": 0.0,
  "anmerkungen": null
}

Datum-Format: YYYY-MM-DD. konfidenz: 0.0–1.0 (wie sicher bist du in der Extraktion)."""

def modus_rechnung(pfad: str, ausgabe_format: str = "json") -> dict:
    _log("Rechnung", f"Extrahiere: {pfad}")
    bild, mime = _lade_bild(pfad)
    nachrichten = _bild_nachricht(bild, mime, PROMPT_RECHNUNG)
    raw = _api_aufruf(nachrichten, system=SYSTEM_RECHNUNG)

    # JSON bereinigen (Modell könnte Markdown-Fences zurückgeben)
    raw_clean = raw.strip()
    if raw_clean.startswith("```"):
        zeilen = raw_clean.split("\n")
        raw_clean = "\n".join(zeilen[1:-1] if zeilen[-1] == "```" else zeilen[1:])

    try:
        daten = json.loads(raw_clean)
    except json.JSONDecodeError as e:
        _warn(f"JSON-Parse-Fehler: {e} — Rohtext wird ausgegeben")
        daten = {"fehler": str(e), "rohtext": raw_clean}

    # Konfidenz-Warnung
    konfidenz = daten.get("konfidenz", 0)
    if isinstance(konfidenz, (int, float)) and konfidenz < KONFIDENZ_SCHWELLE:
        _warn(
            f"Niedrige Konfidenz: {konfidenz:.0%} < {KONFIDENZ_SCHWELLE:.0%}. "
            "Manuelle Prüfung empfohlen."
        )
    else:
        _ok(f"Extraktion abgeschlossen | Konfidenz: {konfidenz:.0%}")

    if ausgabe_format == "markdown":
        _ausgabe_rechnung_markdown(daten)
    else:
        print(json.dumps(daten, indent=2, ensure_ascii=False))

    return daten

def _ausgabe_rechnung_markdown(d: dict) -> None:
    lf = d.get("lieferant", {}) or {}
    emp = d.get("empfaenger", {}) or {}
    pos_liste = d.get("positionen", []) or []

    print(f"# {d.get('dokument_typ', 'Dokument').title()}: {d.get('rechnungsnummer', 'N/A')}")
    print(f"**Datum:** {d.get('datum', 'N/A')} | **Fällig:** {d.get('faellig_am', 'N/A')}\n")
    print(f"**Lieferant:** {lf.get('name', 'N/A')} | USt-ID: {lf.get('ust_id', 'N/A')}")
    print(f"**Empfänger:** {emp.get('name', 'N/A')}\n")
    print("## Positionen\n")
    print("| Pos | Beschreibung | Menge | Einzelpreis | Gesamt | MwSt |")
    print("|---|---|---|---|---|---|")
    for p in pos_liste:
        print(f"| {p.get('pos','')} | {p.get('beschreibung','')} | "
              f"{p.get('menge','')} {p.get('einheit','')} | "
              f"{p.get('einzelpreis','')} | {p.get('gesamtpreis','')} | "
              f"{p.get('mwst_satz','')} |")
    print(f"\n**Netto:** {d.get('zwischensumme_netto','N/A')} {d.get('waehrung','EUR')}")
    print(f"**MwSt:** {d.get('mwst_betrag','N/A')} | **Brutto:** {d.get('gesamtbetrag_brutto','N/A')} {d.get('waehrung','EUR')}")
    if d.get("anmerkungen"):
        print(f"\n> {d['anmerkungen']}")


# =============================================================================
# MODUS 3: DIAGRAMM — Kontextuelle Chart-Analyse → JSON + Interpretation
# Liest Achsenbeschriftungen, korreliert Datenpunkte, interpretiert Trend.
# =============================================================================

SYSTEM_DIAGRAMM = (
    "Du bist ein Datenanalyse-Experte. Extrahiere alle Datenpunkte aus dem Diagramm "
    "und interpretiere die strategische Bedeutung. Antworte mit validem JSON."
)

PROMPT_DIAGRAMM = """Analysiere dieses Diagramm vollständig und gib ein JSON-Objekt zurück:

{
  "diagramm_typ": "balken | linie | kreis | streuung | fläche | heatmap | tabelle | kombiniert | unbekannt",
  "titel": null,
  "quelle": null,
  "zeitraum": null,
  "x_achse": { "bezeichnung": null, "einheit": null, "wertebereich": null },
  "y_achse": { "bezeichnung": null, "einheit": null, "wertebereich": null },
  "legende": [],
  "datenpunkte": [
    { "reihe": null, "label": null, "wert": null, "einheit": null }
  ],
  "hoechstwert": { "label": null, "wert": null, "reihe": null },
  "tiefstwert": { "label": null, "wert": null, "reihe": null },
  "trend": "stark_steigend | steigend | stabil | fallend | stark_fallend | gemischt | zyklisch",
  "veraenderung_gesamt": null,
  "interpretation": "Kontextuelle Analyse in 3-4 Sätzen: Was bedeuten die Daten?",
  "handlungsempfehlung": "Welche Maßnahmen legt das Diagramm nahe?",
  "auffaelligkeiten": [],
  "konfidenz": 0.0,
  "anmerkungen": null
}

Alle numerischen Werte als Zahl (float/int), keine Strings."""

def modus_diagramm(pfad: str, ausgabe_format: str = "json") -> dict:
    _log("Diagramm", f"Analysiere: {pfad}")
    bild, mime = _lade_bild(pfad)
    nachrichten = _bild_nachricht(bild, mime, PROMPT_DIAGRAMM)
    raw = _api_aufruf(nachrichten, system=SYSTEM_DIAGRAMM)

    raw_clean = raw.strip()
    if raw_clean.startswith("```"):
        zeilen = raw_clean.split("\n")
        raw_clean = "\n".join(zeilen[1:-1] if zeilen[-1] == "```" else zeilen[1:])

    try:
        daten = json.loads(raw_clean)
    except json.JSONDecodeError as e:
        _warn(f"JSON-Parse-Fehler: {e}")
        daten = {"fehler": str(e), "rohtext": raw_clean}

    konfidenz = daten.get("konfidenz", 0)
    _ok(f"Diagramm-Analyse | Typ: {daten.get('diagramm_typ','?')} | Trend: {daten.get('trend','?')} | Konfidenz: {konfidenz:.0%}")

    if ausgabe_format == "markdown":
        _ausgabe_diagramm_markdown(daten)
    else:
        print(json.dumps(daten, indent=2, ensure_ascii=False))

    return daten

def _ausgabe_diagramm_markdown(d: dict) -> None:
    print(f"# Diagramm-Analyse: {d.get('titel', 'Unbekanntes Diagramm')}")
    print(f"**Typ:** {d.get('diagramm_typ','N/A')} | **Trend:** {d.get('trend','N/A')}\n")
    if d.get("x_achse"):
        x = d["x_achse"]
        print(f"**X-Achse:** {x.get('bezeichnung','N/A')} [{x.get('einheit','N/A')}]")
    if d.get("y_achse"):
        y = d["y_achse"]
        print(f"**Y-Achse:** {y.get('bezeichnung','N/A')} [{y.get('einheit','N/A')}]\n")
    dp = d.get("datenpunkte", [])
    if dp:
        print("## Datenpunkte\n| Reihe | Label | Wert |")
        print("|---|---|---|")
        for p in dp[:20]:
            print(f"| {p.get('reihe','')} | {p.get('label','')} | {p.get('wert','')} {p.get('einheit','')} |")
    print(f"\n## Interpretation\n{d.get('interpretation','N/A')}")
    print(f"\n## Handlungsempfehlung\n{d.get('handlungsempfehlung','N/A')}")
    if d.get("auffaelligkeiten"):
        print("\n## Auffälligkeiten")
        for a in d["auffaelligkeiten"]:
            print(f"- {a}")


# =============================================================================
# MODUS 4: SCREENSHOT — UI/Fehleranalyse → strukturiertes Markdown
# Identifiziert Benutzeroberflächen, Fehlermeldungen, Status-Informationen.
# =============================================================================

PROMPT_SCREENSHOT = """Analysiere diesen UI-Screenshot oder System-Screenshot präzise.

## Identifikation
- Welche Anwendung / welches System ist zu sehen?
- Welcher Bildschirmbereich / welches Fenster ist aktiv?

## Sichtbare Informationen
- Alle lesbaren Textelemente (Titel, Labels, Werte, Fehlermeldungen)
- Status-Indikatoren (Farben, Icons, Progress-Bars)
- Formularfelder und deren Inhalte (falls sichtbar)
- Buttons, Menüs und Navigation

## Fehlerzustand (falls vorhanden)
- Exakter Fehlertext (wörtlich zitieren)
- Fehlercode oder Exception-Typ
- Betroffene Komponente oder Funktion
- Stack-Trace (falls sichtbar)

## Systemkontext
- Betriebssystem / Browser / Framework (aus UI-Elementen ableiten)
- Versionsinformationen (falls sichtbar)

## Diagnose und nächste Schritte
- Wahrscheinliche Ursache des Problems / des Zustands
- Empfohlene Maßnahmen in Prioritätsreihenfolge"""

def modus_screenshot(pfad: str) -> str:
    _log("Screenshot", f"Analysiere: {pfad}")
    bild, mime = _lade_bild(pfad)
    nachrichten = _bild_nachricht(bild, mime, PROMPT_SCREENSHOT)
    ergebnis = _api_aufruf(nachrichten)
    _ok("Screenshot-Analyse abgeschlossen")
    print(ergebnis)
    return ergebnis


# =============================================================================
# MODUS 5: BATCH — Verzeichnis mit Bildern sequenziell verarbeiten
# Output: JSON-Lines (1 Datensatz pro Zeile → Pipe-kompatibel mit ETL-Pipeline)
# =============================================================================

def modus_batch(verzeichnis: str, analyse_modus: str, ausgabe_datei: str | None = None) -> None:
    """
    Verarbeitet alle Bilder in einem Verzeichnis mit dem gewählten Modus.
    Output: JSON-Lines nach stdout (oder Datei).
    Ein Fehlschlag eines Bildes bricht den Batch nicht ab.

    Pipe-Beispiel:
        python vision_dokument.py batch ./rechnungen/ rechnung | weitere-verarbeitung
    """
    ERLAUBTE_MODI = {"rechnung", "diagramm", "beschreiben", "screenshot"}
    if analyse_modus not in ERLAUBTE_MODI:
        _err(f"Batch-Modus '{analyse_modus}' ungültig. Erlaubt: {ERLAUBTE_MODI}")

    basis = Path(verzeichnis)
    if not basis.is_dir():
        _err(f"Kein Verzeichnis: {verzeichnis}")

    bilder = sorted([p for p in basis.iterdir() if p.suffix.lower() in BILD_ENDUNGEN])
    if not bilder:
        _err(f"Keine Bilder in: {verzeichnis}")

    _log("Batch", f"Starte | {len(bilder)} Bilder | Modus: {analyse_modus}")

    ausgabe = open(ausgabe_datei, "w", encoding="utf-8") if ausgabe_datei else sys.stdout
    ok_count = fehler_count = 0

    try:
        for i, bild_pfad in enumerate(bilder, 1):
            _log("Batch", f"[{i}/{len(bilder)}] {bild_pfad.name}")
            try:
                ergebnis: dict | str

                if analyse_modus == "rechnung":
                    bild, mime = _lade_bild(str(bild_pfad))
                    nachrichten = _bild_nachricht(bild, mime, PROMPT_RECHNUNG)
                    raw = _api_aufruf(nachrichten, system=SYSTEM_RECHNUNG)
                    raw_clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```")
                    try:
                        ergebnis = json.loads(raw_clean)
                    except json.JSONDecodeError:
                        ergebnis = {"rohtext": raw_clean}

                elif analyse_modus == "diagramm":
                    bild, mime = _lade_bild(str(bild_pfad))
                    nachrichten = _bild_nachricht(bild, mime, PROMPT_DIAGRAMM)
                    raw = _api_aufruf(nachrichten, system=SYSTEM_DIAGRAMM)
                    raw_clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```")
                    try:
                        ergebnis = json.loads(raw_clean)
                    except json.JSONDecodeError:
                        ergebnis = {"rohtext": raw_clean}

                elif analyse_modus in ("beschreiben", "screenshot"):
                    prompt = PROMPT_BESCHREIBEN if analyse_modus == "beschreiben" else PROMPT_SCREENSHOT
                    bild, mime = _lade_bild(str(bild_pfad))
                    nachrichten = _bild_nachricht(bild, mime, prompt)
                    text = _api_aufruf(nachrichten)
                    ergebnis = {"text": text}
                else:
                    ergebnis = {}

                # Metadaten anhängen
                if isinstance(ergebnis, dict):
                    ergebnis["_meta"] = {
                        "datei": bild_pfad.name,
                        "pfad": str(bild_pfad.resolve()),
                        "modus": analyse_modus,
                        "verarbeitet_am": _ts(),
                        "batch_index": i,
                    }

                zeile = json.dumps(ergebnis, ensure_ascii=False)
                print(zeile, file=ausgabe, flush=True)
                ok_count += 1

            except Exception as exc:
                fehler_count += 1
                fehler_eintrag = {
                    "fehler": str(exc),
                    "_meta": {
                        "datei": bild_pfad.name,
                        "modus": analyse_modus,
                        "verarbeitet_am": _ts(),
                        "batch_index": i,
                    }
                }
                print(json.dumps(fehler_eintrag, ensure_ascii=False), file=ausgabe, flush=True)
                _warn(f"Fehler bei {bild_pfad.name}: {exc}")

    finally:
        if ausgabe_datei and ausgabe is not sys.stdout:
            ausgabe.close()

    # Abschluss-Statistik (immer nach stderr — nicht in JSON-Lines-Stream)
    print(
        json.dumps({"ok": ok_count, "fehler": fehler_count, "gesamt": len(bilder)}),
        file=sys.stderr
    )
    _ok(f"Batch abgeschlossen: {ok_count} OK | {fehler_count} Fehler | {len(bilder)} gesamt")


# =============================================================================
# CLI
# =============================================================================

HILFE = """
VERWENDUNG:
  python vision_dokument.py beschreiben  <bild>
  python vision_dokument.py rechnung     <bild> [--format json|markdown]
  python vision_dokument.py diagramm     <bild> [--format json|markdown]
  python vision_dokument.py screenshot   <bild>
  python vision_dokument.py batch        <verzeichnis/> <modus> [--ausgabe datei.jsonl]

MODI:
  beschreiben   Kontextuelle Bildbeschreibung → Markdown
  rechnung      Rechnungs-/Quittungsextraktion → JSON (Standard-Schema aus SKILL.md)
  diagramm      Chart-Analyse mit Datenpunkten, Trend und Interpretation → JSON
  screenshot    UI/Fehlermeldungsanalyse → strukturiertes Markdown
  batch         Alle Bilder in Verzeichnis sequenziell → JSON-Lines (stdout)

BATCH-MODI (Argument 2):
  rechnung | diagramm | beschreiben | screenshot

OPTIONEN:
  --format json|markdown   Ausgabeformat (Standard: json)
  --ausgabe datei.jsonl    Batch-Ausgabe in Datei statt stdout

VORAUSSETZUNG:
  export ANTHROPIC_API_KEY=sk-ant-...
  pip install anthropic

MODELL: claude-sonnet-4-6

PIPELINE-BEISPIEL:
  # Rechnungen batch → ETL → CSV
  python vision_dokument.py batch ./rechnungen/ rechnung \\
    | python csv_etl_pipeline.py pipeline - ausgabe.csv

KONFIDENZ-SCHWELLE: {schwelle:.0%} (Warnung bei Unterschreitung → manuelle Prüfung)
""".format(schwelle=KONFIDENZ_SCHWELLE)

if __name__ == "__main__":
    if not HAS_ANTHROPIC:
        print(
            "ERR | anthropic nicht installiert.\n"
            "    Ausführen: pip install anthropic",
            file=sys.stderr
        )
        sys.exit(1)

    if len(sys.argv) < 2:
        print(HILFE)
        sys.exit(0)

    modus = sys.argv[1]
    args = sys.argv[2:]

    def _get_opt(opt: str, default: str | None = None) -> str | None:
        for i, a in enumerate(args):
            if a == opt and i + 1 < len(args):
                return args[i + 1]
        return default

    args_positional = [a for a in args if not a.startswith("--")]
    fmt = _get_opt("--format", "json")

    if modus == "beschreiben":
        if not args_positional:
            _err("VERWENDUNG: beschreiben <bild>")
        modus_beschreiben(args_positional[0])

    elif modus == "rechnung":
        if not args_positional:
            _err("VERWENDUNG: rechnung <bild> [--format json|markdown]")
        modus_rechnung(args_positional[0], ausgabe_format=fmt)

    elif modus == "diagramm":
        if not args_positional:
            _err("VERWENDUNG: diagramm <bild> [--format json|markdown]")
        modus_diagramm(args_positional[0], ausgabe_format=fmt)

    elif modus == "screenshot":
        if not args_positional:
            _err("VERWENDUNG: screenshot <bild>")
        modus_screenshot(args_positional[0])

    elif modus == "batch":
        if len(args_positional) < 2:
            _err("VERWENDUNG: batch <verzeichnis/> <modus> [--ausgabe datei.jsonl]")
        ausgabe_datei = _get_opt("--ausgabe")
        modus_batch(args_positional[0], args_positional[1], ausgabe_datei)

    else:
        print(f"ERR | Unbekannter Modus '{modus}'\n{HILFE}", file=sys.stderr)
        sys.exit(1)
