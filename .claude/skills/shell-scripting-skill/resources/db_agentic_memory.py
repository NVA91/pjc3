#!/usr/bin/env python3
# LADESTUFE 3 — RESSOURCE | KATEGORIE: Datenbank / Agentic Memory
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: SQLite-basiertes Langzeitgedächtnis für KI-Agenten.
#               Speichert Entitäten, kontextuelle Beziehungen und Interaktions-
#               historie persistent über Session-Grenzen hinweg. Optionaler
#               HTTP-Server-Modus für Headless-Agent-Steuerung.
#
# VERWENDUNG:
#   python db_agentic_memory.py init    [DB_PFAD]
#   python db_agentic_memory.py entity  speichern  NAME TYP BESCHREIBUNG [--projekt NAME]
#   python db_agentic_memory.py entity  suchen     SUCHBEGRIFF [--projekt NAME]
#   python db_agentic_memory.py entity  liste      [--projekt NAME] [--typ TYP]
#   python db_agentic_memory.py relation speichern VON RELATION NACH [--beschreibung TEXT]
#   python db_agentic_memory.py relation suchen    ENTITY_NAME
#   python db_agentic_memory.py interaktion speichern PROMPT RESPONSE [--entity NAME] [--tags TAG1,TAG2]
#   python db_agentic_memory.py kontext  abrufen   [--projekt NAME] [--limit N]
#   python db_agentic_memory.py kontext  setzen    SCHLUESSEL WERT [--projekt NAME]
#   python db_agentic_memory.py export   [--projekt NAME] [--format json|markdown]
#   python db_agentic_memory.py server   [--port 8765]
#   python db_agentic_memory.py stats
#
# VORAUSSETZUNG:
#   Python 3.8+ (sqlite3 in Stdlib enthalten)
#   Für HTTP-Server-Modus: pip install fastapi uvicorn
#
# DATENBANK-SCHEMA:
#   entities     — Projektentitäten (Dateien, Funktionen, Konzepte, Entscheidungen)
#   relations    — Kontextbeziehungen zwischen Entitäten
#   interactions — Interaktionshistorie (Prompt + Response + Tags)
#   context      — Session-übergreifende Schlüssel-Wert-Fakten

from __future__ import annotations

import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any

# =============================================================================
# KONFIGURATION
# =============================================================================

DEFAULT_DB = Path(os.environ.get("MEMORY_DB", "memory.db"))
DEFAULT_PROJEKT = os.environ.get("MEMORY_PROJEKT", "default")
DEFAULT_LIMIT = 20

# =============================================================================
# UTILITIES
# =============================================================================

def _ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _log(msg: str) -> None:
    print(f"[{_ts()}] {msg}", file=sys.stderr)

def _ok(msg: str) -> None:
    print(f"OK  | {msg}", file=sys.stderr)

def _err(msg: str, code: int = 1) -> None:
    print(f"ERR | {msg}", file=sys.stderr)
    sys.exit(code)

def _json_out(daten: Any) -> None:
    """Gibt strukturierte Daten als JSON nach stdout aus."""
    print(json.dumps(daten, ensure_ascii=False, indent=2, default=str))

# =============================================================================
# DATENBANK — Schema und Verbindung
# =============================================================================

