# Design: pjc3-viz1 — Lokales Datenvisualisierungs-Tool

**Datum:** 2026-03-09
**Status:** Genehmigt

---

## Ziel

Eigenständiges Python-Projekt mit Streamlit-App zur lokalen, interaktiven Datenvisualisierung.
Kein Claude API-Bezug — reiner Viz-Stack.

---

## Projektstruktur

```
~/claude-c/pjc3-viz1/
├── app.py
├── requirements.txt
├── .gitignore
└── venv/          # nicht in Git
```

---

## Architektur: Single-File (Ansatz A)

Alle Logik in `app.py`. Keine zusätzlichen Module.

---

## Datenfluss

```
Datei-Upload (.csv / .xlsx)
  → pandas einlesen
  → Vorschau: head(5) via st.dataframe
  → Sidebar: X-Achse, Y-Achse, Diagrammtyp auswählen
  → plotly.express Diagramm rendern (interaktiv)
```

---

## Fehlerbehandlung

| Situation | Verhalten |
|---|---|
| Keine Spalte ausgewählt | `st.warning()` — kein Absturz |
| Lesefehler beim Upload | `st.error()` mit Meldung |
| Nicht-numerische Y-Achse (bar/line) | `st.warning()` mit Hinweis |

---

## Abhängigkeiten (`requirements.txt`)

- `streamlit`
- `pandas`
- `plotly`
- `openpyxl`

---

## Setup-Schritte

1. Verzeichnis `~/claude-c/pjc3-viz1/` anlegen
2. `git init`
3. `python3 -m venv venv` + aktivieren
4. `pip install -r requirements.txt`
5. `.gitignore` mit `venv/`, `__pycache__/`, `*.pyc`, `.env`
6. `app.py` implementieren
7. `streamlit run app.py`
