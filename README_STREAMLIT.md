# 📚 Arc Crusade Manuscript Assistant - Streamlit App

Een AI-gebaseerde manuscript analyse tool gebouwd met Streamlit.

## 🚀 Live Demo

[Open de app op Streamlit Community Cloud](https://share.streamlit.io/yourusername/arc-crusade-ai)

## ✨ Features

- 📝 **Manuscript Analyse**: Automatische outline generatie en sectie-analyse
- 🔍 **Stijlfeedback**: Gedetailleerde rubrieken per hoofdstuk
- ⚡ **AI-Powered**: Ondersteunt OpenAI en Ollama modellen
- 📊 **Visualisaties**: Interactieve grafieken en statistieken
- 📥 **Export**: Download rapporten in MD, JSON en ZIP formaten
- 🕒 **Tijdlijn Analyse**: Consistentie controle van verhaallijnen

## 🛠️ Lokale Installation

```bash
# Clone repository
git clone https://github.com/yourusername/arc-crusade-ai.git
cd arc-crusade-ai

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run locally
streamlit run streamlit_app.py
```

## 🔧 Configuratie

### Environment Variables

- `OPENAI_API_KEY`: Je OpenAI API sleutel
- `OPENAI_ORG_ID`: (Optioneel) Je OpenAI organizatie ID
- `OPENAI_PROJECT`: (Optioneel) Je OpenAI project ID

### Ondersteunde Bestanden

- `.txt` - Platte tekst bestanden
- `.md` - Markdown bestanden  
- `.docx` - Microsoft Word documenten

## 📱 Gebruik

1. **Upload**: Sleep je manuscript bestanden naar de upload zone
2. **Configureer**: Kies je AI provider en model in de sidebar
3. **Analyseer**: Klik op "Analyseer Manuscript" 
4. **Download**: Krijg gedetailleerde rapporten en suggesties

## 🎯 Use Cases

- **Schrijvers**: Krijg feedback op manuscript structuur en stijl
- **Editors**: Identificeer verbeterpunten en inconsistenties
- **Beta Readers**: Gestructureerde feedback op verhalen
- **Writing Groups**: Consistente analyse criteria

## 🤝 Contributing

Pull requests zijn welkom! Voor grote wijzigingen, open eerst een issue.

## 📄 License

MIT License - zie [LICENSE](LICENSE) bestand voor details.