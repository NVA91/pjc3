#!/usr/bin/env python3
# LADESTUFE 3 — RESSOURCE | KATEGORIE: Visualisierung
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: Deklarativen Diagramm-Code aus Text, CSV oder Meeting-Notizen
#               generieren. Unterstützt Mermaid.js, PlantUML, D2, Graphviz DOT.
#               Optional: lokales Rendering zu SVG oder PNG.
# VERWENDUNG:
#   python diagramm_generator.py flowchart    "<beschreibung>"  [--tool mermaid|plantuml|d2]
#   python diagramm_generator.py gantt        "<beschreibung>"  [--csv daten.csv]
#   python diagramm_generator.py sequenz      "<beschreibung>"  [--tool mermaid|plantuml]
#   python diagramm_generator.py c4           "<beschreibung>"  [--ebene context|container|component]
#   python diagramm_generator.py erd          "<beschreibung>"  [--tool mermaid|plantuml]
#   python diagramm_generator.py sankey       "<beschreibung>"  [--csv daten.csv]
#   python diagramm_generator.py render       <code-datei.mmd|puml|d2|dot> [--format svg|png]
# VORAUSSETZUNG:
#   export ANTHROPIC_API_KEY=sk-ant-...
#   pip install anthropic
# OPTIONAL (für Rendering):
#   npm install -g @mermaid-js/mermaid-cli    → mmdc  (Mermaid → SVG/PNG)
#   apt install plantuml                       → plantuml
#   curl -fsSL https://d2lang.com/install.sh | sh → d2
#   apt install graphviz                       → dot
# MODELL: claude-sonnet-4-6

from __future__ import annotations

import sys
import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

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

# Rendering-Tool → Dateiendung → Render-Funktion
RENDER_ENDUNGEN = {
    ".mmd":  ("mermaid", "mmdc"),
    ".puml": ("plantuml", "plantuml"),
    ".d2":   ("d2", "d2"),
    ".dot":  ("graphviz", "dot"),
    ".gv":   ("graphviz", "dot"),
}


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
            "ANTHROPIC_API_KEY nicht gesetzt.\n"
            "    Ausführen: export ANTHROPIC_API_KEY=sk-ant-..."
        )
    return key

def _csv_lesen(pfad: str) -> str:
    """Liest CSV als einfachen Text für Kontextualisierung."""
    p = Path(pfad)
    if not p.exists():
        _err(f"CSV-Datei nicht gefunden: {pfad}")
    inhalt = p.read_text(encoding="utf-8", errors="replace")
    # Auf max. 3000 Zeichen begrenzen (Token-Effizienz)
    if len(inhalt) > 3000:
        _warn(f"CSV gekürzt auf 3000 Zeichen (original: {len(inhalt)} Zeichen)")
        inhalt = inhalt[:3000] + "\n... [gekürzt]"
    return inhalt

def _claude(prompt: str, system: str) -> str:
    """Führt einen Claude API-Aufruf aus und gibt den Text-Response zurück."""
    key = _pruefe_api_key()
    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model=MODELL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

