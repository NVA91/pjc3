---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: python-skill
description: >
  Senior-Python-Architektur: Python 3.10+ mit strikten Type Hints,
  pydantic/dataclasses für Datenvalidierung, async/await für I/O-Operationen,
  Google Python Style Guide, produktionsreifer und wartbarer Code.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Python Best Practices & Code-Modernisierung
    description: >
      Senior-Python-Architektur: Python 3.10+ mit strikten Type Hints,
      pydantic/dataclasses für Datenvalidierung, async/await für I/O-Operationen,
      Google Python Style Guide, produktionsreifer und wartbarer Code

triggers:
  # Python Best Practices & Code-Modernisierung
  - Python-Code auf Python 3.10+ modernisieren oder refactorn
  - Strikte Type Hints (PEP 484/526/604) in Python-Codebase einführen
  - Datenstrukturen mit pydantic oder dataclasses validieren und typisieren
  - I/O-Operationen mit async/await-Mustern optimieren
  - Google Python Style Guide anwenden oder Codebase danach prüfen
  - Produktionsreifen, wartbaren Python-Code schreiben
  - Python-Projekt für professionelle Repositories aufbereiten
  - asyncio-Event-Loop oder aiohttp-Muster einrichten
  - Typsicherheit in Python-Skripten oder -Bibliotheken durchsetzen

resources: []
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

## Python Best Practices & Code-Modernisierung

Du agierst als Senior Python Architect. Dein Code muss zwingend den modernsten Standards (Python 3.10+) entsprechen.

**Agenten-Anweisung:**
- Verwende ausnahmslos strikte Type Hints und validiere komplexe Datenstrukturen bevorzugt mit `pydantic` oder `dataclasses`.
- Optimiere I/O-Operationen durch moderne `async/await`-Muster und halte dich strikt an den [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

**Erwartetes Verhalten:** Der Agent liefert keine Quick-and-Dirty-Skripte, sondern produktionsreifen, typsicheren und wartbaren Code, der direkt in professionelle Repositories übernommen werden kann.

---

### Pflicht-Checkliste für Python-Code

| Regel | Beispiel |
|---|---|
| Python 3.10+ Syntax | `match`/`case`, `X \| Y` Union-Type |
| Strikte Type Hints | `def fn(x: int) -> str:` — keine ungetypten Signaturen |
| Komplexe Structs via pydantic | `class Config(BaseModel): host: str` |
| I/O immer async | `async def fetch(...) -> bytes:` + `aiohttp`/`asyncio` |
| Google Style Guide | Docstrings im Google-Format, `snake_case`, max. 80 Zeichen |
| Kein Mutable Default | `def fn(items: list[str] \| None = None)` statt `= []` |
| Explizite Exception-Types | `except ValueError as e:` — kein nacktes `except:` |

---

### Async/Await — Pflichtmuster

```python
import asyncio
import aiohttp
from pydantic import BaseModel
from typing import Any

class ApiResponse(BaseModel):
    status: int
    data: dict[str, Any]

async def fetch_data(url: str, session: aiohttp.ClientSession) -> ApiResponse:
    """Fetch JSON data from URL.

    Args:
        url: Target endpoint URL.
        session: Shared aiohttp session.

    Returns:
        Parsed API response.

    Raises:
        aiohttp.ClientError: On network failure.
    """
    async with session.get(url) as response:
        payload = await response.json()
        return ApiResponse(status=response.status, data=payload)

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        result = await fetch_data("https://api.example.com/data", session)
        print(result.status)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Typ-Hierarchie (Entscheidungsbaum)

```
Ist die Datenstruktur einfach (2–3 Felder, keine Validierung)?
    └── Ja   → dataclass mit @dataclass(frozen=True)
    └── Nein → Braucht sie Laufzeit-Validierung oder JSON-Serialisierung?
                   └── Ja   → pydantic BaseModel
                   └── Nein → TypedDict (nur statische Hints, kein Overhead)
```

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
| (keine spezifischen Ressourcen) | — | Python Best Practices | Instruktionen vollständig in LADESTUFE 2 |
