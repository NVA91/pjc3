# core.md — Zentraler Router

**Jeder Agent liest diese Datei zuerst.**

---

## Pyramide

```
pjc3/  ← EINZIGE Steuerzentrale
├── pjc3-docker/  → Verwalter: .claude/agents/verwalter.md
└── pjc3-viz1/    → Verwalter: .claude/agents/verwalter.md
```

Kein Agent greift direkt über Repo-Grenzen. Änderungen in Sub-Repos → Ticket an Verwalter.

---

## Zuständigkeiten

| Bereich | Zuständig | Wo |
|---|---|---|
| Claude API, MCP, Chatbots | pjc3 direkt | dieses Repo |
| Home-Infrastruktur, Docker | pjc3-docker Verwalter | `/home/ubhp-nova/claude-c/pjc3-docker/` |
| PDF-Analyse, Streamlit | pjc3-viz1 Verwalter | `/home/ubhp-nova/claude-c/pjc3-viz1/` |
| Langzeitgedächtnis | doc-agent | `.claude/agents/doc-agent.md` |

---

## Ticket-System (Cross-Repo)

Wenn pjc3 etwas in einem Sub-Repo ändern will:

```
TICKET
  Von: pjc3
  An: [pjc3-docker|pjc3-viz1] Verwalter
  Aufgabe: <exakte Beschreibung>
  Dateien: <betroffene Dateien>
  Erwartetes Ergebnis: <Verifikationskriterium>
```

Der Verwalter entscheidet ob das Ticket REGEL.md-konform ist. Bei Konflikt: sofortiger Abbruch.

---

## Langzeitgedächtnis — Kategorien

→ [`/memory/MEMORY.md`](/home/ubhp-nova/.claude/projects/-home-ubhp-nova-claude-c-pjc3/memory/MEMORY.md)

| Kategorie | Dateipräfix | Inhalt |
|---|---|---|
| Projekt-Status | `project_` | Offene Aufgaben, Repo-Status |
| Hierarchie & Routing | `arch_` | Pyramide, Verwalter, Direktiven |
| Skills & Konfiguration | `reference_skills_` | Skill-Pfade, Standards |
| Referenz & Best Practices | `reference_` | Bewährte Muster |

**Regel:** Temporäre Arbeitsvermerke werden nach Aufgabenabschluss gelöscht. Nur finaler Bericht bleibt.

---

## Abbruch-Befehl

Unklarheit → **STOP** → User melden. Kein Raten. Keine Workarounds.
