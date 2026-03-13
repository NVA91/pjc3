# Excel-Automatisierung und Finanzmodellierung — Detailreferenz

## Fähigkeiten-Übersicht

| Bereich | Fähigkeiten | Ressource |
|---------|-------------|-----------|
| **Institutionelle Finanzmodelle** | 3-Statement (IS/BS/CF), SaaS-Metriken (ARR/Churn/LTV), Szenario-Analyse (Base/Bull/Bear) | `excel_finanzmodell.py` |
| **Datenaufbereitung & Pivot** | Importierte Daten sortieren/filtern, Pivot-Schema ändern, fehlende Werte füllen, Duplikate entfernen | `excel_finanzmodell.py` |
| **Industriestandard-Formatierung** | Blaue Schrift = manuelle Eingabe, Schwarz = Formel, bedingte Formatierung, Datenbalken | `excel_finanzmodell.py` |
| **Debugging & Verifikation** | Zirkelbezüge lokalisieren, #REF!/#VALUE! korrigieren, LibreOffice headless Formel-Check | `excel_finanzmodell.py` |

## Farbcodierungs-Konvention (Finanzmodellierungs-Standard)

| Schriftfarbe | Hex | Bedeutung | Wann setzen |
|-------------|-----|-----------|-------------|
| Blau | `#0070C0` | Manuelle Eingabe / Annahme | Hardcoded input cells |
| Schwarz | `#000000` | Berechnete Formel | Alle `=`-Zellen |
| Grün | `#00B050` | Verknüpfung zu anderem Sheet | Cross-sheet references |
| Rot | `#FF0000` | Fehler / Warnung | Negative Werte, Checks |

## Ablauf für jedes Finanzmodell

1. **Struktur bestätigen** — Welche Sheets? Welche Perioden (Monate/Jahre)?
2. **Annahmen-Zellen definieren** — Blau färben, benennen (Named Ranges)
3. **Formeln injizieren** — Niemals berechnete Werte hardcoden
4. **Formatierung anwenden** — Zahlenformate, bedingte Formatierung
5. **Verifizieren** — LibreOffice headless öffnen, Formel-Errors prüfen, stdout-Report

## Debugging-Protokoll (#REF!, #VALUE!, Zirkelbezüge)

```
1. Fehlerzellen lokalisieren → ws.iter_rows() + cell.value.startswith("#") prüfen
2. Ursache klassifizieren:
   ├── #REF!  → gelöschte/verschobene Quellzelle → Formel neu aufbauen
   ├── #VALUE! → falscher Datentyp in Formel → Typ-Cast oder Quellzelle prüfen
   └── Zirkelbezug → Abhängigkeits-Graph traversieren → Iterative Calculation oder Formel umstrukturieren
3. Korrektur dokumentieren → Kommentar in Zelle schreiben
4. Re-Verifikation → LibreOffice erneut ausführen → 0 Errors bestätigen
```

## Status-Farbschema für Aufgabentabellen (fest, nicht ändern)

| Status | Hex | Verwendung |
|--------|-----|------------|
| Offen | `FFE699` | Gelb — noch nicht begonnen |
| In Arbeit | `9DC3E6` | Blau — aktiv bearbeitet |
| Erledigt | `A9D18E` | Grün — abgeschlossen |
| Blockiert | `FF7C80` | Rot — Blocker vorhanden |

## Voraussetzungen

Prüfen ob `openpyxl` installiert: `pip show openpyxl`
LibreOffice headless für Verifikation: `libreoffice --headless --calc --convert-to xlsx datei.xlsx`