SCHEMA = """
-- Entitäten: Projektbausteine (Dateien, Funktionen, Konzepte, Entscheidungen)
CREATE TABLE IF NOT EXISTS entities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    typ         TEXT    NOT NULL DEFAULT 'concept',  -- function|file|concept|decision|module|api
    beschreibung TEXT   DEFAULT '',
    projekt     TEXT    NOT NULL DEFAULT 'default',
    tags        TEXT    DEFAULT '',     -- komma-separiert
    erstellt_am TEXT    NOT NULL,
    geaendert_am TEXT   NOT NULL,
    UNIQUE(name, projekt)
);

-- Beziehungen zwischen Entitäten (gerichteter Graph)
CREATE TABLE IF NOT EXISTS relations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    von         TEXT    NOT NULL,      -- Entitäts-Name (Quelle)
    relation    TEXT    NOT NULL,      -- "implementiert", "hängt ab von", "gehört zu", "ruft auf"
    nach        TEXT    NOT NULL,      -- Entitäts-Name (Ziel)
    projekt     TEXT    NOT NULL DEFAULT 'default',
    beschreibung TEXT   DEFAULT '',
    erstellt_am TEXT    NOT NULL
);

-- Interaktionshistorie: Prompt + Response + Kontext-Tags
CREATE TABLE IF NOT EXISTS interactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt      TEXT    NOT NULL,
    response    TEXT    NOT NULL,
    entity      TEXT    DEFAULT NULL,  -- verknüpfte Entität (optional)
    projekt     TEXT    NOT NULL DEFAULT 'default',
    tags        TEXT    DEFAULT '',    -- komma-separiert
    token_count INTEGER DEFAULT 0,
    erstellt_am TEXT    NOT NULL
);

-- Session-übergreifende Kontext-Fakten (Schlüssel-Wert)
CREATE TABLE IF NOT EXISTS context (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    schluessel  TEXT    NOT NULL,
    wert        TEXT    NOT NULL,
    projekt     TEXT    NOT NULL DEFAULT 'default',
    erstellt_am TEXT    NOT NULL,
    geaendert_am TEXT   NOT NULL,
    UNIQUE(schluessel, projekt)
);

-- Indizes für häufige Abfragen
CREATE INDEX IF NOT EXISTS idx_entities_projekt   ON entities(projekt);
CREATE INDEX IF NOT EXISTS idx_entities_typ       ON entities(typ);
CREATE INDEX IF NOT EXISTS idx_relations_von      ON relations(von, projekt);
CREATE INDEX IF NOT EXISTS idx_relations_nach     ON relations(nach, projekt);
CREATE INDEX IF NOT EXISTS idx_interactions_proj  ON interactions(projekt, erstellt_am DESC);
CREATE INDEX IF NOT EXISTS idx_context_key        ON context(schluessel, projekt);
"""

def _verbinden(db_pfad: Path) -> sqlite3.Connection:
    """Öffnet SQLite-Verbindung mit WAL-Modus für bessere Concurrency."""
    conn = sqlite3.connect(str(db_pfad))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn

def _conn(db_pfad: Path | None = None) -> sqlite3.Connection:
    pfad = db_pfad or DEFAULT_DB
    if not pfad.exists():
        _err(f"Datenbank nicht gefunden: {pfad}\nZuerst ausführen: python db_agentic_memory.py init")
    return _verbinden(pfad)

# =============================================================================
# MODUS 1: INIT — Schema anlegen
# =============================================================================

def modus_init(db_pfad: Path) -> None:
    """Initialisiert die SQLite-Datenbank mit vollständigem Schema."""
    if db_pfad.exists():
        _log(f"Datenbank existiert bereits: {db_pfad} — Schema wird aktualisiert")
    else:
        _log(f"Neue Datenbank anlegen: {db_pfad}")

    conn = _verbinden(db_pfad)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

    _ok(f"Datenbank initialisiert: {db_pfad}")
    _json_out({
        "status": "ok",
        "db_pfad": str(db_pfad),
        "tabellen": ["entities", "relations", "interactions", "context"],
        "erstellt_am": _ts(),
    })

# =============================================================================
# MODUS 2: ENTITY — Entitäten verwalten
# =============================================================================

def entity_speichern(name: str, typ: str, beschreibung: str,
                     projekt: str, tags: str, db_pfad: Path) -> None:
    """Speichert oder aktualisiert eine Entität (UPSERT)."""
    jetzt = _ts()
    conn = _conn(db_pfad)
    conn.execute("""
        INSERT INTO entities (name, typ, beschreibung, projekt, tags, erstellt_am, geaendert_am)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name, projekt) DO UPDATE SET
            typ          = excluded.typ,
            beschreibung = excluded.beschreibung,
            tags         = excluded.tags,
            geaendert_am = excluded.geaendert_am
    """, (name, typ, beschreibung, projekt, tags, jetzt, jetzt))
    conn.commit()
    conn.close()
    _ok(f"Entität gespeichert: {name} ({typ}) [Projekt: {projekt}]")
    _json_out({"status": "ok", "name": name, "typ": typ, "projekt": projekt})

