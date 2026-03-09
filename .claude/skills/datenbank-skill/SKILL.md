---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: datenbank-skill
description: >
  MCP-basierte Datenbankintegration: PostgreSQL-Schema-Exploration ohne Token-Overload,
  Read-Only MCP-Konfiguration (DROP TABLE / DELETE via Protokoll blockiert),
  Schreiboperationen ausschließlich als Flyway-Migrationsdateien (nie direkt ausführen),
  SQLite als Agentic-Memory-Backend (Langzeitpersistenz über Session-Grenzen hinweg),
  lokaler HTTP-Server + Headless-Agent + SQLite-MCP-Server für Entitäten und Kontextbeziehungen.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Datenbank
    description: >
      MCP-basierte Datenbankintegration: PostgreSQL-Schema-Exploration ohne Token-Overload,
      Read-Only MCP-Konfiguration (DROP TABLE / DELETE via Protokoll blockiert),
      Schreiboperationen ausschließlich als Flyway-Migrationsdateien (nie direkt ausführen),
      SQLite als Agentic-Memory-Backend (Langzeitpersistenz über Session-Grenzen hinweg),
      lokaler HTTP-Server + Headless-Agent + SQLite-MCP-Server für Entitäten und Kontextbeziehungen

triggers:
  # Datenbank / MCP-Datenbankintegration / Agentic Memory
  - PostgreSQL-Schema über MCP-Server iterativ inspizieren (kein Token-Overload)
  - SELECT-Abfragen strukturiert über MCP-Tools senden (kein Klartext-Credential)
  - MCP-Host verwaltet physische Datenbankverbindung; Agent sendet nur Requests
  - SQLite als Agentic-Memory-Backend einrichten
  - Langzeitgedächtnis für Agenten jenseits des Kontextfensters implementieren
  - Lokalen HTTP-Server zur Steuerung einer Headless-Agent-Session aufbauen
  - Entitäten und kontextuelle Beziehungen in SQLite-MCP-Server speichern
  - Historischen Kontext aus früheren Sessions abrufen und weiterverwenden
  - MCP-Server auf Read-Only konfigurieren (DROP TABLE / DELETE verhindern)
  - Schreiboperationen als SQL-Migrationsdatei generieren statt direkt ausführen
  - Flyway/Liquibase-Migrationsskripte für Schema-Änderungen erzeugen
  - SQL-Migration mit Rollback-Kommentar und Idempotenz-Pattern erstellen
  - CI/CD-Pipeline für sichere Datenbankmigrationen einrichten (Staging → Prod)
  - CREATE INDEX CONCURRENTLY ohne Table-Lock auf Produktionstabellen

resources:
  - resources/db_agentic_memory.py
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

## Datenbankintegration, Schemaverwaltung und Agentic Memory

KI-Agenten greifen über das **Model Context Protocol (MCP)** sicher auf relationale und
nicht-relationale Datenbanken zu — ohne Klartext-Credentials im Kontextfenster und ohne
das gesamte Datenbankschema auf einmal laden zu müssen.

### Architektur: MCP als intelligente Abstraktionsschicht

```
Agent (Modell)
    │  strukturierte Requests (MCP-Protokoll)
    ▼
MCP-Server (z.B. postgres-mcp, sqlite-mcp)
    │  physische Datenbankverbindung (verwaltet vom MCP-Host)
    ▼
Datenbank (PostgreSQL / SQLite / andere)
```

**Kernprinzip:**
- **MCP-Host** (Client-Applikation) verwaltet die physische Datenbankverbindung
- **Agent** sendet ausschließlich strukturierte Requests an die MCP-Tools
- Credentials verbleiben im MCP-Host — niemals im Agenten-Kontext

### PostgreSQL-Integration: Iterative Schema-Exploration

Der Agent inspiziert das Datenbankschema iterativ, um den Token-Overhead zu minimieren.
Niemals das gesamte Schema auf einmal laden — stattdessen:

```
Schritt 1: Tabellenliste holen
  MCP-Tool: list_tables → ["users", "orders", "products", ...]

Schritt 2: Relevante Tabellen selektiv inspizieren
  MCP-Tool: get_schema("orders") →
    { columns: [{name: "id", type: "uuid", pk: true}, ...],
      indexes: [...], foreign_keys: [...] }

Schritt 3: Gezielte SELECT-Abfrage konstruieren
  MCP-Tool: execute_query("SELECT o.id, u.email, o.total
                           FROM orders o JOIN users u ON o.user_id = u.id
                           WHERE o.created_at > NOW() - INTERVAL '7 days'
                           LIMIT 100")
```

**Ablaufregeln für PostgreSQL-Abfragen:**

