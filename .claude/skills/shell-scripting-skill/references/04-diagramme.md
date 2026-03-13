# Grafiken und Diagramme — Detailreferenz

## Tool-Auswahl nach Diagramm-Typ

| Diagramm-Typ | Empfohlenes Tool | Stärke | Wann verwenden |
|-------------|-----------------|--------|----------------|
| **Flowchart / Entscheidungsbaum** | Mermaid.js | Web-nativ, Markdown-einbettbar | Prozesse, Workflows, Decision Trees |
| **Sequenzdiagramm** | Mermaid.js / PlantUML | Präzise Lebenslinien, Aktivierungen | API-Interaktionen, Protokolle |
| **Gantt-Diagramm** | Mermaid.js | Einfache Syntax, CSV-kompatibel | Projektplanung, Meilensteine |
| **C4-Modell** | PlantUML (C4-Lib) | Strukturierte 4-Level-Architektur | System-/Container-/Komponenten-Sicht |
| **ERD (Entity-Relationship)** | Mermaid.js / PlantUML | Relationen, Kardinalitäten | Datenbankschema, Datenmodelle |
| **Sankey-Diagramm** | D2 / Graphviz | Volumenflüsse, Proportionen | Ressourcenverteilung, Datenflüsse |
| **Komplexe Graphen** | Graphviz DOT | Beliebige Knoten-/Kanten-Layouts | Abhängigkeits-Graphen, Netzwerke |

## Rendering-Pipeline

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

## Rendering-Voraussetzungen (optional, lokal)

| Tool | Install | Für |
|------|---------|-----|
| `mmdc` (Mermaid CLI) | `npm install -g @mermaid-js/mermaid-cli` | Mermaid → SVG/PNG |
| `plantuml` | `apt install plantuml` | PlantUML → SVG/PNG |
| `d2` | `curl -fsSL https://d2lang.com/install.sh \| sh` | D2 → SVG/PNG |
| `dot` (Graphviz) | `apt install graphviz` | DOT → SVG/PNG |

## Pflicht-Ablauf für jeden Diagram-Job

1. **Diagramm-Typ klären** — Flowchart / Gantt / Sequenz / C4 / ERD / Sankey?
2. **Input-Format prüfen** — Freitext, CSV oder strukturierte Beschreibung?
3. **Tool wählen** — Tool-Tabelle konsultieren; Standard: Mermaid (web-kompatibel)
4. **Code generieren** — `diagramm_generator.py` aufrufen; Code nach stdout
5. **Rendern** — Lokal (wenn Tool installiert) oder Code in Online-Editor zeigen
6. **Nutzer-Review** — Code und visuelle Vorschau zeigen, Anpassungen iterieren

## Online-Editoren (kein lokales Tool nötig)

- Mermaid: https://mermaid.live
- PlantUML: https://www.plantuml.com/plantuml/uml
- D2: https://play.d2lang.com
