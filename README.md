# 📚 Arc Crusade Manuscript Assistant

Een krachtige AI-gebaseerde analysetool voor manuscripten met meerdere interfaces: **Web App**, **CLI**, en **API**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yourusername/arc-crusade-ai/main/app.py)

## ✨ Features

🔍 **Diepgaande Analyse:**
- Automatische outline generatie
- Sectie-gebaseerde rubriek scores + feedback
- Top 10 verbeterpunten identificatie
- Gefaseerd verbeterplan
- Herschrijfsuggesties per sectie
- Tijdlijn extractie + consistentie controle

📊 **Interactieve Rapporten:**
- Tekst statistieken en visualisaties
- Downloadbare reports (MD, JSON, ZIP)
- Real-time progress tracking
- Sectie-gebaseerde filtering

🤖 **AI Provider Support:**
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo
- **Ollama**: Llama3.1, Mistral, CodeLlama (lokaal)

📁 **Bestandsformaten:**
- `.txt` - Platte tekst
- `.md` - Markdown  
- `.docx` - Microsoft Word

## 🚀 Quick Start

### 🌐 Web App (Aanbevolen)
**Gebruik de live web app:** [Arc Crusade Manuscript Assistant](https://share.streamlit.io/yourusername/arc-crusade-ai/main/app.py)

Geen installatie nodig! Upload gewoon je manuscript en krijg direct feedback.

### 💻 Lokale Installatie
```bash
# Clone repository
git clone https://github.com/yourusername/arc-crusade-ai.git
cd arc-crusade-ai

# Maak virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt

# Start web interface
streamlit run app.py
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

## 🔧 Streamlit Cloud Deployment

### Stap 1: Fork dit repository
1. Klik "Fork" bovenaan deze GitHub pagina
2. Clone je fork lokaal

### Stap 2: Configureer Streamlit Secrets
1. Ga naar [share.streamlit.io](https://share.streamlit.io)
2. Maak nieuwe app met je fork
3. Ga naar **Settings** → **Secrets**
4. Voeg toe:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_ORG_ID = "org-your-org-id"     # Optioneel
OPENAI_PROJECT = "proj-your-project"   # Optioneel
```

### Stap 3: Deploy
- Selecteer `app.py` als main file
- Klik **Deploy**
- Je app is live binnen 2-3 minuten! 🎉

## 🤝 Contributing

Pull requests zijn welkom! Voor grote wijzigingen, open eerst een issue om te bespreken wat je wilt veranderen.

1. Fork het project
2. Maak een feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit je wijzigingen (`git commit -m 'Add some AmazingFeature'`)
4. Push naar de branch (`git push origin feature/AmazingFeature`)
5. Open een Pull Request

## 📄 License

Dit project is gelicenseerd onder de MIT License - zie het [LICENSE](LICENSE) bestand voor details.

## 🎯 Use Cases

- **✍️ Schrijvers**: Structurele feedback op manuscripten
- **📝 Editors**: Consistente analyse criteria
- **👥 Beta Readers**: Gestructureerde feedback tools
- **📚 Writing Groups**: Gedeelde analyse standaarden

## 🔮 Roadmap

- [ ] Meer AI providers (Claude, Gemini)
- [ ] Character arc analysis
- [ ] Plot hole detection
- [ ] Genre-specific templates
- [ ] Collaborative editing
- [ ] Multi-language support

---

**Gemaakt met ❤️ voor schrijvers door schrijvers**

Succes met je manuscript! 🚀📚