| Regel | Begründung |
|---|---|
| Nur SELECT (kein INSERT/UPDATE/DELETE) | Read-Only-Sicherheit; Schreiboperationen nur nach expliziter Freigabe |
| LIMIT immer setzen (max. 1.000) | Verhindert Token-Explosion durch große Result-Sets |
| Schema iterativ erkunden (Tabelle für Tabelle) | Kein Token-Overload durch Bulk-Schema-Import |
| Keine Credentials im Prompt | MCP-Host verwaltet Connection-String; Agent kennt ihn nicht |
| Abfrage-Ergebnis als JSON nach stdout | Standardisiertes Format für ETL-Pipeline-Weitergabe |

### SQLite als Agentic Memory — Langzeitgedächtnis

SQLite ermöglicht persistentes Agenten-Gedächtnis über Session-Grenzen hinweg.
Nach dem Ende des Kontextfensters bleibt das Wissen in der Datenbank erhalten.

**Architektur: Lokaler HTTP-Server + Headless-Agent + SQLite-MCP-Server**

```
Entwickler / Orchestrierer
    │  HTTP-Request (POST /task)
    ▼
Lokaler HTTP-Server (Python/FastAPI)
    │  startet Headless-Agent-Session
    ▼
Claude Code (headless, --print)
    │  MCP-Protokoll
    ▼
SQLite-MCP-Server
    │  SQL
    ▼
SQLite-Datenbank (memory.db)
    ├── entities     (Projektentitäten: Dateien, Funktionen, Konzepte)
    ├── relations    (Kontextbeziehungen: "gehört zu", "implementiert", "hängt ab von")
    ├── interactions (Interaktionshistorie: Zeitstempel, Prompt, Response, Tags)
    └── context      (Abrufbarer Kontext: Session-übergreifende Fakten)
```

**Speicher-Operationen:**

```python
# Entität speichern (z.B. neue Funktion entdeckt)
mcp.execute("INSERT INTO entities (name, type, description, project)
             VALUES ('parse_invoice', 'function', 'Extracts fields from invoice PDF', 'pjc3')")

# Beziehung knüpfen
mcp.execute("INSERT INTO relations (from_entity, relation, to_entity)
             VALUES ('parse_invoice', 'implementiert', 'vision_dokument.py')")

# Historischen Kontext abrufen (neue Session)
mcp.execute("SELECT e.name, e.description, i.response
             FROM entities e JOIN interactions i ON e.name = i.entity
             WHERE e.project = 'pjc3'
             ORDER BY i.created_at DESC LIMIT 20")
```

**Agentic-Memory-Workflow:**

```
Session 1: Agent analysiert Codebase
  → Entitäten extrahieren (Funktionen, Module, Konzepte)
  → Beziehungen in SQLite speichern
  → Interaktionshistorie persistieren
  Context-Window endet → SQLite-DB bleibt erhalten

Session 2 (neue Session, leeres Context-Window):
  → Relevante Entitäten und Relationen aus SQLite laden
  → Historischen Kontext rekonstruieren
  → Agent arbeitet mit vollständigem Projektwissen
  → Neue Erkenntnisse werden zurückgeschrieben
```

### Datenbank-Sicherheit: Read-Only-Konfiguration und Schreiboperationen via CI/CD

Sicherheitsaspekte spielen bei der Agenten-Datenbank-Interaktion eine übergeordnete Rolle.
Der Architekturansatz setzt auf mehrere Schutzschichten, um destruktive Aktionen zu verhindern.

#### Read-Only MCP-Konfiguration — Primärer Schutz

MCP-Server für relationale Datenbanken werden **primär auf schreibgeschützte Abfragen** konfiguriert.
Protokollbasierte und kryptografische Schranken verhindern unbeabsichtigte destruktive Aktionen:

| Bedrohung | Ursache | MCP-Schutz |
|---|---|---|
| `DROP TABLE` | Halluzination oder Prompt-Injection | MCP-Server: `allowed_operations: [SELECT]` — DDL blockiert |
| Unautorisiertes `DELETE` | Fehlerhafte WHERE-Klausel, falscher Kontext | DML-Whitelist: nur SELECT zugelassen |
| Daten-Exfiltration | `SELECT * FROM users` ohne LIMIT | Result-Size-Limit im MCP-Server (z. B. `max_rows: 1000`) |
| Credential-Leak | Connection-String im Prompt | MCP-Host verwaltet Credentials — Agent sieht sie nie |

**MCP-Server-Konfiguration (postgres-mcp — Beispiel):**

```json
{
  "allowed_operations": ["SELECT"],
  "max_rows": 1000,
  "schema_exploration": true,
  "write_operations": false,
  "ddl_operations": false
}
```

> **Pflicht:** Der Agent darf niemals versuchen, MCP-Sicherheitsschranken zu umgehen
> (z.B. durch SQL-Injection-Techniken gegen den MCP-Server selbst oder durch
> Formulierung von DELETE als verschachtelte SELECT-Subqueries wo möglich).
> Bei verweigertem Zugriff: Nutzer informieren, nicht eskalieren.

