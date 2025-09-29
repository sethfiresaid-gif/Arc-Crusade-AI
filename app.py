#!/usr/bin/env python3
"""
Streamlit Web Interface voor Arc Crusade Manuscript Assistant
Versie voor Streamlit Community Cloud deployment
"""
import streamlit as st
import os
import json
import time
from pathlib import Path
import zipfile
import io
from datetime import datetime

# Import onze bestaande functies
from cli_manuscript_assistant import (
    call_model, read_file, split_sections, rough_metrics,
    p_outline, p_rubric, p_short_rewrite, p_top_issues, p_plan,
    p_timeline_feedback, extract_time_markers, OUTPUT_DIR
)

# Page config
st.set_page_config(
    page_title="📚 Arc Crusade Manuscript Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load secrets voor Streamlit Cloud
def load_api_credentials():
    """Load API credentials from Streamlit secrets or environment"""
    try:
        # Try Streamlit secrets first (voor cloud deployment)
        if hasattr(st, 'secrets'):
            openai_key = st.secrets.get("OPENAI_API_KEY", "")
            openai_org = st.secrets.get("OPENAI_ORG_ID", "")
            openai_project = st.secrets.get("OPENAI_PROJECT", "")
        else:
            # Fallback naar environment variables
            openai_key = os.getenv("OPENAI_API_KEY", "")
            openai_org = os.getenv("OPENAI_ORG_ID", "")
            openai_project = os.getenv("OPENAI_PROJECT", "")
        
        # Set environment variables voor de CLI module
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if openai_org:
            os.environ["OPENAI_ORG_ID"] = openai_org
        if openai_project:
            os.environ["OPENAI_PROJECT"] = openai_project
            
        return openai_key, openai_org, openai_project
    except Exception as e:
        st.error(f"Fout bij laden credentials: {e}")
        return "", "", ""

# Load credentials bij app start
openai_key, openai_org, openai_project = load_api_credentials()

# Custom CSS voor betere styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .upload-section {
        border: 2px dashed #1f77b4;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .progress-container {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .stSelectbox > div > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header met welkomstbericht
    st.markdown('<h1 class="main-header">📚 Arc Crusade Manuscript Assistant</h1>', unsafe_allow_html=True)
    
    # Welkomstbericht voor nieuwe gebruikers
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = False
        st.balloons()
        with st.container():
            st.markdown("""
            <div class="success-box">
                <h3>🎉 Welkom bij Arc Crusade Manuscript Assistant!</h3>
                <p>Upload je manuscript en krijg AI-gebaseerde feedback op structuur, stijl en consistentie.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar voor instellingen
    with st.sidebar:
        st.header("🔧 Instellingen")
        
        # API Status check
        st.subheader("📡 API Status")
        if openai_key and openai_key.startswith("sk-"):
            st.success("✅ OpenAI API sleutel geconfigureerd")
        else:
            st.error("❌ Geen OpenAI API sleutel gevonden")
            st.info("🔧 Configureer je API sleutel in Streamlit Cloud Secrets")
            if st.button("🔄 Herlaad Credentials"):
                st.rerun()
        
        # AI Provider selectie
        provider = st.selectbox(
            "🤖 AI Provider",
            ["openai", "ollama"],
            index=0,
            help="Kies je AI provider"
        )
        
        # Model selectie
        if provider == "openai":
            model_options = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            default_model = "gpt-4o-mini"
        else:
            model_options = ["llama3.1", "llama3", "mistral", "codellama"]
            default_model = "llama3.1"
            
        model = st.selectbox(
            "🧠 Model",
            model_options,
            index=0 if default_model in model_options else 0,
            help="Selecteer het AI model"
        )
        
        # Geavanceerde opties
        st.subheader("⚙️ Geavanceerde opties")
        no_rewrite = st.checkbox("Geen herschrijfsuggesties", help="Sla herschrijfsuggesties over voor snellere verwerking")
        
        # Model informatie
        st.subheader("ℹ️ Model Info")
        if provider == "openai":
            if model == "gpt-4o-mini":
                st.info("💡 Snelste en goedkoopste optie")
            elif model == "gpt-4o":
                st.info("🧠 Meest geavanceerd model")
            else:
                st.info(f"🤖 Geselecteerd: {model}")
        else:
            st.info("🏠 Lokale Ollama server vereist")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload je manuscript")
        
        # File uploader met mooiere styling
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Sleep je bestanden hierheen of klik om te uploaden",
            type=['txt', 'md', 'docx'],
            accept_multiple_files=True,
            help="Ondersteunde formaten: .txt, .md, .docx"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} bestand(en) geüpload")
            
            # Toon bestandsinfo
            with st.expander("📋 Bestandsinformatie", expanded=True):
                for file in uploaded_files:
                    file_size = len(file.getvalue()) / 1024  # KB
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>📄 {file.name}</strong><br>
                        <small>Grootte: {file_size:.1f} KB | Type: {file.type or 'text/plain'}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Process button met betere styling
        process_disabled = not uploaded_files or (provider == "openai" and not openai_key)
        if st.button("🚀 Analyseer Manuscript", type="primary", disabled=process_disabled):
            if not openai_key and provider == "openai":
                st.error("❌ OpenAI API sleutel vereist voor analyse")
            else:
                process_manuscript(uploaded_files, provider, model, no_rewrite)
    
    with col2:
        st.subheader("📊 Statistieken")
        if uploaded_files:
            total_size = sum(len(f.getvalue()) for f in uploaded_files) / 1024
            
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Totale grootte", f"{total_size:.1f} KB")
            with col_stat2:
                st.metric("Bestanden", len(uploaded_files))
                
            # File type breakdown
            file_types = {}
            for f in uploaded_files:
                ext = f.name.split('.')[-1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            
            if len(file_types) > 1:
                st.subheader("📈 Bestandstypes")
                for ext, count in file_types.items():
                    st.write(f"• **.{ext}**: {count} bestand(en)")
        
        # Features box met gradient
        st.markdown("""
        <div class="feature-box">
            <h4>🎯 AI Analyse Features</h4>
            <ul>
                <li>📝 Manuscript outline</li>
                <li>🔍 Hoofdstuk analyse</li>
                <li>⚡ Schrijfstijl feedback</li>
                <li>📈 Tekst statistieken</li>
                <li>🕒 Tijdlijn controle</li>
                <li>✍️ Herschrijf suggesties</li>
                <li>📊 Interactieve rapporten</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Usage tips
        with st.expander("💡 Tips voor beste resultaten"):
            st.markdown("""
            - **Hoofdstukken**: Markeer duidelijk met "Hoofdstuk X" of "Chapter X"
            - **Bestandsgrootte**: Houd bestanden onder 10MB voor snelle verwerking
            - **Formaat**: .txt bestanden werken het beste
            - **Taal**: Tool is geoptimaliseerd voor Nederlandse teksten
            - **API Kosten**: gpt-4o-mini is goedkoopste optie
            """)

def process_manuscript(uploaded_files, provider, model, no_rewrite):
    """Process the uploaded manuscript files with enhanced UI"""
    
    # Progress tracking met mooiere UI
    st.markdown("### 🔄 Manuscript wordt geanalyseerd...")
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Estimated time display
        estimated_time = len(uploaded_files) * 30  # Rough estimate
        time_display = st.empty()
        start_time = time.time()
    
    try:
        # Step 1: Lees bestanden
        status_text.text("📖 Bestanden inlezen en verwerken...")
        time_display.text(f"⏱️ Geschatte tijd: {estimated_time} seconden")
        progress_bar.progress(10)
        
        full_text = ""
        sections = []
        
        for file in uploaded_files:
            # Simuleer bestand schrijven en lezen
            temp_path = Path("temp_" + file.name)
            temp_path.write_bytes(file.getvalue())
            
            try:
                txt = read_file(temp_path)
                full_text += f"\n\n=== FILE: {file.name} ===\n\n{txt}"
                sections += split_sections(txt)
            finally:
                if temp_path.exists():
                    temp_path.unlink()
        
        if not sections:
            st.error("❌ Geen secties gevonden. Zorg ervoor dat je hoofdstukken duidelijk gemarkeerd zijn met 'Hoofdstuk X' of 'Chapter X'.")
            return
        
        st.info(f"📚 {len(sections)} secties gevonden voor analyse")
        
        # Step 2: Genereer outline
        status_text.text("🗂️ Manuscript outline genereren...")
        progress_bar.progress(20)
        elapsed = time.time() - start_time
        remaining = max(0, estimated_time - elapsed)
        time_display.text(f"⏱️ Resterende tijd: ~{remaining:.0f} seconden")
        
        outline = call_model(p_outline(full_text), provider, model, 0.2)
        
        # Step 3: Analyseer secties
        results = []
        rubric_blobs = []
        
        total_sections = len(sections)
        for i, sec in enumerate(sections):
            progress = 20 + (i / total_sections) * 50
            progress_bar.progress(int(progress))
            status_text.text(f"🔍 Analyseren: {sec['title']} ({i+1}/{total_sections})")
            
            elapsed = time.time() - start_time
            remaining = max(0, estimated_time - elapsed)
            time_display.text(f"⏱️ Resterende tijd: ~{remaining:.0f} seconden")
            
            m = rough_metrics(sec["text"])
            rub = call_model(p_rubric(sec["title"], sec["text"]), provider, model, 0.3)
            rubric_blobs.append(f"--- {sec['title']} ---\n{rub[:4000]}")
            
            rewrite = ""
            if not no_rewrite:
                rewrite = call_model(p_short_rewrite(sec["title"], sec["text"]), provider, model, 0.5)
            
            results.append({
                "title": sec["title"], 
                "metrics": m, 
                "rubric": rub, 
                "rewrite": rewrite
            })
        
        # Step 4: Top issues en plan
        status_text.text("🎯 Belangrijkste verbeterpunten identificeren...")
        progress_bar.progress(75)
        
        top_issues = call_model(p_top_issues(rubric_blobs), provider, model, 0.2)
        plan = call_model(p_plan(outline, top_issues), provider, model, 0.2)
        
        # Step 5: Timeline analyse
        status_text.text("🕒 Tijdlijn en consistentie analyseren...")
        progress_bar.progress(85)
        
        timeline_rows = []
        for sec in sections:
            marks = extract_time_markers(sec["text"])
            pretty = "; ".join([f"{k}:{v}" for (k,v) in marks]) if marks else "(geen)"
            timeline_rows.append(f"* {sec['title']}: {pretty}")
        
        timeline_text = "\n".join(timeline_rows)
        timeline_feedback = call_model(p_timeline_feedback(timeline_text), provider, model, 0.2)
        
        # Step 6: Resultaten opslaan en tonen
        status_text.text("💾 Resultaten opslaan en rapport genereren...")
        progress_bar.progress(95)
        
        ts = time.strftime("%Y%m%d-%H%M%S")
        
        # Save files
        report_data = {
            "outline": outline,
            "issues": top_issues,
            "plan": plan,
            "timeline_extract": timeline_text,
            "timeline_feedback": timeline_feedback,
            "sections": results,
            "analysis_info": {
                "provider": provider,
                "model": model,
                "timestamp": ts,
                "total_sections": len(results),
                "processing_time": time.time() - start_time
            }
        }
        
        # Maak output bestanden
        create_output_files(report_data, results, ts)
        
        # Step 7: Klaar!
        progress_bar.progress(100)
        final_time = time.time() - start_time
        status_text.text("✅ Analyse succesvol voltooid!")
        time_display.text(f"🎉 Voltooid in {final_time:.1f} seconden")
        
        # Clear progress container en toon resultaten
        progress_container.empty()
        
        # Success animation
        st.balloons()
        
        # Toon resultaten
        display_results(report_data, results, ts)
        
    except Exception as e:
        st.error(f"❌ Fout tijdens verwerking: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Verwerking mislukt - probeer opnieuw")
        time_display.text("")
        
        # Debug info voor ontwikkelaars
        with st.expander("🔧 Debug informatie"):
            st.code(str(e))

def create_output_files(report_data, results, ts):
    """Create output files and prepare downloads"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    rew_dir = OUTPUT_DIR / "rewrites"
    rew_dir.mkdir(exist_ok=True)
    
    # Create enhanced markdown report
    report_md = [
        f"# 📚 Arc Crusade Manuscript Analyse Rapport",
        f"**Gegenereerd op:** {datetime.now().strftime('%d-%m-%Y om %H:%M')}",
        f"**Model gebruikt:** {report_data['analysis_info']['provider']} - {report_data['analysis_info']['model']}",
        f"**Verwerkingstijd:** {report_data['analysis_info']['processing_time']:.1f} seconden",
        f"**Aantal secties:** {report_data['analysis_info']['total_sections']}",
        "",
        "---",
        "",
        "## 📋 Manuscript Outline", 
        report_data["outline"],
        "",
        "## 🎯 Top 10 Verbeterpunten", 
        report_data["issues"],
        "",
        "## 📈 Aanbevolen Verbeterplan", 
        report_data["plan"],
        "",
        "## 🕒 Tijdlijn Extractie", 
        f"```\n{report_data['timeline_extract']}\n```",
        "",
        "## ⚡ Tijdlijn Consistentie Feedback", 
        report_data["timeline_feedback"],
        "",
        "## 📖 Gedetailleerde Sectie Analyses"
    ]
    
    for r in results:
        report_md += [
            f"### 📝 {r['title']}",
            f"**Statistieken:** {json.dumps(r['metrics'], ensure_ascii=False)}",
            "",
            "#### 🔍 Analyse & Feedback",
            r["rubric"],
            "",
            "#### ✍️ Herschrijfvoorstel",
            r["rewrite"] or "_(Geen herschrijfvoorstel gegenereerd)_",
            "",
            "---",
            ""
        ]
        
        if r["rewrite"]:
            import re
            safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", r["title"])[:60]
            (rew_dir / f"{safe}-{ts}.md").write_text(r["rewrite"], encoding="utf-8")
    
    # Save files
    (OUTPUT_DIR / f"report-{ts}.md").write_text("\n".join(report_md), encoding="utf-8")
    (OUTPUT_DIR / f"results-{ts}.json").write_text(
        json.dumps(report_data, ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )

def display_results(report_data, results, ts):
    """Display the analysis results in Streamlit with enhanced UI"""
    
    # Success header
    st.markdown("""
    <div class="success-box">
        <h2>🎉 Manuscript Analyse Voltooid!</h2>
        <p>Je gedetailleerde analyse is klaar. Bekijk de resultaten hieronder of download de rapporten.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Secties", len(results))
    with col2:
        total_words = sum(r['metrics'].get('words', 0) for r in results)
        st.metric("📊 Totaal woorden", f"{total_words:,}")
    with col3:
        processing_time = report_data.get('analysis_info', {}).get('processing_time', 0)
        st.metric("⏱️ Verwerkingstijd", f"{processing_time:.1f}s")
    with col4:
        model_used = report_data.get('analysis_info', {}).get('model', 'Unknown')
        st.metric("🤖 Model", model_used)
    
    st.markdown("---")
    
    # Download section
    st.subheader("📥 Download je rapporten")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON download
        json_data = json.dumps(report_data, ensure_ascii=False, indent=2)
        st.download_button(
            "📊 JSON Data",
            json_data,
            f"manuscript-analyse-{ts}.json",
            "application/json",
            help="Gestructureerde data voor verdere verwerking"
        )
    
    with col2:
        # Markdown report
        if (OUTPUT_DIR / f"report-{ts}.md").exists():
            report_content = (OUTPUT_DIR / f"report-{ts}.md").read_text(encoding="utf-8")
            st.download_button(
                "📝 Volledig Rapport",
                report_content,
                f"manuscript-rapport-{ts}.md",
                "text/markdown",
                help="Uitgebreid rapport in Markdown formaat"
            )
    
    with col3:
        # ZIP van alle bestanden
        create_zip_download(ts)
    
    st.markdown("---")
    
    # Results tabs met verbeterde layout
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Overzicht", 
        "📖 Sectie Analyses", 
        "🕒 Tijdlijn", 
        "📊 Statistieken",
        "🎯 Verbeterplan"
    ])
    
    with tab1:
        st.subheader("📋 Manuscript Overzicht")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**🗂️ Gegenereerde Outline:**")
            st.markdown(report_data["outline"])
        
        with col2:
            # Analysis info box
            analysis_info = report_data.get('analysis_info', {})
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔍 Analyse Details</h4>
                <p><strong>Provider:</strong> {analysis_info.get('provider', 'N/A')}</p>
                <p><strong>Model:</strong> {analysis_info.get('model', 'N/A')}</p>
                <p><strong>Verwerkingstijd:</strong> {analysis_info.get('processing_time', 0):.1f}s</p>
                <p><strong>Timestamp:</strong> {analysis_info.get('timestamp', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🎯 Belangrijkste Bevindingen")
        st.markdown(report_data["issues"])
    
    with tab2:
        st.subheader("📖 Gedetailleerde Sectie Analyses")
        
        # Search/filter functionality
        search_term = st.text_input("🔍 Zoek in secties:", placeholder="Type om te filteren...")
        
        for i, result in enumerate(results):
            # Filter op zoekterm
            if search_term and search_term.lower() not in result['title'].lower():
                continue
                
            with st.expander(f"📝 {result['title']}", expanded=i==0):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Metrics in mooie cards
                    metrics = result['metrics']
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📊 Tekst Statistieken</h4>
                        <p><strong>Woorden:</strong> {metrics.get('words', 0):,}</p>
                        <p><strong>Zinnen:</strong> {metrics.get('sentences', 0):,}</p>
                        <p><strong>Dialoog:</strong> {metrics.get('dialogue_pct', 0):.1f}%</p>
                        <p><strong>Gem. woorden/zin:</strong> {metrics.get('words', 0) / max(1, metrics.get('sentences', 1)):.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**🔍 Analyse & Feedback:**")
                    with st.container():
                        st.markdown(result['rubric'])
                
                with col2:
                    if result['rewrite']:
                        st.markdown("**✍️ Herschrijfvoorstel:**")
                        with st.container():
                            st.markdown(result['rewrite'])
                            
                        # Download button voor individuele herschrijving
                        st.download_button(
                            f"💾 Download herschrijving",
                            result['rewrite'],
                            f"herschrijving-{result['title'][:30]}-{ts}.md",
                            "text/markdown",
                            key=f"download_{i}"
                        )
                    else:
                        st.info("💡 Geen herschrijfvoorstel gegenereerd (uitgeschakeld in instellingen)")
    
    with tab3:
        st.subheader("🕒 Tijdlijn & Consistentie Analyse")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**📅 Geëxtraheerde tijdmarkers:**")
            st.code(report_data["timeline_extract"], language="markdown")
        
        with col2:
            st.markdown("**⚡ Consistentie feedback:**")
            st.markdown(report_data["timeline_feedback"])
    
    with tab4:
        st.subheader("📊 Manuscript Statistieken & Visualisaties")
        
        # Overall stats cards
        total_words = sum(r['metrics'].get('words', 0) for r in results)
        total_sentences = sum(r['metrics'].get('sentences', 0) for r in results)
        avg_dialogue = sum(r['metrics'].get('dialogue_pct', 0) for r in results) / len(results) if results else 0
        avg_words_per_sentence = total_words / max(1, total_sentences)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📝 Totaal woorden", f"{total_words:,}")
        col2.metric("💬 Totaal zinnen", f"{total_sentences:,}")
        col3.metric("🗣️ Gem. dialoog %", f"{avg_dialogue:.1f}%")
        col4.metric("📏 Woorden/zin", f"{avg_words_per_sentence:.1f}")
        
        # Interactive charts
        if results:
            import pandas as pd
            
            # Data voorbereiding
            chart_data = pd.DataFrame([
                {
                    'Sectie': r['title'][:25] + "..." if len(r['title']) > 25 else r['title'],
                    'Woorden': r['metrics'].get('words', 0),
                    'Zinnen': r['metrics'].get('sentences', 0),
                    'Dialoog %': r['metrics'].get('dialogue_pct', 0)
                }
                for r in results
            ])
            
            st.subheader("📈 Woorden per sectie")
            st.bar_chart(chart_data.set_index('Sectie')['Woorden'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🗣️ Dialoog percentage")
                st.bar_chart(chart_data.set_index('Sectie')['Dialoog %'])
            
            with col2:
                st.subheader("💬 Zinnen per sectie")
                st.bar_chart(chart_data.set_index('Sectie')['Zinnen'])
            
            # Data table voor gedetailleerde stats
            with st.expander("🔍 Gedetailleerde statistieken tabel"):
                st.dataframe(chart_data, use_container_width=True)
    
    with tab5:
        st.subheader("🎯 Persoonlijk Verbeterplan")
        st.markdown(report_data["plan"])
        
        # Actie items
        st.markdown("### 📋 Actiepunten")
        st.markdown("""
        **Volgende stappen:**
        1. 📖 Lees het volledige rapport door
        2. 🎯 Prioriteer de verbeterpunten
        3. ✍️ Begin met de herschrijfsuggesties
        4. 🔄 Herhaal het proces na revisies
        5. 🎉 Vier je vooruitgang!
        """)
        
        # Tips voor verbetering
        with st.expander("💡 Extra schrijftips"):
            st.markdown("""
            - **Consistentie:** Let op tijdlijn en character ontwikkeling
            - **Dialoog:** Zorg voor natuurlijke gesprekken
            - **Pacing:** Wissel af tussen actie en reflectie
            - **Show don't tell:** Laat zien in plaats van vertellen
            - **Editing:** Laat het manuscript 'rusten' voor je reviseert
            """)

def create_zip_download(ts):
    """Create a ZIP file with all outputs"""
    zip_buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add main files
            report_file = OUTPUT_DIR / f"report-{ts}.md"
            json_file = OUTPUT_DIR / f"results-{ts}.json"
            
            if report_file.exists():
                zip_file.write(report_file, f"manuscript-rapport-{ts}.md")
            if json_file.exists():
                zip_file.write(json_file, f"analyse-data-{ts}.json")
            
            # Add rewrites
            rew_dir = OUTPUT_DIR / "rewrites"
            if rew_dir.exists():
                for rewrite_file in rew_dir.glob(f"*-{ts}.md"):
                    zip_file.write(rewrite_file, f"herschrijvingen/{rewrite_file.name}")
        
        zip_buffer.seek(0)
        
        st.download_button(
            "📦 Compleet Pakket (ZIP)",
            zip_buffer.getvalue(),
            f"arc-crusade-manuscript-analyse-{ts}.zip",
            "application/zip",
            help="Alle rapporten en bestanden in één ZIP bestand"
        )
    except Exception as e:
        st.error(f"Fout bij maken ZIP bestand: {e}")

if __name__ == "__main__":
    main()