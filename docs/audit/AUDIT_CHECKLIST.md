# Audit Checklist (Phase 1)

## Zweck
Kompakte Prüfliste für Governance-Audits in Phase 1 (Pre-Flight Router + Skill Guards).

## A. Routing & Intent
- [ ] Jede neue Aufgabe startet mit einem Intent-Token (`[Intent: ...]`).
- [ ] Nur erlaubte Router-Intents werden genutzt (`write_code`, `debug`, `review`, `architecture`, `docs`, `explain`, `ops`).
- [ ] Bei `architecture` wird vor Umsetzung `NOVA_ROADMAP.md` berücksichtigt.

## B. Skill-Zuständigkeit
- [ ] Skill-Zuständigkeiten sind in der Matrix dokumentiert.
- [ ] Verantwortungsgrenzen pro Skill sind klar (inkl. Anti-Pattern).
- [ ] Keine Scope-Überschreitungen zwischen Router, Code, Security und MCP-Konfiguration.

## C. Guard-Compliance
- [ ] `sec-guard` ist bei Code-/Debug-/Review-relevanten Flows aktiv berücksichtigt.
- [ ] `mcp-guard` schützt MCP-Konfiguration und Tool-Verkabelung.
- [ ] `system-health` wird nur Read-Only eingesetzt (keine Config-Schreiboperationen).

## D. Nachvollziehbarkeit
- [ ] Änderungen sind in Git mit klarer Commit-Message dokumentiert.
- [ ] Entscheidungsgrundlagen liegen in `NOVA_ROADMAP.md` und den Skill-Matrizen.
- [ ] Memory-Regeln sind konsistent mit Roadmap und Governance-Dokumenten.

## E. Freigabe für Testarbeiten
- [ ] Completeness-Check für Matrix/Governance ist erfolgreich.
- [ ] Keine offenen kritischen Lücken in Zuständigkeit oder Guarding.
- [ ] Repository-Stand ist sauber dokumentiert und commitbar.
