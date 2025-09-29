#!/usr/bin/env python3
"""
Streamlit Web Interface voor Arc Crusade Manuscript Assistant
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

# Custom CSS voor betere styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .progress-container {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">📚 Arc Crusade Manuscript Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar voor instellingen
    with st.sidebar:
        st.header("🔧 Instellingen")
        
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
        
        # API Status check
        st.subheader("📡 API Status")
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key.startswith("sk-"):
                st.success("✅ OpenAI API sleutel gevonden")
            else:
                st.error("❌ OpenAI API sleutel niet gevonden in .env")
        else:
            st.info("🔄 Ollama - Zorg dat de server draait op localhost:11434")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload je manuscript")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Sleep je bestanden hierheen of klik om te uploaden",
            type=['txt', 'md', 'docx'],
            accept_multiple_files=True,
            help="Ondersteunde formaten: .txt, .md, .docx"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} bestand(en) geüpload")
            
            # Toon bestandsinfo
            with st.expander("📋 Bestandsinformatie"):
                for file in uploaded_files:
                    file_size = len(file.getvalue()) / 1024  # KB
                    st.write(f"• **{file.name}** ({file_size:.1f} KB)")
        
        # Process button
        if st.button("🚀 Analyseer Manuscript", type="primary", disabled=not uploaded_files):
            process_manuscript(uploaded_files, provider, model, no_rewrite)
    
    with col2:
        st.subheader("📊 Statistieken")
        if uploaded_files:
            total_size = sum(len(f.getvalue()) for f in uploaded_files) / 1024
            st.metric("Totale grootte", f"{total_size:.1f} KB")
            st.metric("Aantal bestanden", len(uploaded_files))
        
        st.subheader("🎯 Features")
        st.info("""
        **✨ Deze tool analyseert:**
        • 📝 Manuscript outline
        • 🔍 Sectie-analyse per hoofdstuk
        • ⚡ Schrijfstijl feedback  
        • 📈 Tekst metrics
        • 🕒 Tijdlijn consistentie
        • ✍️ Herschrijfsuggesties
        • 📊 Gedetailleerde rapporten
        """)

def process_manuscript(uploaded_files, provider, model, no_rewrite):
    """Process the uploaded manuscript files"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Lees bestanden
        status_text.text("📖 Bestanden inlezen...")
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
            st.error("❌ Geen secties gevonden. Zorg ervoor dat je hoofdstukken duidelijk gemarkeerd zijn.")
            return
        
        # Step 2: Genereer outline
        status_text.text("🗂️ Outline genereren...")
        progress_bar.progress(20)
        
        outline = call_model(p_outline(full_text), provider, model, 0.2)
        
        # Step 3: Analyseer secties
        status_text.text("🔍 Secties analyseren...")
        results = []
        rubric_blobs = []
        
        total_sections = len(sections)
        for i, sec in enumerate(sections):
            progress = 20 + (i / total_sections) * 50
            progress_bar.progress(int(progress))
            status_text.text(f"🔍 Analyseren: {sec['title']} ({i+1}/{total_sections})")
            
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
        status_text.text("🎯 Top issues identificeren...")
        progress_bar.progress(75)
        
        top_issues = call_model(p_top_issues(rubric_blobs), provider, model, 0.2)
        plan = call_model(p_plan(outline, top_issues), provider, model, 0.2)
        
        # Step 5: Timeline analyse
        status_text.text("🕒 Tijdlijn analyseren...")
        progress_bar.progress(85)
        
        timeline_rows = []
        for sec in sections:
            marks = extract_time_markers(sec["text"])
            pretty = "; ".join([f"{k}:{v}" for (k,v) in marks]) if marks else "(geen)"
            timeline_rows.append(f"* {sec['title']}: {pretty}")
        
        timeline_text = "\n".join(timeline_rows)
        timeline_feedback = call_model(p_timeline_feedback(timeline_text), provider, model, 0.2)
        
        # Step 6: Resultaten opslaan en tonen
        status_text.text("💾 Resultaten opslaan...")
        progress_bar.progress(95)
        
        ts = time.strftime("%Y%m%d-%H%M%S")
        
        # Save files
        report_data = {
            "outline": outline,
            "issues": top_issues,
            "plan": plan,
            "timeline_extract": timeline_text,
            "timeline_feedback": timeline_feedback,
            "sections": results
        }
        
        # Maak output bestanden
        create_output_files(report_data, results, ts)
        
        # Step 7: Klaar!
        progress_bar.progress(100)
        status_text.text("✅ Analyse voltooid!")
        
        # Toon resultaten
        display_results(report_data, results, ts)
        
    except Exception as e:
        st.error(f"❌ Fout tijdens verwerking: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Verwerking mislukt")