def entity_suchen(suchbegriff: str, projekt: str | None, db_pfad: Path) -> None:
    """Volltext-Suche in Entitäten (Name + Beschreibung + Tags)."""
    conn = _conn(db_pfad)
    if projekt:
        rows = conn.execute("""
            SELECT * FROM entities
            WHERE projekt = ?
              AND (name LIKE ? OR beschreibung LIKE ? OR tags LIKE ?)
            ORDER BY geaendert_am DESC LIMIT 50
        """, (projekt, f"%{suchbegriff}%", f"%{suchbegriff}%", f"%{suchbegriff}%")).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM entities
            WHERE name LIKE ? OR beschreibung LIKE ? OR tags LIKE ?
            ORDER BY geaendert_am DESC LIMIT 50
        """, (f"%{suchbegriff}%", f"%{suchbegriff}%", f"%{suchbegriff}%")).fetchall()
    conn.close()
    _json_out([dict(r) for r in rows])

def entity_liste(projekt: str | None, typ: str | None, db_pfad: Path) -> None:
    """Listet alle Entitäten eines Projekts."""
    conn = _conn(db_pfad)
    bedingungen = []
    params: list[Any] = []
    if projekt:
        bedingungen.append("projekt = ?"); params.append(projekt)
    if typ:
        bedingungen.append("typ = ?"); params.append(typ)
    wo = ("WHERE " + " AND ".join(bedingungen)) if bedingungen else ""
    rows = conn.execute(
        f"SELECT * FROM entities {wo} ORDER BY typ, name", params
    ).fetchall()
    conn.close()
    _json_out([dict(r) for r in rows])

# =============================================================================
# MODUS 3: RELATION — Beziehungen verwalten
# =============================================================================

ERLAUBTE_RELATIONEN = {
    "implementiert", "hängt ab von", "gehört zu", "ruft auf",
    "erbt von", "enthält", "verweist auf", "ersetzt", "erweitert",
    "testet", "konfiguriert", "produziert", "konsumiert",
}

def relation_speichern(von: str, relation: str, nach: str,
                       projekt: str, beschreibung: str, db_pfad: Path) -> None:
    """Speichert eine Beziehung zwischen zwei Entitäten."""
    if relation not in ERLAUBTE_RELATIONEN:
        _log(f"Nicht-Standard-Relation: '{relation}' — erlaubt aber nicht normalisiert")
    conn = _conn(db_pfad)
    conn.execute("""
        INSERT INTO relations (von, relation, nach, projekt, beschreibung, erstellt_am)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (von, relation, nach, projekt, beschreibung, _ts()))
    conn.commit()
    conn.close()
    _ok(f"Relation gespeichert: {von} --[{relation}]--> {nach}")
    _json_out({"status": "ok", "von": von, "relation": relation, "nach": nach})

def relation_suchen(entity_name: str, db_pfad: Path) -> None:
    """Gibt alle Beziehungen einer Entität zurück (ausgehend und eingehend)."""
    conn = _conn(db_pfad)
    ausgehend = conn.execute(
        "SELECT * FROM relations WHERE von = ? ORDER BY relation", (entity_name,)
    ).fetchall()
    eingehend = conn.execute(
        "SELECT * FROM relations WHERE nach = ? ORDER BY relation", (entity_name,)
    ).fetchall()
    conn.close()
    _json_out({
        "entity": entity_name,
        "ausgehend": [dict(r) for r in ausgehend],
        "eingehend": [dict(r) for r in eingehend],
    })

# =============================================================================
# MODUS 4: INTERAKTION — Verlauf persistieren
# =============================================================================