def _code_bereinigen(raw: str, sprache: str) -> str:
    """Entfernt Markdown-Code-Fences aus der API-Antwort."""
    text = raw.strip()
    for fence in [f"```{sprache}", "```mermaid", "```plantuml", "```d2",
                  "```dot", "```graphviz", "```"]:
        if text.startswith(fence):
            text = text[len(fence):]
            break
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def _rendern_versuchen(code: str, endung: str, ausgabe_pfad: str | None, fmt: str = "svg") -> bool:
    """
    Versucht, Diagramm-Code mit lokalem Tool zu rendern.
    Gibt True zurück wenn erfolgreich, False wenn Tool nicht installiert.
    """
    if endung not in RENDER_ENDUNGEN:
        return False
    _, tool_cmd = RENDER_ENDUNGEN[endung]
    if not shutil.which(tool_cmd):
        _warn(f"Render-Tool '{tool_cmd}' nicht installiert — nur Code-Output.")
        return False

    tmp = Path(f"/tmp/diagramm_{datetime.now().strftime('%H%M%S')}{endung}")
    tmp.write_text(code, encoding="utf-8")

    if ausgabe_pfad is None:
        ausgabe_pfad = str(tmp.with_suffix(f".{fmt}"))

    if tool_cmd == "mmdc":
        cmd = ["mmdc", "-i", str(tmp), "-o", ausgabe_pfad, "-f", fmt.upper()]
    elif tool_cmd == "plantuml":
        flag = "-tsvg" if fmt == "svg" else "-tpng"
        cmd = ["plantuml", flag, "-o", str(Path(ausgabe_pfad).parent), str(tmp)]
    elif tool_cmd == "d2":
        cmd = ["d2", str(tmp), ausgabe_pfad]
    elif tool_cmd == "dot":
        flag = f"-T{fmt}"
        cmd = ["dot", flag, "-o", ausgabe_pfad, str(tmp)]
    else:
        return False

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            _ok(f"Gerendert: {ausgabe_pfad}")
            return True
        else:
            _warn(f"Render-Fehler: {result.stderr[:200]}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        _warn(f"Render-Fehler: {e}")
        return False
    finally:
        tmp.unlink(missing_ok=True)


# =============================================================================
# SYSTEM-PROMPTS (Diagramm-spezifisch)
# =============================================================================

SYSTEM_BASIS = (
    "Du bist ein Experte für technische Diagramme und visuelle Kommunikation. "
    "Antworte AUSSCHLIESSLICH mit dem Diagramm-Code, kein erklärender Text, "
    "keine Markdown-Fences, kein Kommentar vor oder nach dem Code. "
    "Der Code muss syntaktisch korrekt und direkt ausführbar sein."
)

SYSTEM_MERMAID = SYSTEM_BASIS + (
    " Nutze ausschließlich valide Mermaid.js-Syntax (Version ≥ 10). "
    "Keine Sonderzeichen in Node-Labels ohne Anführungszeichen. "
    "Farbcodierung per classDef wo sinnvoll."
)

SYSTEM_PLANTUML = SYSTEM_BASIS + (
    " Nutze ausschließlich valide PlantUML-Syntax. "
    "Beginne immer mit @startuml und ende mit @enduml. "
    "Nutze !theme materia für professionelles Aussehen."
)

SYSTEM_D2 = SYSTEM_BASIS + (
    " Nutze ausschließlich valide D2-Syntax. "
    "Verwende Shape-Typen (rectangle, oval, cylinder) wo passend. "
    "Füge direction: right oder down ein."
)

SYSTEM_DOT = SYSTEM_BASIS + (
    " Nutze ausschließlich valide Graphviz DOT-Syntax. "
    "Beginne mit digraph G { oder graph G { je nach Richtung. "
    "Nutze rankdir, node [shape=...] und edge [label=...] für Lesbarkeit."
)


# =============================================================================
# MODUS 1: FLOWCHART — Prozessablauf / Entscheidungsbaum
# Input: Freitext, Meeting-Notizen, Prozessbeschreibung
# =============================================================================

def modus_flowchart(beschreibung: str, tool: str = "mermaid", csv_pfad: str | None = None,
                    render_fmt: str | None = None, ausgabe: str | None = None) -> str:
    """
    Generiert Flowchart-Code aus Prozessbeschreibung oder Meeting-Notizen.
    Entscheidungsknoten, Alternativrouten und Verantwortlichkeiten werden
    automatisch aus dem Text extrahiert.
    """
    _log("Flowchart", f"Tool: {tool} | Input: {beschreibung[:60]}...")

    kontext = ""
    if csv_pfad:
        kontext = f"\n\nZusätzliche Daten aus CSV:\n{_csv_lesen(csv_pfad)}"

    if tool == "mermaid":
        prompt = f"""Erstelle ein Mermaid.js Flowchart für folgenden Prozess.
Nutze TD (top-down) Layout. Entscheidungen als Rauten ({{{{...}}}}),
Aktionen als Rechtecke, Start/Ende als Stadien (([...])).
Farbcodierung: classDef gruen fill:#d1e7dd; classDef rot fill:#f8d7da; classDef blau fill:#cfe2ff;
Weise relevante Klassen zu (z.B. Fehler=rot, Erfolg=gruen, Prozess=blau).

Prozessbeschreibung:
{beschreibung}{kontext}"""
        system = SYSTEM_MERMAID
        endung = ".mmd"

    elif tool == "plantuml":
        prompt = f"""Erstelle ein PlantUML Activity-Diagramm für folgenden Prozess.
Nutze |Swimlanes| für verschiedene Verantwortlichkeiten falls erkennbar.
Entscheidungen als if/else, Aktionen als :Aktion;

Prozessbeschreibung:
{beschreibung}{kontext}"""
        system = SYSTEM_PLANTUML
        endung = ".puml"

    elif tool == "d2":
        prompt = f"""Erstelle ein D2-Diagramm für folgenden Prozess.
Nutze Pfeile (->) für Fluss, beschriftete Kanten für Bedingungen.
Gruppiere zusammengehörige Schritte in Containern.

Prozessbeschreibung:
{beschreibung}{kontext}"""
        system = SYSTEM_D2
        endung = ".d2"

    else:
        _err(f"Unbekanntes Tool: {tool} | Erlaubt: mermaid, plantuml, d2")

    raw = _claude(prompt, system)
    code = _code_bereinigen(raw, tool)
    print(code)

    if render_fmt:
        _rendern_versuchen(code, endung, ausgabe, render_fmt)

    return code


# =============================================================================
# MODUS 2: GANTT — Projektplan aus CSV oder Beschreibung
# =============================================================================

def modus_gantt(beschreibung: str, csv_pfad: str | None = None,
                render_fmt: str | None = None, ausgabe: str | None = None) -> str:
    """
    Generiert Mermaid Gantt-Diagramm aus Projektbeschreibung oder CSV-Daten.
    CSV-Spalten erwartet: task, start (YYYY-MM-DD), end (YYYY-MM-DD), [section, done]
    """
    _log("Gantt", f"CSV: {csv_pfad or 'keins'} | Beschreibung: {beschreibung[:60]}...")

    csv_kontext = ""
    if csv_pfad:
        csv_kontext = f"\n\nProjektdaten aus CSV:\n{_csv_lesen(csv_pfad)}"

    prompt = f"""Erstelle ein Mermaid.js Gantt-Diagramm.
Format:
  gantt
    title <Projekttitel>
    dateFormat YYYY-MM-DD
    section <Phase>
      <Aufgabe> : [done|active|crit], <id>, <start>, <dauer>d

Regeln:
- Nutze done für abgeschlossene Aufgaben
- Nutze crit für kritische Aufgaben (roter Balken)
- Nutze active für laufende Aufgaben
- Meilensteine als: milestone, nach <id>, <datum>, 0d
- Sections für Projektphasen (Planung, Umsetzung, Abschluss etc.)

Projektbeschreibung:
{beschreibung}{csv_kontext}"""

    raw = _claude(prompt, SYSTEM_MERMAID)
    code = _code_bereinigen(raw, "mermaid")
    print(code)

    if render_fmt:
        _rendern_versuchen(code, ".mmd", ausgabe, render_fmt)

    return code


# =============================================================================
# MODUS 3: SEQUENZ — API-Interaktionen / Protokoll-Abläufe
# =============================================================================

def modus_sequenz(beschreibung: str, tool: str = "mermaid",
                  render_fmt: str | None = None, ausgabe: str | None = None) -> str:
    """
    Generiert Sequenzdiagramm für API-Flows, Protokolle oder Systeminteraktionen.
    Aktivierungen, Schleifen und Alt-Bedingungen werden automatisch eingefügt.
    """
    _log("Sequenz", f"Tool: {tool} | Input: {beschreibung[:60]}...")

    if tool == "mermaid":
        prompt = f"""Erstelle ein Mermaid.js Sequenzdiagramm.
Nutze:
- participant <Name> as <Alias> für alle Akteure
- activate/deactivate für Verarbeitungszeiträume
- loop für wiederholende Prozesse
- alt/else für Bedingungen (Erfolg/Fehler-Pfade)
- Note right of <Akteur>: <Hinweis> für wichtige Anmerkungen
- ->> für asynchrone, -->> für Antwort-Nachrichten

Beschreibung:
{beschreibung}"""
        system = SYSTEM_MERMAID
        endung = ".mmd"

    elif tool == "plantuml":
        prompt = f"""Erstelle ein PlantUML Sequenzdiagramm.
Nutze:
- actor, participant, database, boundary, control, entity für Akteur-Typen
- activate/deactivate für Lebenslinien-Aktivierungen
- alt/else/end für Bedingungen
- loop für Schleifen
- note left/right of für Kommentare
- -> für synchron, ->> für asynchron, --> für Antworten

Beschreibung:
{beschreibung}"""
        system = SYSTEM_PLANTUML
        endung = ".puml"

    else:
        _err(f"Unbekanntes Tool: {tool} | Erlaubt: mermaid, plantuml")

    raw = _claude(prompt, system)
    code = _code_bereinigen(raw, tool)
    print(code)

    if render_fmt:
        _rendern_versuchen(code, endung, ausgabe, render_fmt)

    return code


# =============================================================================
# MODUS 4: C4 — Systemarchitektur (Context / Container / Component)
# =============================================================================

C4_EBENEN = {
    "context":   ("C4Context", "Zeigt das System im Kontext: externe Nutzer und Systeme"),
    "container": ("C4Container", "Zeigt Container (Apps, DBs, Services) und ihre Interaktionen"),
    "component": ("C4Component", "Zeigt Komponenten innerhalb eines Containers"),
}

def modus_c4(beschreibung: str, ebene: str = "context",
             render_fmt: str | None = None, ausgabe: str | None = None) -> str:
    """
    Generiert PlantUML C4-Modell (Context / Container / Component Level).
    Benötigt C4-PlantUML-Bibliothek (automatisch via !include eingebunden).
    """
    if ebene not in C4_EBENEN:
        _err(f"Unbekannte C4-Ebene: {ebene} | Erlaubt: {list(C4_EBENEN.keys())}")

    typ, erklaerung = C4_EBENEN[ebene]
    _log("C4", f"Ebene: {ebene} ({erklaerung}) | Input: {beschreibung[:60]}...")

    prompt = f"""Erstelle ein PlantUML C4-Modell auf Ebene: {ebene.upper()} ({erklaerung}).

Pflicht-Header:
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/{typ}.puml

Verfügbare Makros je nach Ebene:
Context:   Person(alias, label, descr), System(alias, label, descr), System_Ext(alias, label, descr), Rel(from, to, label, techn)
Container: Container(alias, label, techn, descr), ContainerDb(alias, label, techn, descr), Container_Ext(...)
Component: Component(alias, label, techn, descr), ComponentDb(...), ComponentQueue(...)

Füge LAYOUT_WITH_LEGEND() am Ende ein.

Systembeschreibung:
{beschreibung}"""

    raw = _claude(prompt, SYSTEM_PLANTUML)
    code = _code_bereinigen(raw, "plantuml")
    print(code)

    if render_fmt:
        _rendern_versuchen(code, ".puml", ausgabe, render_fmt)

    return code


# =============================================================================
# MODUS 5: ERD — Entity-Relationship-Diagramm
# =============================================================================

def modus_erd(beschreibung: str, tool: str = "mermaid",
              render_fmt: str | None = None, ausgabe: str | None = None) -> str:
    """
    Generiert ERD aus Datenbankschema-Beschreibung oder Entitätsliste.
    Zeigt Attribute, Datentypen und Kardinalitäten (1:1, 1:N, M:N).
    """
    _log("ERD", f"Tool: {tool} | Input: {beschreibung[:60]}...")

    if tool == "mermaid":
        prompt = f"""Erstelle ein Mermaid.js Entity-Relationship-Diagramm (erDiagram).
Format:
  ENTITY {{
    datatype ATTR_NAME PK/FK "Kommentar"
  }}
  ENTITY1 ||--o{{ ENTITY2 : "Beziehung"

Kardinalitäts-Notation:
  ||--|| (genau 1 zu genau 1)
  ||--o{{ (genau 1 zu null-oder-mehr)
  }}o--o{{ (null-oder-mehr zu null-oder-mehr)
  ||--|{{ (genau 1 zu ein-oder-mehr)

Datenbankbeschreibung / Entitäten:
{beschreibung}"""
        system = SYSTEM_MERMAID
        endung = ".mmd"

    elif tool == "plantuml":
        prompt = f"""Erstelle ein PlantUML Entity-Relationship-Diagramm.
Nutze !theme materia.
Entitäten als: entity "Name" as ALIAS {{ + PK/FK-Felder }}
Beziehungen als: ALIAS1 ||--o{{ ALIAS2 : label

Datenbankbeschreibung / Entitäten:
{beschreibung}"""
        system = SYSTEM_PLANTUML
        endung = ".puml"

    else:
        _err(f"Unbekanntes Tool: {tool} | Erlaubt: mermaid, plantuml")

    raw = _claude(prompt, system)
    code = _code_bereinigen(raw, tool)
    print(code)

    if render_fmt:
        _rendern_versuchen(code, endung, ausgabe, render_fmt)

    return code


# =============================================================================
# MODUS 6: SANKEY — Volumenverteilungen / Datenflüsse
# =============================================================================

def modus_sankey(beschreibung: str, csv_pfad: str | None = None,
                 render_fmt: str | None = None, ausgabe: str | None = None) -> str:
    """
    Generiert Sankey-Diagramm für Volumenflüsse und Ressourcenverteilungen.
    Mermaid sankey-beta oder D2 je nach Verfügbarkeit.
    CSV-Spalten erwartet: von, nach, wert
    """
    _log("Sankey", f"CSV: {csv_pfad or 'keins'} | Input: {beschreibung[:60]}...")

    csv_kontext = ""
    if csv_pfad:
        csv_kontext = f"\n\nFlussdaten aus CSV (von, nach, wert):\n{_csv_lesen(csv_pfad)}"

    # Mermaid sankey-beta (ab Version 10.3)
    prompt = f"""Erstelle ein Mermaid.js Sankey-Diagramm (sankey-beta).
Format:
  sankey-beta
  Quelle,Ziel,Wert
  A,B,100
  A,C,200
  B,D,80

Regeln:
- Nur Komma-separierte Tripel (von, nach, numerischer Wert)
- Werte repräsentieren Volumina/Mengen (nicht Prozent)
- Aggregiere kleine Flüsse zu "Sonstiges" wenn > 7 Zweige

Flussbeschreibung:
{beschreibung}{csv_kontext}"""

    raw = _claude(prompt, SYSTEM_MERMAID)
    code = _code_bereinigen(raw, "mermaid")
    print(code)

    if render_fmt:
        _rendern_versuchen(code, ".mmd", ausgabe, render_fmt)

    return code


# =============================================================================
# MODUS 7: RENDER — Bestehenden Code-File rendern
# =============================================================================

def modus_render(code_datei: str, fmt: str = "svg", ausgabe: str | None = None) -> None:
    """
    Rendert eine bestehende Diagramm-Code-Datei zu SVG oder PNG.
    Erkennt Tool automatisch anhand der Dateiendung.
    """
    p = Path(code_datei)
    if not p.exists():
        _err(f"Code-Datei nicht gefunden: {code_datei}")

    endung = p.suffix.lower()
    if endung not in RENDER_ENDUNGEN:
        _err(f"Unbekannte Dateiendung: {endung} | Unterstützt: {list(RENDER_ENDUNGEN.keys())}")

    _log("Render", f"Datei: {p.name} | Format: {fmt}")
    code = p.read_text(encoding="utf-8")

    if ausgabe is None:
        ausgabe = str(p.with_suffix(f".{fmt}"))

    erfolg = _rendern_versuchen(code, endung, ausgabe, fmt)
    if not erfolg:
        _log("Render", "Render nicht möglich — Code wurde zur manuellen Verarbeitung ausgegeben")
        print(code)


# =============================================================================
# TOOL-VERFÜGBARKEIT PRÜFEN
# =============================================================================

def _zeige_tool_status() -> None:
    tools = [
        ("mmdc",      "Mermaid CLI",  "npm install -g @mermaid-js/mermaid-cli"),
        ("plantuml",  "PlantUML",     "apt install plantuml"),
        ("d2",        "D2",           "curl -fsSL https://d2lang.com/install.sh | sh"),
        ("dot",       "Graphviz",     "apt install graphviz"),
    ]
    print("\n=== Render-Tools ===")
    for cmd, name, install in tools:
        status = "✓ installiert" if shutil.which(cmd) else f"✗ fehlt  →  {install}"
        print(f"  {name:<12} ({cmd:<10}) {status}")
    print()


# =============================================================================
# CLI
# =============================================================================

HILFE = """
VERWENDUNG:
  python diagramm_generator.py flowchart  "<beschreibung>" [--tool mermaid|plantuml|d2] [--render svg|png]
  python diagramm_generator.py gantt      "<beschreibung>" [--csv daten.csv] [--render svg|png]
  python diagramm_generator.py sequenz    "<beschreibung>" [--tool mermaid|plantuml] [--render svg|png]
  python diagramm_generator.py c4         "<beschreibung>" [--ebene context|container|component] [--render svg]
  python diagramm_generator.py erd        "<beschreibung>" [--tool mermaid|plantuml] [--render svg|png]
  python diagramm_generator.py sankey     "<beschreibung>" [--csv daten.csv] [--render svg|png]
  python diagramm_generator.py render     <datei.mmd|puml|d2|dot> [--format svg|png] [--ausgabe pfad]
  python diagramm_generator.py tools

OPTIONEN:
  --tool mermaid|plantuml|d2|graphviz   Diagramm-Sprache (Standard: mermaid)
  --ebene context|container|component   C4-Detailierungsebene (Standard: context)
  --csv daten.csv                       Zusätzliche Daten aus CSV-Datei
  --render svg|png                      Optional: lokal rendern wenn Tool installiert
  --ausgabe pfad.svg                    Ausgabe-Pfad für gerenderte Datei

MODI:
  flowchart   Prozessablauf, Entscheidungsbaum, Workflow aus Beschreibung/Notizen
  gantt       Projektplan mit Phasen und Meilensteine aus Beschreibung oder CSV
  sequenz     API-Interaktionen, Protokolle, System-Kommunikation
  c4          Systemarchitektur (Context / Container / Component Level)
  erd         Entity-Relationship-Diagramm aus Datenbankschema
  sankey      Volumenverteilungen, Ressourcen- und Datenflüsse
  render      Bestehenden Code-File zu SVG/PNG rendern
  tools       Zeigt Verfügbarkeit der lokalen Render-Tools

RENDER-TOOLS (optional):
  npm install -g @mermaid-js/mermaid-cli    → mmdc  (Mermaid)
  apt install plantuml                       → plantuml
  curl -fsSL https://d2lang.com/install.sh | sh → d2
  apt install graphviz                       → dot (Graphviz)

VORAUSSETZUNG:
  export ANTHROPIC_API_KEY=sk-ant-...
  pip install anthropic

MODELL: claude-sonnet-4-6
"""

if __name__ == "__main__":
    if not HAS_ANTHROPIC:
        print("ERR | anthropic nicht installiert.\nAusführen: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print(HILFE); sys.exit(0)

    modus = sys.argv[1]
    args = sys.argv[2:]

    def _opt(name: str, default: str | None = None) -> str | None:
        for i, a in enumerate(args):
            if a == name and i + 1 < len(args):
                return args[i + 1]
        return default

    def _pos(idx: int) -> str | None:
        positional = [a for a in args if not a.startswith("--")]
        return positional[idx] if idx < len(positional) else None

    render_fmt = _opt("--render")
    ausgabe    = _opt("--ausgabe")
    tool       = _opt("--tool", "mermaid")
    csv_pfad   = _opt("--csv")
    ebene      = _opt("--ebene", "context")
    fmt        = _opt("--format", "svg")

    if modus == "flowchart":
        beschr = _pos(0) or _err("VERWENDUNG: flowchart '<beschreibung>'")
        modus_flowchart(beschr, tool=tool, csv_pfad=csv_pfad, render_fmt=render_fmt, ausgabe=ausgabe)

    elif modus == "gantt":
        beschr = _pos(0) or _err("VERWENDUNG: gantt '<beschreibung>'")
        modus_gantt(beschr, csv_pfad=csv_pfad, render_fmt=render_fmt, ausgabe=ausgabe)

    elif modus == "sequenz":
        beschr = _pos(0) or _err("VERWENDUNG: sequenz '<beschreibung>'")
        modus_sequenz(beschr, tool=tool, render_fmt=render_fmt, ausgabe=ausgabe)

    elif modus == "c4":
        beschr = _pos(0) or _err("VERWENDUNG: c4 '<beschreibung>'")
        modus_c4(beschr, ebene=ebene, render_fmt=render_fmt, ausgabe=ausgabe)

    elif modus == "erd":
        beschr = _pos(0) or _err("VERWENDUNG: erd '<beschreibung>'")
        modus_erd(beschr, tool=tool, render_fmt=render_fmt, ausgabe=ausgabe)

    elif modus == "sankey":
        beschr = _pos(0) or _err("VERWENDUNG: sankey '<beschreibung>'")
        modus_sankey(beschr, csv_pfad=csv_pfad, render_fmt=render_fmt, ausgabe=ausgabe)

    elif modus == "render":
        datei = _pos(0) or _err("VERWENDUNG: render <datei.mmd|puml|d2|dot>")
        modus_render(datei, fmt=fmt, ausgabe=ausgabe)

    elif modus == "tools":
        _zeige_tool_status()

    else:
        print(f"ERR | Unbekannter Modus '{modus}'\n{HILFE}", file=sys.stderr)
        sys.exit(1)