def create_output_files(report_data, results, ts):
    """Create output files and prepare downloads"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    rew_dir = OUTPUT_DIR / "rewrites"
    rew_dir.mkdir(exist_ok=True)
    
    # Create markdown report
    report_md = [
        f"# Manuscript Rapport – {ts}",
        "## Outline", report_data["outline"],
        "## Top 10 Issues", report_data["issues"],
        "## Verbeterplan", report_data["plan"],
        "## Tijdlijn (extractie)", f"```\n{report_data['timeline_extract']}\n```",
        "## Tijdlijn-consistentie (advies)", report_data["timeline_feedback"],
        "## Secties"
    ]
    
    for r in results:
        report_md += [
            f"### {r['title']}",
            f"- Metrics: {json.dumps(r['metrics'])}",
            "#### Rubriek", r["rubric"],
            "#### Herschrijfsuggestie", r["rewrite"] or "_(uit)_"
        ]
        
        if r["rewrite"]:
            import re
            safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", r["title"])[:60]
            (rew_dir / f"{safe}-{ts}.md").write_text(r["rewrite"], encoding="utf-8")
    
    # Save files
    (OUTPUT_DIR / f"report-{ts}.md").write_text("\n\n".join(report_md), encoding="utf-8")
    (OUTPUT_DIR / f"results-{ts}.json").write_text(
        json.dumps(report_data, ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )

def display_results(report_data, results, ts):
    """Display the analysis results in Streamlit"""
    
    st.success("🎉 **Analyse voltooid!**")
    
    # Download section
    st.subheader("📥 Downloads")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON download
        json_data = json.dumps(report_data, ensure_ascii=False, indent=2)
        st.download_button(
            "📊 JSON Resultaten",
            json_data,
            f"results-{ts}.json",
            "application/json"
        )
    
    with col2:
        # Markdown report
        if (OUTPUT_DIR / f"report-{ts}.md").exists():
            report_content = (OUTPUT_DIR / f"report-{ts}.md").read_text(encoding="utf-8")
            st.download_button(
                "📝 Markdown Rapport",
                report_content,
                f"report-{ts}.md",
                "text/markdown"
            )
    
    with col3:
        # ZIP van alle bestanden
        create_zip_download(ts)
    
    st.markdown("---")
    
    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overzicht", "📖 Secties", "🕒 Tijdlijn", "📊 Metrics"])
    
    with tab1:
        st.subheader("📋 Manuscript Overzicht")
        st.markdown("**Gegenereerde Outline:**")
        st.markdown(report_data["outline"])
        
        st.subheader("🎯 Top Issues")
        st.markdown(report_data["issues"])
        
        st.subheader("📈 Verbeterplan")
        st.markdown(report_data["plan"])
    
    with tab2:
        st.subheader("📖 Sectie Analyses")
        for i, result in enumerate(results):
            with st.expander(f"📝 {result['title']}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**📊 Metrics:**")
                    metrics = result['metrics']
                    st.write(f"• Woorden: {metrics.get('words', 0)}")
                    st.write(f"• Zinnen: {metrics.get('sentences', 0)}")
                    st.write(f"• Dialoog: {metrics.get('dialogue_pct', 0):.1f}%")
                    
                    st.markdown("**🔍 Analyse:**")
                    st.markdown(result['rubric'][:500] + "..." if len(result['rubric']) > 500 else result['rubric'])
                
                with col2:
                    if result['rewrite']:
                        st.markdown("**✍️ Herschrijfvoorstel:**")
                        st.markdown(result['rewrite'][:500] + "..." if len(result['rewrite']) > 500 else result['rewrite'])
                    else:
                        st.info("Geen herschrijfvoorstel gegenereerd")
    
    with tab3:
        st.subheader("🕒 Tijdlijn Analyse")
        st.markdown("**Geëxtraheerde tijdmarkers:**")
        st.code(report_data["timeline_extract"])
        
        st.markdown("**Consistentie feedback:**")
        st.markdown(report_data["timeline_feedback"])
    
    with tab4:
        st.subheader("📊 Manuscript Statistieken")
        
        # Overall stats
        total_words = sum(r['metrics'].get('words', 0) for r in results)
        total_sentences = sum(r['metrics'].get('sentences', 0) for r in results)
        avg_dialogue = sum(r['metrics'].get('dialogue_pct', 0) for r in results) / len(results) if results else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Totaal woorden", total_words)
        col2.metric("Totaal zinnen", total_sentences)
        col3.metric("Gem. dialoog %", f"{avg_dialogue:.1f}%")
        col4.metric("Secties", len(results))
        
        # Per section chart
        if results:
            import pandas as pd
            chart_data = pd.DataFrame([
                {
                    'Sectie': r['title'][:20] + "..." if len(r['title']) > 20 else r['title'],
                    'Woorden': r['metrics'].get('words', 0),
                    'Dialoog %': r['metrics'].get('dialogue_pct', 0)
                }
                for r in results
            ])
            
            st.subheader("📈 Woorden per sectie")
            st.bar_chart(chart_data.set_index('Sectie')['Woorden'])

def create_zip_download(ts):
    """Create a ZIP file with all outputs"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main files
        report_file = OUTPUT_DIR / f"report-{ts}.md"
        json_file = OUTPUT_DIR / f"results-{ts}.json"
        
        if report_file.exists():
            zip_file.write(report_file, f"report-{ts}.md")
        if json_file.exists():
            zip_file.write(json_file, f"results-{ts}.json")
        
        # Add rewrites
        rew_dir = OUTPUT_DIR / "rewrites"
        if rew_dir.exists():
            for rewrite_file in rew_dir.glob(f"*-{ts}.md"):
                zip_file.write(rewrite_file, f"rewrites/{rewrite_file.name}")
    
    zip_buffer.seek(0)
    
    st.download_button(
        "📦 Alle bestanden (ZIP)",
        zip_buffer.getvalue(),
        f"manuscript-analyse-{ts}.zip",
        "application/zip"
    )

if __name__ == "__main__":
    main()