def interaktion_speichern(prompt: str, response: str, entity: str | None,
                          projekt: str, tags: str, db_pfad: Path) -> None:
    """Speichert eine Interaktion (Prompt + Response) in der Verlaufshistorie."""
    token_schaetzung = (len(prompt) + len(response)) // 4
    conn = _conn(db_pfad)
    conn.execute("""
        INSERT INTO interactions (prompt, response, entity, projekt, tags, token_count, erstellt_am)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (prompt, response, entity, projekt, tags, token_schaetzung, _ts()))
    conn.commit()
    conn.close()
    _ok(f"Interaktion gespeichert (~{token_schaetzung} Token) [Projekt: {projekt}]")
    _json_out({"status": "ok", "token_schaetzung": token_schaetzung, "projekt": projekt})

# =============================================================================
# MODUS 5: KONTEXT — Session-übergreifende Fakten
# =============================================================================

def kontext_setzen(schluessel: str, wert: str, projekt: str, db_pfad: Path) -> None:
    """Speichert oder aktualisiert einen Kontext-Fakt."""
    jetzt = _ts()
    conn = _conn(db_pfad)
    conn.execute("""
        INSERT INTO context (schluessel, wert, projekt, erstellt_am, geaendert_am)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(schluessel, projekt) DO UPDATE SET
            wert         = excluded.wert,
            geaendert_am = excluded.geaendert_am
    """, (schluessel, wert, projekt, jetzt, jetzt))
    conn.commit()
    conn.close()
    _ok(f"Kontext gesetzt: {schluessel} = {wert[:60]}... [Projekt: {projekt}]")

def kontext_abrufen(projekt: str | None, limit: int, db_pfad: Path) -> None:
    """
    Ruft historischen Kontext ab — ideal zum Session-Start einer neuen Agenten-Session.
    Gibt Entitäten, Relationen, letzte Interaktionen und Kontext-Fakten zurück.
    """
    conn = _conn(db_pfad)

    # Entitäten (neueste zuerst)
    e_query = "SELECT name, typ, beschreibung, tags FROM entities"
    e_params: list[Any] = []
    if projekt:
        e_query += " WHERE projekt = ?"; e_params.append(projekt)
    e_query += f" ORDER BY geaendert_am DESC LIMIT {limit}"
    entitaeten = [dict(r) for r in conn.execute(e_query, e_params).fetchall()]

    # Letzte Interaktionen (Zusammenfassung)
    i_query = "SELECT prompt, response, entity, tags, erstellt_am FROM interactions"
    i_params: list[Any] = []
    if projekt:
        i_query += " WHERE projekt = ?"; i_params.append(projekt)
    i_query += f" ORDER BY erstellt_am DESC LIMIT {limit // 2}"
    interaktionen = []
    for r in conn.execute(i_query, i_params).fetchall():
        d = dict(r)
        # Prompt + Response für Token-Effizienz kürzen
        d["prompt"]   = d["prompt"][:200] + ("..." if len(d["prompt"]) > 200 else "")
        d["response"] = d["response"][:400] + ("..." if len(d["response"]) > 400 else "")
        interaktionen.append(d)

    # Kontext-Fakten
    k_query = "SELECT schluessel, wert, geaendert_am FROM context"
    k_params: list[Any] = []
    if projekt:
        k_query += " WHERE projekt = ?"; k_params.append(projekt)
    k_query += " ORDER BY geaendert_am DESC"
    kontext_fakten = [dict(r) for r in conn.execute(k_query, k_params).fetchall()]

    conn.close()

    _json_out({
        "abruf_zeitpunkt": _ts(),
        "projekt": projekt or "alle",
        "entitaeten": entitaeten,
        "interaktionen": interaktionen,
        "kontext_fakten": kontext_fakten,
        "hinweis": (
            "Diesen JSON-Block an den Agenten als System-Kontext übergeben. "
            "Reduziert Token-Bedarf gegenüber einer neuen Codebase-Analyse."
        ),
    })

# =============================================================================
# MODUS 6: EXPORT — Vollexport für Übergabe / Backup
# =============================================================================

def modus_export(projekt: str | None, fmt: str, db_pfad: Path) -> None:
    """Exportiert die gesamte Memory-Datenbank als JSON oder Markdown."""
    conn = _conn(db_pfad)

    def q(table: str, filter_proj: bool = True) -> list[dict]:
        sql = f"SELECT * FROM {table}"
        params: list[Any] = []
        if filter_proj and projekt:
            sql += " WHERE projekt = ?"; params.append(projekt)
        sql += " ORDER BY id"
        return [dict(r) for r in conn.execute(sql, params).fetchall()]

    daten = {
        "export_zeitpunkt": _ts(),
        "projekt": projekt or "alle",
        "entities":     q("entities"),
        "relations":    q("relations"),
        "interactions": q("interactions"),
        "context":      q("context"),
    }
    conn.close()

    if fmt == "json":
        _json_out(daten)

    elif fmt == "markdown":
        md = [f"# Agentic Memory Export\n\n**Projekt:** {daten['projekt']}  ",
              f"**Zeitpunkt:** {daten['export_zeitpunkt']}\n"]

        md.append("\n## Entitäten\n")
        md.append("| Name | Typ | Beschreibung | Tags |")
        md.append("|---|---|---|---|")
        for e in daten["entities"]:
            md.append(f"| {e['name']} | {e['typ']} | {e['beschreibung'][:60]} | {e['tags']} |")

        md.append("\n## Beziehungen\n")
        md.append("| Von | Relation | Nach | Beschreibung |")
        md.append("|---|---|---|---|")
        for r in daten["relations"]:
            md.append(f"| {r['von']} | {r['relation']} | {r['nach']} | {r['beschreibung'][:40]} |")

        md.append("\n## Kontext-Fakten\n")
        for k in daten["context"]:
            md.append(f"- **{k['schluessel']}**: {k['wert']}")

        md.append(f"\n## Interaktionen ({len(daten['interactions'])} Einträge)\n")
        for i in daten["interactions"][:10]:
            md.append(f"### {i['erstellt_am']} ({i.get('entity', '—')})")
            md.append(f"**Prompt:** {i['prompt'][:150]}...")
            md.append(f"**Response:** {i['response'][:300]}...\n")

        print("\n".join(md))

# =============================================================================
# MODUS 7: STATS — Datenbank-Statistik
# =============================================================================

def modus_stats(db_pfad: Path) -> None:
    conn = _conn(db_pfad)
    stats = {
        "db_pfad":        str(db_pfad),
        "db_groesse_kb":  round(db_pfad.stat().st_size / 1024, 1),
        "entities":       conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
        "relations":      conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
        "interactions":   conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0],
        "context_fakten": conn.execute("SELECT COUNT(*) FROM context").fetchone()[0],
        "projekte":       [r[0] for r in conn.execute(
            "SELECT DISTINCT projekt FROM entities ORDER BY projekt"
        ).fetchall()],
        "entity_typen": dict(conn.execute(
            "SELECT typ, COUNT(*) FROM entities GROUP BY typ ORDER BY COUNT(*) DESC"
        ).fetchall()),
        "token_gesamt_schaetzung": (
            conn.execute("SELECT SUM(token_count) FROM interactions").fetchone()[0] or 0
        ),
    }
    conn.close()
    _json_out(stats)

# =============================================================================
# MODUS 8: SERVER — HTTP-Server für Headless-Agent-Steuerung
# =============================================================================

def modus_server(port: int, db_pfad: Path) -> None:
    """
    Startet lokalen HTTP-Server für Headless-Agent-Steuerung.
    Ermöglicht externes Triggern von Agent-Sessions über POST-Requests.

    Voraussetzung: pip install fastapi uvicorn
    """
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
        from pydantic import BaseModel
        import uvicorn
    except ImportError:
        _err(
            "Server-Modus benötigt: pip install fastapi uvicorn\n"
            "Alternativ: Direkte CLI-Verwendung ohne Server-Modus"
        )

    app = FastAPI(title="Agentic Memory Server", version="1.0")

    class EntityRequest(BaseModel):
        name: str
        typ: str = "concept"
        beschreibung: str = ""
        projekt: str = DEFAULT_PROJEKT
        tags: str = ""

    class RelationRequest(BaseModel):
        von: str
        relation: str
        nach: str
        projekt: str = DEFAULT_PROJEKT
        beschreibung: str = ""

    class InteraktionRequest(BaseModel):
        prompt: str
        response: str
        entity: str | None = None
        projekt: str = DEFAULT_PROJEKT
        tags: str = ""

    class KontextRequest(BaseModel):
        schluessel: str
        wert: str
        projekt: str = DEFAULT_PROJEKT

    @app.get("/health")
    def health():
        return {"status": "ok", "db": str(db_pfad)}

    @app.get("/stats")
    def stats():
        conn = _conn(db_pfad)
        result = {
            "entities": conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
            "relations": conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
            "interactions": conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0],
        }
        conn.close()
        return result

    @app.post("/entity")
    def entity_post(req: EntityRequest):
        entity_speichern(req.name, req.typ, req.beschreibung,
                         req.projekt, req.tags, db_pfad)
        return {"status": "ok", "name": req.name}

    @app.get("/entity/suchen")
    def entity_get(q: str, projekt: str = DEFAULT_PROJEKT):
        conn = _conn(db_pfad)
        rows = conn.execute("""
            SELECT * FROM entities WHERE projekt = ?
              AND (name LIKE ? OR beschreibung LIKE ? OR tags LIKE ?)
            ORDER BY geaendert_am DESC LIMIT 50
        """, (projekt, f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @app.post("/relation")
    def relation_post(req: RelationRequest):
        relation_speichern(req.von, req.relation, req.nach,
                           req.projekt, req.beschreibung, db_pfad)
        return {"status": "ok"}

    @app.post("/interaktion")
    def interaktion_post(req: InteraktionRequest):
        interaktion_speichern(req.prompt, req.response, req.entity,
                              req.projekt, req.tags, db_pfad)
        return {"status": "ok"}

    @app.post("/kontext")
    def kontext_post(req: KontextRequest):
        kontext_setzen(req.schluessel, req.wert, req.projekt, db_pfad)
        return {"status": "ok"}

    @app.get("/kontext")
    def kontext_get(projekt: str = DEFAULT_PROJEKT, limit: int = DEFAULT_LIMIT):
        conn = _conn(db_pfad)
        result = {
            "entitaeten": [dict(r) for r in conn.execute(
                "SELECT name, typ, beschreibung, tags FROM entities WHERE projekt = ? "
                "ORDER BY geaendert_am DESC LIMIT ?", (projekt, limit)
            ).fetchall()],
            "kontext_fakten": [dict(r) for r in conn.execute(
                "SELECT schluessel, wert FROM context WHERE projekt = ?", (projekt,)
            ).fetchall()],
        }
        conn.close()
        return result

    _log(f"HTTP-Server startet auf Port {port} (DB: {db_pfad})")
    _log("Endpunkte: GET /health | GET /stats | POST /entity | POST /relation | "
         "POST /interaktion | POST /kontext | GET /kontext")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

# =============================================================================
# HILFE
# =============================================================================

HILFE = """
VERWENDUNG:
  python db_agentic_memory.py init     [DB_PFAD]
  python db_agentic_memory.py entity   speichern  NAME TYP BESCHREIBUNG [--projekt P] [--tags T1,T2]
  python db_agentic_memory.py entity   suchen     SUCHBEGRIFF [--projekt P]
  python db_agentic_memory.py entity   liste      [--projekt P] [--typ TYP]
  python db_agentic_memory.py relation speichern  VON RELATION NACH [--projekt P] [--beschreibung B]
  python db_agentic_memory.py relation suchen     ENTITY_NAME
  python db_agentic_memory.py interaktion speichern PROMPT RESPONSE [--entity E] [--projekt P] [--tags T]
  python db_agentic_memory.py kontext  setzen     SCHLUESSEL WERT [--projekt P]
  python db_agentic_memory.py kontext  abrufen    [--projekt P] [--limit N]
  python db_agentic_memory.py export   [--projekt P] [--format json|markdown]
  python db_agentic_memory.py stats
  python db_agentic_memory.py server   [--port 8765]

UMGEBUNGSVARIABLEN:
  MEMORY_DB=memory.db         Pfad zur SQLite-Datenbank (Standard: ./memory.db)
  MEMORY_PROJEKT=default      Standard-Projektname

ENTITÄTS-TYPEN (Konvention):
  function | file | concept | decision | module | api | config | test

RELATIONS-TYPEN (Konvention):
  implementiert | hängt ab von | gehört zu | ruft auf | erbt von
  enthält | verweist auf | ersetzt | erweitert | testet | konfiguriert

BEISPIELE:
  # Datenbank anlegen
  python db_agentic_memory.py init memory.db

  # Entität speichern
  python db_agentic_memory.py entity speichern "parse_invoice" function \\
    "Extracts fields from invoice PDF" --projekt pjc3 --tags "vision,pdf"

  # Beziehung knüpfen
  python db_agentic_memory.py relation speichern "parse_invoice" "implementiert" \\
    "vision_dokument.py" --projekt pjc3

  # Interaktion persistieren
  python db_agentic_memory.py interaktion speichern \\
    "Wie funktioniert der ETL-Prozess?" "Die ETL-Pipeline besteht aus 4 Phasen..." \\
    --entity "csv_etl_pipeline.py" --projekt pjc3

  # Kontext abrufen (Session-Start)
  python db_agentic_memory.py kontext abrufen --projekt pjc3 --limit 30

  # Export als Markdown
  python db_agentic_memory.py export --projekt pjc3 --format markdown > memory.md

  # HTTP-Server starten (für Headless-Agent-Steuerung)
  python db_agentic_memory.py server --port 8765
"""

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HILFE); sys.exit(0)

    args = sys.argv[1:]

    def _opt(name: str, default: str | None = None) -> str | None:
        for i, a in enumerate(args):
            if a == name and i + 1 < len(args):
                return args[i + 1]
        return default

    def _pos(start: int) -> list[str]:
        return [a for a in args if not a.startswith("--")][start:]

    db_pfad = Path(_opt("--db", str(DEFAULT_DB)) or str(DEFAULT_DB))
    projekt = _opt("--projekt", DEFAULT_PROJEKT) or DEFAULT_PROJEKT

    modus = args[0]
    unter = args[1] if len(args) > 1 and not args[1].startswith("--") else ""

    if modus == "init":
        pfad = Path(_pos(1)[0]) if _pos(1) else db_pfad
        modus_init(pfad)

    elif modus == "entity" and unter == "speichern":
        p = _pos(2)
        if len(p) < 3:
            _err("VERWENDUNG: entity speichern NAME TYP BESCHREIBUNG")
        entity_speichern(p[0], p[1], p[2], projekt,
                         _opt("--tags", "") or "", db_pfad)

    elif modus == "entity" and unter == "suchen":
        p = _pos(2)
        if not p:
            _err("VERWENDUNG: entity suchen SUCHBEGRIFF")
        entity_suchen(p[0], _opt("--projekt"), db_pfad)

    elif modus == "entity" and unter == "liste":
        entity_liste(_opt("--projekt"), _opt("--typ"), db_pfad)

    elif modus == "relation" and unter == "speichern":
        p = _pos(2)
        if len(p) < 3:
            _err("VERWENDUNG: relation speichern VON RELATION NACH")
        relation_speichern(p[0], p[1], p[2], projekt,
                           _opt("--beschreibung", "") or "", db_pfad)

    elif modus == "relation" and unter == "suchen":
        p = _pos(2)
        if not p:
            _err("VERWENDUNG: relation suchen ENTITY_NAME")
        relation_suchen(p[0], db_pfad)

    elif modus == "interaktion" and unter == "speichern":
        p = _pos(2)
        if len(p) < 2:
            _err("VERWENDUNG: interaktion speichern PROMPT RESPONSE")
        interaktion_speichern(p[0], p[1],
                              _opt("--entity"),
                              projekt,
                              _opt("--tags", "") or "",
                              db_pfad)

    elif modus == "kontext" and unter == "setzen":
        p = _pos(2)
        if len(p) < 2:
            _err("VERWENDUNG: kontext setzen SCHLUESSEL WERT")
        kontext_setzen(p[0], p[1], projekt, db_pfad)

    elif modus == "kontext" and unter == "abrufen":
        limit = int(_opt("--limit", str(DEFAULT_LIMIT)) or DEFAULT_LIMIT)
        kontext_abrufen(_opt("--projekt"), limit, db_pfad)

    elif modus == "export":
        modus_export(_opt("--projekt"), _opt("--format", "json") or "json", db_pfad)

    elif modus == "stats":
        modus_stats(db_pfad)

    elif modus == "server":
        port = int(_opt("--port", "8765") or "8765")
        modus_server(port, db_pfad)

    else:
        print(f"ERR | Unbekannter Modus: '{modus} {unter}'\n{HILFE}", file=sys.stderr)
        sys.exit(1)
