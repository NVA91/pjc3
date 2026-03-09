# pjc3-viz1 Visualisierungs-App — Implementierungsplan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Eigenständiges Streamlit-Projekt mit interaktiver CSV/XLSX-Datenvisualisierung via Plotly Express.

**Architecture:** Single-file Streamlit-App (`app.py`) mit File-Upload, Pandas-Vorschau und dynamischer Sidebar-Steuerung. Kein Backend, kein State-Management — alles in-memory pro Session.

**Tech Stack:** Python 3, streamlit, pandas, plotly.express, openpyxl, venv

---

### Task 1: Projektverzeichnis und Git-Repository anlegen

**Files:**
- Create: `~/claude-c/pjc3-viz1/` (Verzeichnis)

**Step 1: Verzeichnis anlegen und Git initialisieren**

```bash
mkdir -p ~/claude-c/pjc3-viz1
cd ~/claude-c/pjc3-viz1
git init
```

Expected: `Initialized empty Git repository in .../pjc3-viz1/.git/`

**Step 2: .gitignore erstellen**

Datei `~/claude-c/pjc3-viz1/.gitignore`:

```
venv/
__pycache__/
*.pyc
.env
.DS_Store
```

**Step 3: Commit**

```bash
cd ~/claude-c/pjc3-viz1
git add .gitignore
git commit -m "Initial commit: add .gitignore"
```

---

### Task 2: Virtuelle Umgebung und Abhängigkeiten einrichten

**Files:**
- Create: `~/claude-c/pjc3-viz1/requirements.txt`

**Step 1: venv anlegen und aktivieren**

```bash
cd ~/claude-c/pjc3-viz1
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

Expected: `Successfully installed pip X.X.X`

**Step 2: requirements.txt erstellen**

Datei `~/claude-c/pjc3-viz1/requirements.txt`:

```
streamlit
pandas
plotly
openpyxl
```

**Step 3: Abhängigkeiten installieren**

```bash
pip install -r requirements.txt
```

Expected: Kein Fehler, alle Pakete installiert.

**Step 4: Verify**

```bash
python -c "import streamlit, pandas, plotly, openpyxl; print('OK')"
```

Expected: `OK`

**Step 5: Commit**

```bash
git add requirements.txt
git commit -m "Add requirements.txt with viz stack"
```

---

### Task 3: app.py — Grundgerüst und Datei-Upload

**Files:**
- Create: `~/claude-c/pjc3-viz1/app.py`

**Step 1: app.py mit Grundstruktur erstellen**

Datei `~/claude-c/pjc3-viz1/app.py`:

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Datenvisualisierung", layout="wide")
st.title("Universelles Datenvisualisierungs-Tool")

uploaded_file = st.file_uploader(
    "CSV- oder Excel-Datei hochladen",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
        st.stop()

    st.subheader("Datenvorschau (erste 5 Zeilen)")
    st.dataframe(df.head())
```

**Step 2: App starten und Upload testen**

```bash
cd ~/claude-c/pjc3-viz1
source venv/bin/activate
streamlit run app.py
```

Manuell prüfen: Browser öffnet sich, Upload-Widget sichtbar, CSV-Upload zeigt Vorschau.

**Step 3: Commit**

```bash
git add app.py
git commit -m "Add file upload and data preview"
```

---

### Task 4: Sidebar mit dynamischer Spaltenauswahl

**Files:**
- Modify: `~/claude-c/pjc3-viz1/app.py`

**Step 1: Sidebar-Steuerung nach dem Datenvorschau-Block einfügen**

Den bestehenden `if uploaded_file is not None:`-Block erweitern — nach `st.dataframe(df.head())` folgendes hinzufügen:

