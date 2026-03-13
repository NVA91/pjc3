# Vision: Bildbeschreibung und Dokumentenanalyse — Detailreferenz

## Anwendungsfälle und Ausgabeformate

| Anwendungsfall | Input | Ausgabeformat | Ressource |
|---------------|-------|---------------|-----------|
| **Allgemeine Bildbeschreibung** | Beliebiges Bild (PNG/JPG/WebP) | Markdown-Prose | `vision_dokument.py beschreiben` |
| **Rechnungs-/Quittungsextraktion** | Scan, Foto, PDF-Screenshot | JSON (strukturiert) | `vision_dokument.py rechnung` |
| **Diagramm-Analyse** | Chart-Screenshot (Balken/Linie/Kreis) | JSON + Interpretation | `vision_dokument.py diagramm` |
| **UI-Screenshot / Fehleranalyse** | Browser/App-Screenshot | Markdown strukturiert | `vision_dokument.py screenshot` |
| **Batch-Verarbeitung** | Verzeichnis mit Bildern | JSON-Lines (1 Datei = 1 Zeile) | `vision_dokument.py batch` |

## Architektur-Prinzip

```
Bild-Input (lokal / URL)
    ↓
Claude Vision API (claude-sonnet-4-6, base64 oder URL)
    ↓  kontextuelle Interpretation (kein simple OCR)
Strukturierter Output (JSON / Markdown)
    ↓
Downstream: ETL-Pipeline | Excel-Modell | Datenbank-Skill | Report
```

## Rechnungsextraktion — JSON-Schema (Standard)

```json
{
  "dokument_typ": "rechnung | quittung | lieferschein | unbekannt",
  "rechnungsnummer": "...",
  "datum": "YYYY-MM-DD",
  "faellig_am": "YYYY-MM-DD | null",
  "lieferant": { "name": "...", "adresse": "...", "ust_id": "..." },
  "empfaenger": { "name": "...", "adresse": "..." },
  "positionen": [
    { "beschreibung": "...", "menge": 0, "einheit": "...",
      "einzelpreis": 0.0, "gesamtpreis": 0.0, "mwst_satz": 0.19 }
  ],
  "zwischensumme": 0.0,
  "mwst_betrag": 0.0,
  "gesamtbetrag": 0.0,
  "waehrung": "EUR",
  "konfidenz": 0.0,
  "anmerkungen": "..."
}
```

## Diagramm-Analyse — Ausgabestruktur

```json
{
  "diagramm_typ": "balken | linie | kreis | streuung | tabelle | unbekannt",
  "titel": "...",
  "x_achse": { "bezeichnung": "...", "einheit": "..." },
  "y_achse": { "bezeichnung": "...", "einheit": "..." },
  "datenpunkte": [{ "label": "...", "wert": 0.0 }],
  "trend": "steigend | fallend | stabil | gemischt",
  "interpretation": "Kontextuelle Bedeutung in 2-3 Sätzen",
  "handlungsempfehlung": "..."
}
```

## Pflicht-Ablauf für jeden Vision-Job

1. **Bildpfad bestätigen** — Pfad dem Nutzer anzeigen; kein autonomes Scannen ohne Freigabe.
2. **Modus wählen** — `rechnung` / `diagramm` / `screenshot` / `beschreiben` / `batch`.
3. **API-Key prüfen** — `ANTHROPIC_API_KEY` muss gesetzt sein (kein `load_dotenv()` in Ressource).
4. **Output nach stdout** — JSON oder Markdown; kein direktes Schreiben in Drittsysteme.
5. **Konfidenz kommunizieren** — Bei niedriger Konfidenz (< 0.7) Nutzer zur manuellen Prüfung auffordern.

## Batch-Verarbeitung — Übergabe an ETL-Pipeline

```bash
# Beispiel-Verkettung (Rechnungen batch → ETL → CSV)
python vision_dokument.py batch ./rechnungen/ rechnung \
  | python csv_etl_pipeline.py transformieren - "SELECT * FROM df WHERE konfidenz > 0.8" \
  > rechnungen_verifiziert.csv
```

## Infrastrukturelle Herausforderungen

| Herausforderung | Ursache | Lösung |
|----------------|---------|--------|
| **Token-Limit bei PDFs** | Jede Seite ≈ 1.500–3.000 Token | PDF → Bilder + Chunking; `vision_dokument.py batch` |
| **API-Ratenlimits** | Burst > 50 req/min → 429-Fehler | Exponentieller Backoff + Queue (max 3 Retry) |
| **Tabellenstruktur-Verlust** | Modell ignoriert Zellen-Grenzen | Prompt: `Behalte alle Zeilenumbrüche EXAKT bei` |
| **Ausgabe-Inkonsistenz** | JSON-Schema weicht ab | JSON-Schema im System-Prompt mitgeben |
| **Hochskalierbar (> 100 Seiten)** | Chunking + Retry zu komplex | Graphlit-Integration |

## Prompt-Engineering für OCR-ähnliche Aufgaben

```
System-Prompt Ergänzung für Tabellenextraktion:
"Behalte alle Zeilenumbrüche EXAKT bei. Trenne Tabellenspalten mit | (Pipe).
 Füge nach jeder Tabellenzeile einen Newline ein. Verliere keine Zelle."
```

## Graphlit-Integration (Enterprise-Scale)

Graphlit übernimmt: PDF-to-Image-Konvertierung, Seiten-Chunking, Retry-Logik, Output-Normalisierung.
Das Modell ist exklusiv für semantische und visuelle Extraktion zuständig.
Schnittstelle: Graphlit MCP-Server → `get_document_content` → Ergebnis an ETL-Pipeline.