#### Schreiboperationen via Migrationsdateien — Einziger erlaubter Write-Weg

Sind Schreiboperationen (Schema-Migrationen, Daten-Korrekturen) zwingend notwendig,
**generiert der Agent ausschließlich SQL-Code als Textdatei** — er führt ihn niemals direkt aus.

**Migrations-Datei-Namenskonvention (Flyway-Standard):**

```
migrations/
├── V1__create_users_table.sql        # Erstellt Tabelle
├── V2__add_email_index.sql           # Fügt Index hinzu
├── V3__add_created_at_column.sql     # Fügt Spalte hinzu (nicht nullable mit DEFAULT)
└── R__refresh_materialized_views.sql # Repeatable Migration (immer neu ausführen)
```

**Pflicht-Inhalte einer Migrations-Datei (Agent muss alle generieren):**

```sql
-- Migration: V3__add_created_at_column.sql
-- Zweck:     Zeitstempel-Spalte für Audit-Trail in orders-Tabelle
-- Autor:     Claude Code (generiert, nicht ausgeführt)
-- Erstellt:  2026-03-09
-- Review:    Pflichtfeld — vor CI/CD-Ausführung durch Entwickler prüfen
--
-- RÜCKGÄNGIG MACHEN:
--   ALTER TABLE orders DROP COLUMN IF EXISTS created_at;

BEGIN;

-- Neue Spalte mit DEFAULT (verhindert NOT NULL Constraint-Fehler bei bestehenden Zeilen)
ALTER TABLE orders
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Index für Datumsbereichs-Abfragen
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at
  ON orders(created_at DESC);

-- Verifikation (Agent zeigt Erwartungswert)
-- ERWARTUNG: 0 Zeilen ohne created_at
-- SELECT COUNT(*) FROM orders WHERE created_at IS NULL;

COMMIT;
```

**Kritische Regeln für Migrations-SQL (Agent muss einhalten):**

| Regel | SQL-Pattern | Grund |
|---|---|---|
| `ADD COLUMN IF NOT EXISTS` | `ALTER TABLE t ADD COLUMN IF NOT EXISTS c TYPE` | Idempotent — wiederholbar ohne Fehler |
| `NOT NULL` immer mit `DEFAULT` | `NOT NULL DEFAULT 'wert'` | Bestehende Zeilen nicht blockieren |
| `CREATE INDEX CONCURRENTLY` | `CREATE INDEX CONCURRENTLY IF NOT EXISTS` | Kein Table-Lock auf Produktionstabellen |
| `BEGIN; ... COMMIT;` | Transaktion wrappen | Rollback bei Fehler automatisch |
| Rollback-Kommentar pflicht | `-- RÜCKGÄNGIG MACHEN: DROP COLUMN ...` | Entwickler kennt Undo-Weg |
| Nur eine Änderung pro Datei | 1 `ALTER TABLE` pro Migration | Atomare, nachvollziehbare Änderungen |

#### Vollständiger Sicherheits-Entscheidungsbaum

```
Agent erhält Datenbankaufgabe
    │
    ├── Aufgabe = Daten lesen / analysieren?
    │   → SELECT via MCP-Tool (Read-Only)
    │   → LIMIT setzen → Ergebnis nach stdout
    │
    ├── Aufgabe = Schema inspizieren?
    │   → list_tables → get_schema (iterativ, Tabelle für Tabelle)
    │   → Kein Bulk-Import
    │
    ├── Aufgabe = Daten schreiben / Schema ändern?
    │   → SQL-Migrationsdatei generieren (Flyway-Konvention)
    │   → Nutzer zur Prüfung auffordern
    │   → Datei im migrations/-Verzeichnis ablegen
    │   → CI/CD-Pipeline informieren (niemals selbst ausführen)
    │
    └── Aufgabe = Credentials abfragen / Connection-String anzeigen?
        → VERWEIGERN — Credentials verbleiben im MCP-Host
        → Nutzer informieren: Credentials sind MCP-Host-Verantwortung
```

### Pflicht-Ablauf für Datenbankjobs

1. **Zugang prüfen** — MCP-Server verfügbar? (`list_tables` als Connectivity-Test)
2. **Schema iterativ erkunden** — Nur benötigte Tabellen inspizieren (niemals Bulk-Import)
3. **Read-Only zuerst** — SELECT konstruieren, Ergebnis validieren, bevor Schreib-Ops
4. **Token-Kontrolle** — LIMIT setzen; Result > 500 Zeilen → Zusammenfassung statt Raw-Dump
5. **Schreib-Ops als Migration** — SQL als Datei generieren, niemals direkt ausführen
6. **Memory-Persistenz** — Neue Erkenntnisse sofort in SQLite schreiben (nicht am Session-Ende)

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
| `resources/db_agentic_memory.py` | 3 | Datenbank | SQLite Agentic Memory: Entitäten/Relationen/Interaktionen persistieren + HTTP-Server-Modus |
