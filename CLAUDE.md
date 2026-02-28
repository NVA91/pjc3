# CLAUDE.md — Projekt pjc3

## Zweck
Claude API Lernprojekt — Experimente mit Anthropic SDK (Chatbots, Notebooks, Skripte).

## Techstack
- Python + venv (`./venv/`) — aktivieren: `source venv/bin/activate`
- Deps: `anthropic`, `jupyter`, `python-dotenv`
- API-Key: `ANTHROPIC_API_KEY` in `.env` (wird via python-dotenv geladen)
- Standardmodell: `claude-sonnet-4-6`

## Projektstruktur
- `01_getting_started.ipynb`, `02_messages_format.ipynb` — Lernnotebooks
- `nova_claude.py` — Streaming-Chatbot (Hauptskript)
- `chatbot.py` — Einfacher Multi-Turn-Chatbot
- `generate_questions.py` — Fragengenerator mit stop_sequences

## Befehle
- `python nova_claude.py` — Streaming-Chatbot starten
- `python chatbot.py` — Einfachen Chatbot starten
- `python generate_questions.py` — stop_sequences Demo starten
- `jupyter notebook` — Notebooks öffnen

## Hinweise
- Nur `generate_questions.py` ruft `load_dotenv()` auf — bei den anderen Skripten muss `ANTHROPIC_API_KEY` bereits in der Shell gesetzt sein (z.B. via `export ANTHROPIC_API_KEY=...` oder `.env` manuell sourcen)
- Nach freshly Clone: `git remote set-head origin main` ausführen (wird von `/security-review` und ähnlichen Skills benötigt)