```python
    st.sidebar.header("Diagramm-Einstellungen")

    columns = df.columns.tolist()

    x_col = st.sidebar.selectbox("X-Achse", options=[""] + columns)
    y_col = st.sidebar.selectbox("Y-Achse", options=[""] + columns)
    chart_type = st.sidebar.selectbox(
        "Diagrammtyp",
        options=["Balkendiagramm", "Liniendiagramm", "Streudiagramm"]
    )
```

**Step 2: Manuell prüfen**

Datei hochladen → Sidebar zeigt Spaltenauswahl und Diagrammtyp-Dropdown.

**Step 3: Commit**

```bash
git add app.py
git commit -m "Add sidebar with dynamic column selection"
```

---

### Task 5: Plotly-Diagramm rendern mit Fehlerbehandlung

**Files:**
- Modify: `~/claude-c/pjc3-viz1/app.py`

**Step 1: Diagramm-Block nach der Sidebar-Steuerung einfügen**

Direkt nach dem `chart_type`-Selectbox-Block:

```python
    if not x_col or not y_col:
        st.warning("Bitte X-Achse und Y-Achse in der Sidebar auswählen.")
    else:
        try:
            if chart_type == "Balkendiagramm":
                fig = px.bar(df, x=x_col, y=y_col)
            elif chart_type == "Liniendiagramm":
                fig = px.line(df, x=x_col, y=y_col)
            else:
                fig = px.scatter(df, x=x_col, y=y_col)

            st.subheader(f"{chart_type}: {x_col} vs. {y_col}")
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Fehler beim Erstellen des Diagramms: {e}")
```

**Step 2: Manuell testen — Fehlerfälle**

- Keine Spalten ausgewählt → `st.warning()` sichtbar
- Gültige Spalten → Diagramm erscheint interaktiv (Zoom/Hover funktioniert)
- Nicht-numerische Y-Spalte bei Balken → `st.error()` erscheint

**Step 3: Commit**

```bash
git add app.py
git commit -m "Add plotly chart rendering with error handling"
```

---

### Task 6: Abschluss — README und finaler Commit

**Files:**
- Create: `~/claude-c/pjc3-viz1/README.md`

**Step 1: README erstellen**

Datei `~/claude-c/pjc3-viz1/README.md`:

```markdown
# pjc3-viz1 — Lokales Datenvisualisierungs-Tool

Streamlit-App zur interaktiven Visualisierung von CSV- und Excel-Dateien.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Starten

```bash
streamlit run app.py
```

## Verwendung

1. CSV- oder XLSX-Datei hochladen
2. In der Sidebar X-Achse, Y-Achse und Diagrammtyp wählen
3. Interaktives Diagramm erscheint (Zoom, Hover)
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage"
```

---

## Vollständige app.py (Referenz)

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Datenvisualisierung", layout="wide")
st.title("Universelles Datenvisualisierungs-Tool")

uploaded_file = st.file_uploader(
    "CSV- oder Excel-Datei hochladen",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
        st.stop()

    st.subheader("Datenvorschau (erste 5 Zeilen)")
    st.dataframe(df.head())

    st.sidebar.header("Diagramm-Einstellungen")
    columns = df.columns.tolist()

    x_col = st.sidebar.selectbox("X-Achse", options=[""] + columns)
    y_col = st.sidebar.selectbox("Y-Achse", options=[""] + columns)
    chart_type = st.sidebar.selectbox(
        "Diagrammtyp",
        options=["Balkendiagramm", "Liniendiagramm", "Streudiagramm"]
    )

    if not x_col or not y_col:
        st.warning("Bitte X-Achse und Y-Achse in der Sidebar auswählen.")
    else:
        try:
            if chart_type == "Balkendiagramm":
                fig = px.bar(df, x=x_col, y=y_col)
            elif chart_type == "Liniendiagramm":
                fig = px.line(df, x=x_col, y=y_col)
            else:
                fig = px.scatter(df, x=x_col, y=y_col)

            st.subheader(f"{chart_type}: {x_col} vs. {y_col}")
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Fehler beim Erstellen des Diagramms: {e}")
```
