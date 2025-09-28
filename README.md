# Arc Manuscript Assistant (CLI + FastAPI)

Een lichte AI-analysetool voor manuscripten (DOCX/MD/TXT) met:
- Outline (bullets)
- Rubriek-scores + motivatie
- Top 10 issues
- Gefaseerd verbeterplan
- Korte herschrijfsuggesties per sectie
- Tijdlijn-extractie + consistentie-advies
- Exports: Markdown + JSON (+ losse rewrites)

## 1) Installatie
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Modellen
- **Lokaal**: [Ollama](https://ollama.com/) (bijv. `llama3.1`)
- **Cloud**: OpenAI-compatibel. Zet `OPENAI_API_KEY` in je omgeving of `.env`.

`.env` voorbeeld:
```
OPENAI_API_KEY=sk-...
OPENAI_BASE= # optioneel: eigen endpoint
ARC_API_KEY=change-me
```

## 2) CLI gebruiken (aanbevolen voor jou)
```bash
python cli_manuscript_assistant.py pad/naar/manuscript.docx --provider ollama --model llama3.1
# of
OPENAI_API_KEY=sk-... python cli_manuscript_assistant.py pad/naar/manuscript.docx --provider openai --model gpt-4o-mini
```
Outputs komen in `outputs/`:
- `report-YYYYMMDD-HHMMSS.md`
- `results-YYYYMMDD-HHMMSS.json`
- `outputs/rewrites/*.md`

## 3) API (voor later delen met klanten)
Start lokaal:
```bash
python api.py
# draait op http://127.0.0.1:8000
```
POST `/analyze` (multipart form):
- `file`: upload
- `provider`: `ollama` of `openai`
- `model`: bijv. `llama3.1` of `gpt-4o-mini`
- `rewrites`: `true`/`false`

### Beveiliging
Zet `ARC_API_KEY` in je `.env`. Elke request moet header `X-ARC-KEY` meesturen.

## 4) Config uitbreiden
- `config/genre_profiles.json`: extra regels per genre (worden in prompts geïnjecteerd).
- `config/forbidden_terms.txt`: lijst met verboden/cliché-termen of regex.

Succes!
