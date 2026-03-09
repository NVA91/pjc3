---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: visualisierung-skill
description: >
  Deklarative Diagramme (Mermaid, PlantUML, D2, Graphviz): Flowcharts,
  Gantt, Sequenz, C4, ERD, Sankey — aus Text, CSV oder Meeting-Notizen.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Visualisierung
    description: >
      Deklarative Diagramme (Mermaid, PlantUML, D2, Graphviz): Flowcharts,
      Gantt, Sequenz, C4, ERD, Sankey — aus Text, CSV oder Meeting-Notizen

triggers:
  # Visualisierung / Diagramme
  - Flussdiagramm oder Prozessablauf als Mermaid/PlantUML generieren
  - Gantt-Diagramm aus CSV-Daten oder Projektplan erstellen
  - Sequenzdiagramm für API-Interaktionen oder Workflows zeichnen
  - C4-Modell für Systemarchitektur oder Komponenten erstellen
  - Entity-Relationship-Diagramm (ERD) aus Datenbankschema generieren
  - Sankey-Diagramm für Volumenverteilungen oder Datenflüsse erstellen
  - Diagramm-Code in SVG oder PNG rendern (mmdc, dot, d2, plantuml)
  - Meeting-Notizen oder Prozessbeschreibung in Flowchart überführen
  - D2 oder Graphviz DOT-Code für komplexe Graphen schreiben

resources:
  - resources/diagramm_generator.py
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

## Grafiken und Diagramme — Deklarative Visualisierung

Anstatt Pixel manuell zu verschieben, übersetzt der Agent abstrakte Beschreibungen,
Meeting-Notizen oder CSV-Datenströme in exakten, maschinenlesbaren Diagramm-Code.
Rendering-Engines (mmdc, dot, d2, plantuml) erzeugen daraus SVG oder PNG.

### Tool-Auswahl nach Diagramm-Typ

| Diagramm-Typ | Empfohlenes Tool | Stärke | Wann verwenden |
|---|---|---|---|
| **Flowchart / Entscheidungsbaum** | Mermaid.js | Web-nativ, Markdown-einbettbar | Prozesse, Workflows, Decision Trees |
| **Sequenzdiagramm** | Mermaid.js / PlantUML | Präzise Lebenslinien, Aktivierungen | API-Interaktionen, Protokolle |
| **Gantt-Diagramm** | Mermaid.js | Einfache Syntax, CSV-kompatibel | Projektplanung, Meilensteine |
| **C4-Modell** | PlantUML (C4-Lib) | Strukturierte 4-Level-Architektur | System-/Container-/Komponenten-Sicht |
| **ERD (Entity-Relationship)** | Mermaid.js / PlantUML | Relationen, Kardinalitäten | Datenbankschema, Datenmodelle |
| **Sankey-Diagramm** | D2 / Graphviz | Volumenflüsse, Proportionen | Ressourcenverteilung, Datenflüsse |
| **Komplexe Graphen** | Graphviz DOT | Beliebige Knoten-/Kanten-Layouts | Abhängigkeits-Graphen, Netzwerke |

### Rendering-Pipeline

```
Beschreibung / CSV / Meeting-Notizen
    ↓
diagramm_generator.py <typ> (Claude API generiert Code)
    ↓
Diagramm-Code (Mermaid / PlantUML / D2 / DOT) → stdout
    ↓  (optional, wenn lokale Tools installiert)
Rendering: mmdc | plantuml | d2 | dot
    ↓
SVG / PNG-Datei
```

### Rendering-Voraussetzungen (optional, lokal)

| Tool | Install | Für |
|---|---|---|
| `mmdc` (Mermaid CLI) | `npm install -g @mermaid-js/mermaid-cli` | Mermaid → SVG/PNG |
| `plantuml` | `apt install plantuml` | PlantUML → SVG/PNG |
| `d2` | `curl -fsSL https://d2lang.com/install.sh \| sh` | D2 → SVG/PNG |
| `dot` (Graphviz) | `apt install graphviz` | DOT → SVG/PNG |

### Pflicht-Ablauf für jeden Diagram-Job

1. **Diagramm-Typ klären** — Flowchart / Gantt / Sequenz / C4 / ERD / Sankey?
2. **Input-Format prüfen** — Freitext, CSV oder strukturierte Beschreibung?
3. **Tool wählen** — Tool-Tabelle konsultieren; Standard: Mermaid (web-kompatibel)
4. **Code generieren** — `diagramm_generator.py` aufrufen; Code nach stdout
5. **Rendern** — Lokal (wenn Tool installiert) oder Code in Online-Editor zeigen
6. **Nutzer-Review** — Code und visuelle Vorschau zeigen, Anpassungen iterieren

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
| `resources/diagramm_generator.py` | 3 | Visualisierung | Mermaid/PlantUML/D2/Graphviz-Code generieren + optional rendern (SVG/PNG) |
