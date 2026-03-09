---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: vision-skill
description: >
  Bildbeschreibung, Dokumentenextraktion (Rechnungen/Quittungen),
  Diagramm-Analyse, Screenshot-Auswertung, Batch-Verarbeitung,
  PDF-Chunking, Graphlit-Integration, OCR-Prompt-Engineering.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Vision
    description: >
      Bildbeschreibung, Dokumentenextraktion (Rechnungen/Quittungen),
      Diagramm-Analyse, Screenshot-Auswertung, Batch-Verarbeitung,
      PDF-Chunking, Graphlit-Integration, OCR-Prompt-Engineering

triggers:
  # Vision / Bildbeschreibung / Dokumentenanalyse
  - Bild beschreiben oder kontextuell interpretieren (Vision)
  - Rechnung, Quittung oder Lieferschein aus Bild/Scan extrahieren
  - Balken-, Linien- oder Kreisdiagramm aus Screenshot analysieren
  - UI-Screenshot oder Fehlermeldung strukturiert beschreiben
  - Mehrere Bilder oder Dokumente als Batch verarbeiten
  - Visuelle Informationen in JSON oder Markdown überführen
  - OCR-ähnliche Extraktion aus analogen Dokumenten durchführen
  - Automatisierte Reporting-Workflows mit Bildinput aufbauen

resources:
  - resources/vision_dokument.py
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

## Vision: Bildbeschreibung und visuelle Dokumentenanalyse

Das Modell nähert sich Bildern nicht über einfache OCR oder Objekterkennung, sondern über
denselben Reasoning-Apparat wie bei Text: Achsenbeschriftungen werden gelesen, Relationen
zwischen Datenpunkten korreliert, strategische Bedeutung im Geschäftskontext interpretiert.

### Anwendungsfälle und Ausgabeformate

| Anwendungsfall | Input | Ausgabeformat | Ressource |
|---|---|---|---|
| **Allgemeine Bildbeschreibung** | Beliebiges Bild (PNG/JPG/WebP) | Markdown-Prose | `vision_dokument.py beschreiben` |
| **Rechnungs-/Quittungsextraktion** | Scan, Foto, PDF-Screenshot | JSON (strukturiert) | `vision_dokument.py rechnung` |
| **Diagramm-Analyse** | Chart-Screenshot (Balken/Linie/Kreis) | JSON + Interpretation | `vision_dokument.py diagramm` |
| **UI-Screenshot / Fehleranalyse** | Browser/App-Screenshot | Markdown strukturiert | `vision_dokument.py screenshot` |
| **Batch-Verarbeitung** | Verzeichnis mit Bildern | JSON-Lines (1 Datei = 1 Zeile) | `vision_dokument.py batch` |

### Architektur-Prinzip

```
Bild-Input (lokal / URL)
    ↓
Claude Vision API (claude-sonnet-4-6, base64 oder URL)
    ↓  kontextuelle Interpretation (kein simple OCR)
Strukturierter Output (JSON / Markdown)
    ↓
Downstream: ETL-Pipeline | Excel-Modell | Datenbank-Skill | Report
```

### Rechnungsextraktion — JSON-Schema (Standard)

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

### Diagramm-Analyse — Ausgabestruktur

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

### Pflicht-Ablauf für jeden Vision-Job

1. **Bildpfad bestätigen** — Pfad dem Nutzer anzeigen; kein autonomes Scannen ohne Freigabe.
2. **Modus wählen** — `rechnung` / `diagramm` / `screenshot` / `beschreiben` / `batch`.
3. **API-Key prüfen** — `ANTHROPIC_API_KEY` muss gesetzt sein (kein `load_dotenv()` in Ressource).
4. **Output nach stdout** — JSON oder Markdown; kein direktes Schreiben in Drittsysteme.
5. **Konfidenz kommunizieren** — Bei niedriger Konfidenz (`< 0.7`) Nutzer zur manuellen Prüfung auffordern.

### Batch-Verarbeitung — Übergabe an ETL-Pipeline

```
Verzeichnis mit Bildern
    → vision_dokument.py batch (JSON-Lines nach stdout)
    → Pipe zu csv_etl_pipeline.py transformieren
    → Konsolidierter Datensatz für DB-Einlagerung
```

```bash
# Beispiel-Verkettung (Rechnungen batch → ETL → Excel)
python vision_dokument.py batch ./rechnungen/ rechnung \
  | python csv_etl_pipeline.py transformieren - "SELECT * FROM df WHERE konfidenz > 0.8" \
  > rechnungen_verifiziert.csv
```

### Infrastrukturelle Herausforderungen & Skalierung

Rohe API-Aufrufe stoßen bei hochskalierenden Office-Anwendungen an Grenzen.
Pflicht-Überlegungen vor dem Einsatz:

| Herausforderung | Ursache | Lösung |
|---|---|---|
| **Token-Limit bei PDFs** | Jede Seite ≈ 1.500–3.000 Token; 100-Seiten-PDF > Kontext-Fenster | PDF → Bilder (1 Bild/Seite) + Chunking; `vision_dokument.py batch` |
| **API-Ratenlimits** | Burst > 50 req/min triggert 429-Fehler | Exponentieller Backoff + Queue (max 3 Retry); Graphlit übernimmt dies |
| **Tabellenstruktur-Verlust** | Modell ignoriert Zellen-Grenzen ohne expliziten Prompt | Prompt muss explizit fordern: `Behalte alle Zeilenumbrüche und Tabellenstruktur exakt bei` |
| **Ausgabe-Inkonsistenz** | JSON-Schema weicht bei seltenen Layouts ab | JSON-Schema im System-Prompt mitgeben; `IFERROR`-ähnliches Fallback in Parser |
| **Hochskalierbar (> 100 Seiten)** | Eigenimplementierung von Chunking + Retry zu komplex | Graphlit-Integration: übernimmt Chunking, Ratenlimit, Normalisierung |

**Prompt-Engineering für OCR-ähnliche Aufgaben (Pflicht):**

```
System-Prompt Ergänzung für Tabellenextraktion:
"Behalte alle Zeilenumbrüche EXAKT bei. Trenne Tabellenspalten mit | (Pipe).
 Füge nach jeder Tabellenzeile einen Newline ein. Verliere keine Zelle."
```

**Graphlit-Integration (für Enterprise-Scale):**
- Graphlit übernimmt: PDF-to-Image-Konvertierung, Seiten-Chunking, Retry-Logik, Output-Normalisierung
- Das Modell ist exklusiv für semantische und visuelle Extraktion zuständig
- Schnittstelle: Graphlit MCP-Server → `get_document_content` → Ergebnis an ETL-Pipeline

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
| `resources/vision_dokument.py` | 3 | Vision | Claude Vision API: Rechnung/Diagramm/Screenshot/Batch → JSON oder Markdown |
