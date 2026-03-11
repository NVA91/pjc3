# Pre-Flight Router (Master)

## Zweck
Dieser Router ist der erste Pflichtschritt bei jeder neuen Nutzeraufgabe.
Er klassifiziert den Intent, prüft Kontext und definiert den minimalen Ausführungsplan.

## Pflichtablauf (immer, in Reihenfolge)
1. Aufgabe in 1 Satz zusammenfassen (intern).
2. Intent bestimmen.
3. Sicherheits-/Scope-Check durchführen.
4. Nur falls strategisch/architektonisch/zukunftsbezogen: zuerst `NOVA_ROADMAP.md` lesen.
5. Erst danach mit Umsetzung starten.

## Intent-Schema
Nutze genau eines dieser Labels:
- `[Intent: write_code]`
- `[Intent: debug]`
- `[Intent: review]`
- `[Intent: architecture]`
- `[Intent: docs]`
- `[Intent: explain]`
- `[Intent: ops]`

## Ausgabeformat (erste sichtbare Zeile)
Die erste sichtbare Zeile der Antwort MUSS immer ein Intent-Label sein.
Beispiel:
`[Intent: write_code]`

## Entscheidungsregel Roadmap
Wenn der Intent `architecture` ist ODER die Anfrage strategische Langzeitwirkung hat,
muss vor allen Vorschlägen die Datei `NOVA_ROADMAP.md` als primäre Quelle berücksichtigt werden.

## Guardrails
- Kein Start von Dateiänderungen ohne klaren Intent.
- Keine scope-fremden Erweiterungen.
- Bei Ambiguität maximal 1–3 präzise Rückfragen.
- Bei klaren Anforderungen direkt umsetzen.
