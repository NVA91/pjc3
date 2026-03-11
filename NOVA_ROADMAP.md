# Nova Universe: Architektur & Vision
Dieses Dokument ist die Single Source of Truth für die Evolution dieses Agenten-Frameworks.

## Phase 1: Kalibrierung 
- **Ansatz:**  Integrierter Router-Skill in der Claude CLI.
- **Ziele:** Intent-Detection stabilisieren, Skill-Definitionen schärfen, Output-Formate für den Dispatcher testen.
- **Fokus:** Schnelles Feedback-Loop, schnelles Prototyping (z.B. FastMCP Türsteher anbinden).

## Phase 2: Nova Framework 
- **Ansatz:** Eigener Python-Orchestrator / CLI-Eingang.
- **Trigger:** Sobald die Skill-Typen stabil sind und Bedarf an Logging, Metriken oder Multi-Model-Routing entsteht.
- **Architektur:** Router wird als eigener, kostengünstiger API-Service/CLI ausgelagert. Er klassifiziert den Intent und startet erst dann den 'teuren' Coding-Agenten (Claude) mit exakt passendem Kontext.

## Phase 3: Nova Universe (Zukunft / Langfristig)
- **Vision:** Ein vollautonomes, lokales Agenten-Ökosystem. 100% Offline-Fähigkeit für sensible Daten, eigene Memory-Graphen pro Projekt, nahtlose Automatisierung über n8n und lokale FastMCP-Gateways.
