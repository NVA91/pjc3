# Audit Runbook (Phase 1)

## Ziel
Schneller, reproduzierbarer Ablauf für interne Governance-Audits vor Testarbeiten.

## 1) Vorbereitung
1. Projektstatus prüfen (`git status`).
2. Governance-Dokumente aktualitätsprüfen (`NOVA_ROADMAP.md`, Skill-Matrizen, `CLAUDE.md`).
3. Sicherstellen, dass kritische Regeln im Memory vorhanden sind.

## 2) Durchführung
1. Routing prüfen: Intent-Token wird als erste Zeile ausgegeben.
2. Architekturfall simulieren: Verifikation, dass zuerst `NOVA_ROADMAP.md` referenziert wird.
3. Guard-Verhalten prüfen:
   - Codefluss → `sec-guard`
   - MCP-Konfiguration → `mcp-guard`
   - Diagnosefluss → `system-health` (Read-Only)
4. Matrix-Completeness prüfen (alle Kernskills vorhanden).

## 3) Ergebnisbewertung
- **Pass**: Keine Lücken in Zuständigkeit, Guarding oder Dokumentation.
- **Warnung**: Inkonsistenzen in Matrix/Roadmap/Memory müssen vor Tests behoben werden.
- **Fail**: Fehlende Kernartefakte oder gebrochene Guard-Regeln.

## 4) Abschluss
1. Findings und Maßnahmen kurz dokumentieren.
2. Änderungen in einem nachvollziehbaren Commit bündeln.
3. Repository für Testarbeiten freigeben.

## Definition of Done
- Audit-Dokumente aktuell
- Governance vollständig
- Commit erstellt
- Team kann testgetrieben weiterarbeiten
