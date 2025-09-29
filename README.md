# 📚 Arc Crusade Manuscript Assistant

A powerful AI-based manuscript analysis tool with multiple interfaces: **Web App**, **CLI**, and **API**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/sethfiresaid-gif/arc-crusade-ai/main/streamlit_app.py)

## ✨ Features

🔍 **In-Depth Analysis:**
- Automatic outline generation
- Section-based rubric scores + feedback
- Top 10 improvement points identification
- Phased improvement plan
- Rewrite suggestions per section
- Timeline extraction + consistency check

📊 **Interactive Reports:**
- Text statistics and visualizations
- Downloadable reports (MD, JSON, ZIP)
- Real-time progress tracking
- Section-based filtering

🤖 **AI Provider Support:**
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo
- **Ollama**: Llama3.1, Mistral, CodeLlama (local)

📁 **File Formats:**
- `.txt` - Plain text
- `.md` - Markdown  
- `.docx` - Microsoft Word

## 🚀 Quick Start

### 🌐 Web App (Recommended)
**Use the live web app:** [Arc Crusade Manuscript Assistant](https://share.streamlit.io/sethfiresaid-gif/arc-crusade-ai/main/streamlit_app.py)

No installation needed! Simply upload your manuscript and get instant feedback.

### 💻 Local Installation
```bash
# Clone repository
git clone https://github.com/sethfiresaid-gif/Arc-Crusade-AI.git
cd Arc-Crusade-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start web interface
streamlit run streamlit_app.py
```

### 🔑 API Configuration
Create a `.env` file or configure Streamlit secrets:
```bash
# .env file
OPENAI_API_KEY=sk-your-openai-api-key-here
```

For Streamlit Cloud deployment, add secrets in your app settings.

### 🖥️ Usage Options

#### Web Interface (Streamlit)
```bash
streamlit run streamlit_app.py
```
Then open `http://localhost:8501` in your browser.

#### Command Line Interface
```bash
# Analyze a single file
python cli_manuscript_assistant.py manuscript.txt

# Multiple files with specific model
python cli_manuscript_assistant.py chapter1.txt chapter2.txt --model gpt-4o-mini

# Skip rewrites for faster processing
python cli_manuscript_assistant.py manuscript.docx --no-rewrite
```

#### API Server
```bash
# Start API server
python api.py

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

## 📊 Analysis Features

### 🎭 **Character Analysis**
- Character development tracking
- Emotional arc analysis  
- Voice consistency checking
- Character interaction mapping

### ⚡ **Pacing Analysis**
- Scene rhythm evaluation
- Action vs description balance
- Tension curve analysis
- Dialogue pacing optimization

### 🎨 **Style Analysis**
- Show vs tell ratio
- Weak verb identification
- Adverb usage patterns
- Repetition detection
- Passive voice analysis

### 📖 **Genre-Specific Feedback**
Optimized analysis for:
- Fantasy - Worldbuilding, magic systems
- Thriller - Tension, pacing, suspense
- Romance - Emotional connection, chemistry
- Mystery - Clue placement, revelations
- Sci-Fi - Technology integration, concepts
- Historical - Period accuracy, atmosphere
- Literary - Prose quality, themes

### 🕒 **Timeline Consistency**
- Time marker extraction
- Chronology validation
- Consistency checking
- Timeline visualization

## 📁 OneDrive Integration

Automatic cloud storage with Zapier compatibility:
- Saves analysis results to OneDrive
- Organized folder structure
- ZIP archives for complete reports
- Seamless workflow integration

## 🔧 Streamlit Cloud Deployment

### Step 1: Fork this repository
1. Click "Fork" at the top of this GitHub page
2. Clone your fork locally

### Step 2: Configure Streamlit Secrets
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Create new app with your fork
3. Go to **Settings** → **Secrets**
4. Add:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_ORG_ID = "org-your-org-id"     # Optional
OPENAI_PROJECT = "proj-your-project"   # Optional
```

### Step 3: Deploy
- Select `streamlit_app.py` as main file
- Click **Deploy**
- Your app will be live within 2-3 minutes! 🎉

## 🛠️ Development

### Project Structure
```
Arc-Crusade-AI/
├── cli_manuscript_assistant.py    # Core analysis engine
├── streamlit_app.py              # Web interface
├── enhanced_analysis.py          # Advanced analysis functions
├── onedrive_integration.py       # Cloud storage
├── api.py                        # FastAPI server
├── requirements.txt              # Dependencies
└── outputs/                      # Analysis results
```

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/sethfiresaid-gif/Arc-Crusade-AI/issues)
- **Documentation**: See project wiki for detailed guides
- **Updates**: Watch the repository for new features

## 🎯 Use Cases

- **✍️ Writers**: Structural feedback on manuscripts
- **📝 Editors**: Consistent analysis criteria
- **👥 Beta Readers**: Structured feedback tools
- **📚 Writing Groups**: Shared analysis standards

## 🔮 Roadmap

- [ ] Advanced plotting structure analysis
- [ ] Multi-language support
- [ ] Collaborative editing features
- [ ] Publishing workflow integration
- [ ] Advanced genre-specific templates

---

**Built with ❤️ for writers by writers**

Success with your manuscript! 🚀📚
