#!/usr/bin/env python3
"""
Streamlit Web Interface for Arc Crusade Manuscript Assistant
"""
import streamlit as st
import os
import json
import time
from pathlib import Path
import zipfile
import io
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

def check_password():
    """Simple password protection for the app"""
    def password_entered():
        # Check if password is correct (from Streamlit secrets or env var)
        correct_password = st.secrets.get("APP_PASSWORD", os.getenv("APP_PASSWORD", "arccrusade2024"))
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("### 🏰 Arc Crusade AI - Private Access")
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://via.placeholder.com/200x100/2E86AB/FFFFFF?text=ARC+CRUSADE", width=200)
            st.text_input("🔐 Wachtwoord vereist", type="password", 
                         on_change=password_entered, key="password",
                         help="Voer het wachtwoord in om toegang te krijgen")
        st.info("💡 Deze tool is alleen toegankelijk voor geautoriseerde gebruikers")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("### 🏰 Arc Crusade AI - Private Access") 
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://via.placeholder.com/200x100/2E86AB/FFFFFF?text=ARC+CRUSADE", width=200)
            st.text_input("🔐 Wachtwoord vereist", type="password", 
                         on_change=password_entered, key="password",
                         help="Voer het wachtwoord in om toegang te krijgen")
        st.error("❌ Incorrect wachtwoord. Probeer opnieuw.")
        return False
    else:
        return True

# Import our existing functions
from cli_manuscript_assistant import (
    call_model, read_file, split_sections, rough_metrics, enhanced_metrics,
    p_outline, p_rubric, p_short_rewrite, p_top_issues, p_plan,
    p_timeline_feedback, extract_time_markers, OUTPUT_DIR, 
    save_analysis_with_onedrive
)
# Import advanced analysis functions
from enhanced_analysis import (
    p_advanced_rewrite, p_character_voice_analysis, p_scene_structure_analysis,
    p_emotional_depth_analysis, p_prose_quality_analysis, p_genre_specific_analysis
)

# Page config
st.set_page_config(
    page_title="📚 Arc Crusade Manuscript Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    # Check password first
    if not check_password():
        return
    
    # Header
    st.markdown('<h1 class="main-header">📚 Arc Crusade Manuscript Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("🔧 Settings")
        
        # AI Provider selection
        provider = st.selectbox(
            "🤖 AI Provider",
            ["openai", "ollama"],
            index=0,
            help="Choose your AI provider"
        )
        
        # Model selection
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
            help="Select the AI model"
        )
        
        # Advanced options
        st.subheader("⚙️ Analysis Options")
        
        # Basic settings
        no_rewrite = st.checkbox("Skip rewrite suggestions", help="Skip rewrite suggestions for faster processing")
        enhanced_analysis = st.checkbox("🚀 Enhanced Analysis", value=True, help="Use in-depth analysis of characters, pacing and style")
        
        # Genre selection for specific analysis  
        genre = st.selectbox(
            "📖 Genre",
            ["fantasy", "thriller", "romance", "mystery", "literary", "sci-fi", "historical"],
            help="Select genre for targeted feedback"
        )
        
        # Rewrite focus
        if not no_rewrite:
            rewrite_focus = st.selectbox(
                "🎯 Rewrite Focus",
                ["overall", "pacing", "character", "dialog", "description", "tension", "style"],
                help="What should the rewrite focus on?"
            )
        else:
            rewrite_focus = "overall"
        
        # API Status check
        st.subheader("📡 API Status")
        if provider == "openai":
            # Try Streamlit secrets first, then .env as fallback
            api_key = None
            source = None
            
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
                source = "Streamlit secrets"
            except (KeyError, FileNotFoundError, AttributeError):
                pass
            
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
                source = ".env file"
            
            if api_key and api_key.startswith("sk-"):
                st.success(f"✅ OpenAI API key found ({source})")
                # Show partial key for verification
                masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "sk-***"
                st.info(f"🔑 Key: {masked_key}")
            else:
                st.error("❌ OpenAI API key not found. Configure secrets.toml or .env")
                st.markdown("""
                **Configuration options:**
                1. Local: Add `OPENAI_API_KEY` to `.env` file
                2. Streamlit Cloud: Configure in App Settings → Secrets
                """)
        else:
            st.info("🔄 Ollama - Ensure server is running on localhost:11434")
        
        # OneDrive integration
        st.subheader("📁 OneDrive Integration")
        try:
            from onedrive_integration import OneDriveManager
            onedrive = OneDriveManager()
            
            if onedrive.is_onedrive_available():
                st.success("✅ OneDrive detected")
                st.info(f"📂 Path: {onedrive.base_path}")
                
                auto_save_onedrive = st.checkbox(
                    "🔄 Auto-save to OneDrive",
                    value=True,
                    help="Automatically save analyses to your OneDrive for Zapier workflows"
                )
                
                if st.button("📋 Setup OneDrive"):
                    success, message = onedrive.setup_onedrive_structure()
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
            else:
                st.warning("⚠️ OneDrive not found")
                auto_save_onedrive = False
                
        except ImportError:
            st.info("📝 OneDrive integration not available")
            auto_save_onedrive = False
        except Exception as e:
            st.error(f"❌ OneDrive error: {str(e)}")
            auto_save_onedrive = False
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload your manuscript")
        
        # Client Organization Section
        st.markdown("### 👤 Client Information")
        col_client1, col_client2 = st.columns([2, 1])
        
        with col_client1:
            client_name = st.text_input(
                "Client Name", 
                placeholder="e.g., John Smith, Fantasy Publishing, etc.",
                help="Enter client name for organized export (optional but recommended)"
            )
        
        with col_client2:
            use_client_export = st.checkbox(
                "🗂️ Organized Export",
                value=bool(client_name),
                help="Create client-specific folder structure"
            )
        
        if use_client_export and client_name:
            # Export path configuration
            with st.expander("📂 Export Settings", expanded=False):
                export_path = st.text_input(
                    "Custom Export Path",
                    value=r"G:\Mijn Drive\The arc crusade\Export Arc Crusade Program",
                    help="Path where client folders will be created"
                )
                
                if export_path:
                    st.info(f"📁 Client folder will be created at:\n`{export_path}\\{client_name}_[manuscript]_[date]`")
        
        st.markdown("---")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Drag your files here or click to upload",
            type=['txt', 'md', 'docx'],
            accept_multiple_files=True,
            help="Supported formats: .txt, .md, .docx"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            # Show file info
            with st.expander("📋 File information"):
                for file in uploaded_files:
                    file_size = len(file.getvalue()) / 1024  # KB
                    st.write(f"• **{file.name}** ({file_size:.1f} KB)")
                    
            # Show export preview if client info provided
            if use_client_export and client_name:
                st.success(f"🎯 Will create organized export for: **{client_name}**")
        
        # Process button  
        if st.button("🚀 Analyze Manuscript", type="primary", disabled=not uploaded_files):
            # Get OneDrive setting from sidebar (if it exists)
            try:
                # This variable should be available from sidebar
                auto_save_setting = auto_save_onedrive if 'auto_save_onedrive' in locals() else False
            except NameError:
                auto_save_setting = False
            
            # Prepare client export settings
            client_export_settings = None
            if use_client_export and client_name:
                client_export_settings = {
                    'client_name': client_name,
                    'export_path': export_path if 'export_path' in locals() else None
                }
                
            result = process_manuscript(
                uploaded_files, provider, model, no_rewrite, enhanced_analysis, 
                genre, rewrite_focus, auto_save_setting, client_export_settings
            )
            
            # Process results
            if result and result[0] is not None:
                # Results are already displayed within process_manuscript
                pass
            else:
                st.error("❌ Analysis failed")
    
    with col2:
        st.subheader("📊 Statistics")
        if uploaded_files:
            total_size = sum(len(f.getvalue()) for f in uploaded_files) / 1024
            st.metric("Total size", f"{total_size:.1f} KB")
            st.metric("Number of files", len(uploaded_files))
        
        st.subheader("🎯 Features")
        st.info("""
        **✨ This tool analyzes:**
        • 📝 Manuscript outline
        • 🔍 Section analysis per chapter
        • ⚡ Writing style feedback  
        • 📈 Text metrics
        • 🕒 Timeline consistency
        • ✍️ Rewrite suggestions
        • 📊 Detailed reports
        """)

def process_manuscript(uploaded_files, provider, model, no_rewrite, enhanced_analysis=True, genre="fantasy", rewrite_focus="overall", auto_save_onedrive=False, client_export_settings=None):
    """Process the uploaded manuscript files"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Read files
        status_text.text("📖 Reading files...")
        progress_bar.progress(10)
        
        full_text = ""
        sections = []
        
        for file in uploaded_files:
            # Simulate file writing and reading
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
            st.error("❌ No sections found. Make sure your chapters are clearly marked.")
            return
        
        # Step 2: Generate outline
        status_text.text("🗂️ Generating outline...")
        progress_bar.progress(20)
        
        outline = call_model(p_outline(full_text), provider, model, 0.2)
        
        # Step 3: Analyze sections
        status_text.text("🔍 Analyzing sections...")
        results = []
        rubric_blobs = []
        
        total_sections = len(sections)
        for i, sec in enumerate(sections):
            progress = 20 + (i / total_sections) * 50
            progress_bar.progress(int(progress))
            status_text.text(f"🔍 Analyzing: {sec['title']} ({i+1}/{total_sections})")
            
            # Basic metrics
            if enhanced_analysis:
                m = enhanced_metrics(sec["content"])
            else:
                m = rough_metrics(sec["content"])
            
            # Basic rubric
            rub = call_model(p_rubric(sec["title"], sec["content"]), provider, model, 0.3)
            rubric_blobs.append(f"--- {sec['title']} ---\n{rub[:4000]}")
            
            # Advanced analyses
            advanced_analyses = {}
            if enhanced_analysis:
                status_text.text(f"🎭 Advanced analysis: {sec['title']} ({i+1}/{total_sections})")
                
                # Character analysis
                if m.get("characters"):
                    char_analysis = call_model(p_character_voice_analysis(sec["content"]), provider, model, 0.3)
                    advanced_analyses["character_analysis"] = char_analysis
                
                # Scene structure
                scene_analysis = call_model(p_scene_structure_analysis(sec["content"]), provider, model, 0.3)
                advanced_analyses["scene_structure"] = scene_analysis
                
                # Emotional depth
                emotion_analysis = call_model(p_emotional_depth_analysis(sec["content"]), provider, model, 0.3)
                advanced_analyses["emotional_depth"] = emotion_analysis
                
                # Genre-specific analysis
                genre_analysis = call_model(p_genre_specific_analysis(sec["content"], genre), provider, model, 0.3)
                advanced_analyses["genre_analysis"] = genre_analysis
            
            # Rewrite suggestions
            rewrite = ""
            if not no_rewrite:
                if enhanced_analysis:
                    rewrite = call_model(p_advanced_rewrite(sec["title"], sec["content"], rewrite_focus), provider, model, 0.5)
                else:
                    rewrite = call_model(p_short_rewrite(sec["title"], sec["content"]), provider, model, 0.5)
            
            section_result = {
                "title": sec["title"], 
                "metrics": m, 
                "rubric": rub, 
                "rewrite": rewrite
            }
            
            # Add advanced analyses if available
            if enhanced_analysis and advanced_analyses:
                section_result["advanced_analysis"] = advanced_analyses
                
            results.append(section_result)
        
        # Step 4: Top issues and plan
        status_text.text("🎯 Identifying top issues...")
        progress_bar.progress(75)
        
        top_issues = call_model(p_top_issues(rubric_blobs), provider, model, 0.2)
        plan = call_model(p_plan(outline, top_issues), provider, model, 0.2)
        
        # Step 5: Timeline analysis
        status_text.text("🕒 Analyzing timeline...")
        progress_bar.progress(85)
        
        timeline_rows = []
        for sec in sections:
            marks = extract_time_markers(sec["content"])
            pretty = "; ".join([f"{k}:{v}" for (k,v) in marks]) if marks else "(none)"
            timeline_rows.append(f"* {sec['title']}: {pretty}")
        
        timeline_text = "\n".join(timeline_rows)
        timeline_feedback = call_model(p_timeline_feedback(timeline_text), provider, model, 0.2)
        
        # Step 6: Save and show results
        status_text.text("💾 Saving results...")
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
        
        # Create output files
        create_output_files(report_data, results, ts, auto_save_onedrive, client_export_settings, uploaded_files)
        
        # Step 7: Done!
        progress_bar.progress(100)
        status_text.text("✅ Analysis completed!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Show results
        display_results(report_data, results, ts)
        
        return report_data, results, ts
        
    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Processing failed")
        return None, None, None

def create_output_files(report_data, results, ts, auto_save_onedrive=False, client_export_settings=None, uploaded_files=None):
    """Create output files and prepare downloads"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    rew_dir = OUTPUT_DIR / "rewrites"
    rew_dir.mkdir(exist_ok=True)
    
    # Create markdown report
    report_md = [
        f"# Manuscript Report – {ts}",
        "## Outline", report_data["outline"],
        "## Top 10 Issues", report_data["issues"],
        "## Improvement Plan", report_data["plan"],
        "## Timeline (extraction)", f"```\n{report_data['timeline_extract']}\n```",
        "## Timeline Consistency (advice)", report_data["timeline_feedback"],
        "## Sections"
    ]
    
    for r in results:
        report_md += [
            f"### {r['title']}",
            f"- Metrics: {json.dumps(r['metrics'], indent=2)}",
            "#### Rubric", r["rubric"]
        ]
        
        # Add advanced analyses
        if "advanced_analysis" in r:
            adv = r["advanced_analysis"]
            if "character_analysis" in adv:
                report_md += ["#### Character Analysis", adv["character_analysis"]]
            if "scene_structure" in adv:
                report_md += ["#### Scene Structure", adv["scene_structure"]]
            if "emotional_depth" in adv:
                report_md += ["#### Emotional Depth", adv["emotional_depth"]]
            if "genre_analysis" in adv:
                report_md += ["#### Genre Analysis", adv["genre_analysis"]]
        
        report_md += ["#### Rewrite Suggestion", r["rewrite"] or "_(skipped)_"]
        
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
    
    # Client Export Integration
    try:
        from onedrive_integration import OneDriveManager
        onedrive = OneDriveManager()
        
        # Prepare rewrite files
        rewrite_files = list(rew_dir.glob(f"*-{ts}.md"))
        
        # Client-specific export if configured
        if client_export_settings:
            client_name = client_export_settings.get('client_name')
            export_path = client_export_settings.get('export_path')
            
            if client_name and export_path:
                # Setup custom export path
                if onedrive.set_custom_export_path(export_path):
                    # Get original file for client folder
                    original_file = None
                    if uploaded_files:
                        # Create temporary file to represent the original
                        original_filename = uploaded_files[0].name
                        original_file = Path("temp_original_" + original_filename)
                        original_file.write_bytes(uploaded_files[0].getvalue())
                    
                    success = onedrive.save_analysis_to_client_folder(
                        client_name=client_name,
                        analysis_data=report_data,
                        report_content="\n\n".join(report_md),
                        original_file=original_file,
                        rewrite_files=rewrite_files,
                        timestamp=ts
                    )
                    
                    # Clean up temp file
                    if original_file and original_file.exists():
                        original_file.unlink()
                    
                    if success:
                        st.success(f"🎯 Client export created for **{client_name}**")
                        st.info(f"📁 Location: `{export_path}\\{client_name}_*_{ts[:8]}`")
                        st.info("""
                        **📋 Organized folders created:**
                        - `01_Original_Manuscript` - Your uploaded files
                        - `02_Analysis_Reports` - Complete analysis report  
                        - `03_Rewritten_Sections` - Improved sections
                        - `04_JSON_Data` - Structured analysis data
                        - `05_Complete_Archive` - ZIP with everything
                        - `06_Notes_And_Feedback` - Space for communication
                        """)
                    else:
                        st.warning(f"⚠️ Client export failed for {client_name}")
                        
                else:
                    st.warning(f"⚠️ Export path not accessible: {export_path}")
        
        # Standard OneDrive integration
        if auto_save_onedrive:
            success, message = save_analysis_with_onedrive(
                analysis_data=report_data,
                report_content="\n\n".join(report_md),
                rewrite_files=rewrite_files,
                timestamp=ts
            )
            
            if success:
                st.info(f"☁️ {message}")
            else:
                st.warning(f"⚠️ OneDrive: {message}")
                
    except ImportError:
        # Fallback if OneDrive integration not available
        if auto_save_onedrive:
            st.warning("⚠️ OneDrive integration not available")
        if client_export_settings:
            st.warning("⚠️ Client export requires OneDrive integration")
    except Exception as e:
        st.error(f"❌ Export error: {str(e)}")

def display_results(report_data, results, ts):
    """Display the analysis results in Streamlit"""
    
    st.success("🎉 **Analysis completed!**")
    
    # Download section
    st.subheader("📥 Downloads")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON download
        json_data = json.dumps(report_data, ensure_ascii=False, indent=2)
        st.download_button(
            "📊 JSON Results",
            json_data,
            f"results-{ts}.json",
            "application/json"
        )
    
    with col2:
        # Markdown report
        if (OUTPUT_DIR / f"report-{ts}.md").exists():
            report_content = (OUTPUT_DIR / f"report-{ts}.md").read_text(encoding="utf-8")
            st.download_button(
                "📝 Markdown Report",
                report_content,
                f"report-{ts}.md",
                "text/markdown"
            )
    
    with col3:
        # ZIP of all files
        create_zip_download(ts)
    
    st.markdown("---")
    
    # Results tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overview", "📖 Sections", "🕒 Timeline", "📊 Metrics", "🚀 Advanced"])
    
    with tab1:
        st.subheader("📋 Manuscript Overview")
        st.markdown("**Generated Outline:**")
        st.markdown(report_data["outline"])
        
        st.subheader("🎯 Top Issues")
        st.markdown(report_data["issues"])
        
        st.subheader("📈 Improvement Plan")
        st.markdown(report_data["plan"])
    
    with tab2:
        st.subheader("📖 Section Analyses")
        for i, result in enumerate(results):
            with st.expander(f"📝 {result['title']}"):
                col1, col2 = st.columns([1, 1])
                
                # Basic metrics
                st.markdown("**📊 Basic Metrics:**")
                metrics = result['metrics']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", metrics.get('words', 0))
                    st.metric("Sentences", metrics.get('sentences', 0))
                with col2:
                    st.metric("Dialogue %", f"{metrics.get('dialog_word_share', 0)*100:.1f}")
                    st.metric("Adverbs", metrics.get('adverb_count', 0))
                with col3:
                    if 'readability_score' in metrics:
                        st.metric("Readability", f"{metrics['readability_score']:.1f}")
                    if 'engagement_score' in metrics:
                        st.metric("⚡ Engagement", f"{metrics['engagement_score']:.1f}")
                
                # Show advanced metrics
                if 'pacing' in metrics:
                    st.markdown("**🎭 Pacing & Style:**")
                    pacing = metrics['pacing']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"• Pacing Score: {pacing.get('pacing_score', 0):.1f}/10")
                        st.write(f"• Action/Description: {pacing.get('action_description_ratio', 0):.2f}")
                    with col2:
                        st.write(f"• Show vs Tell: {metrics.get('show_vs_tell', {}).get('show_vs_tell_score', 0):.1f}/10")
                        st.write(f"• Style Issues: {len(metrics.get('style_issues', []))}")
                
                # Show characters
                if 'characters' in metrics and metrics['characters']:
                    st.markdown("**👥 Characters:**")
                    for char, data in metrics['characters'].items():
                        st.write(f"• **{char}**: {data['mentions']} mentions, {len(data['emotions'])} emotions")
                
                # Basic analysis
                st.markdown("**🔍 Analysis:**")
                with st.expander("View complete analysis"):
                    st.markdown(result['rubric'])
                
                # Advanced analyses
                if "advanced_analysis" in result:
                    adv = result["advanced_analysis"]
                    
                    # Tabbed interface voor geavanceerde analyses
                    adv_tabs = st.tabs(["🎭 Karakter", "🏗️ Structuur", "❤️ Emotie", "📖 Genre"])
                    
                    with adv_tabs[0]:
                        if "character_analysis" in adv:
                            st.markdown(adv["character_analysis"])
                    
                    with adv_tabs[1]:
                        if "scene_structure" in adv:
                            st.markdown(adv["scene_structure"])
                    
                    with adv_tabs[2]:
                        if "emotional_depth" in adv:
                            st.markdown(adv["emotional_depth"])
                    
                    with adv_tabs[3]:
                        if "genre_analysis" in adv:
                            st.markdown(adv["genre_analysis"])
                
                # Rewrite proposal
                if result['rewrite']:
                    st.markdown("**✍️ Rewrite Proposal:**")
                    with st.expander("View complete rewrite"):
                        st.markdown(result['rewrite'])
                else:
                    st.info("No rewrite proposal generated")
    
    with tab3:
        st.subheader("🕒 Timeline Analysis")
        st.markdown("**Extracted time markers:**")
        st.code(report_data["timeline_extract"])
        
        st.markdown("**Consistency feedback:**")
        st.markdown(report_data["timeline_feedback"])
    
    with tab4:
        st.subheader("📊 Manuscript Statistics")
        
        # Overall stats
        total_words = sum(r['metrics'].get('words', 0) for r in results)
        total_sentences = sum(r['metrics'].get('sentences', 0) for r in results)
        avg_dialogue = sum(r['metrics'].get('dialogue_pct', 0) for r in results) / len(results) if results else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total words", total_words)
        col2.metric("Total sentences", total_sentences)
        col3.metric("Avg dialogue %", f"{avg_dialogue:.1f}%")
        col4.metric("Sections", len(results))
        
        # Per section chart
        if results:
            import pandas as pd
            chart_data = pd.DataFrame([
                {
                    'Section': r['title'][:20] + "..." if len(r['title']) > 20 else r['title'],
                    'Words': r['metrics'].get('words', 0),
                    'Dialogue %': r['metrics'].get('dialogue_pct', 0)
                }
                for r in results
            ])
            
            st.subheader("📈 Words per section")
            st.bar_chart(chart_data.set_index('Section')['Words'])
    
    with tab5:
        st.subheader("🚀 Advanced Analysis Dashboard")
        
        # Overall manuscript scores
        if results and any('readability_score' in r['metrics'] for r in results):
            st.subheader("📊 Overall Manuscript Scores")
            
            # Calculate averages
            readability_scores = [r['metrics'].get('readability_score', 0) for r in results if 'readability_score' in r['metrics']]
            engagement_scores = [r['metrics'].get('engagement_score', 0) for r in results if 'engagement_score' in r['metrics']]
            pacing_scores = [r['metrics'].get('pacing', {}).get('pacing_score', 0) for r in results if 'pacing' in r['metrics']]
            show_tell_scores = [r['metrics'].get('show_vs_tell', {}).get('show_vs_tell_score', 0) for r in results if 'show_vs_tell' in r['metrics']]
            
            col1, col2, col3, col4 = st.columns(4)
            if readability_scores:
                col1.metric("🔤 Readability", f"{sum(readability_scores)/len(readability_scores):.1f}/100")
            if engagement_scores:
                col2.metric("⚡ Engagement", f"{sum(engagement_scores)/len(engagement_scores):.1f}/10")
            if pacing_scores:
                col3.metric("🎭 Pacing", f"{sum(pacing_scores)/len(pacing_scores):.1f}/10")
            if show_tell_scores:
                col4.metric("👁️ Show vs Tell", f"{sum(show_tell_scores)/len(show_tell_scores):.1f}/10")
        
        # Character analysis overview
        all_characters = {}
        for result in results:
            if 'characters' in result['metrics']:
                for char, data in result['metrics']['characters'].items():
                    if char not in all_characters:
                        all_characters[char] = {'total_mentions': 0, 'sections': 0, 'emotions': set()}
                    all_characters[char]['total_mentions'] += data['mentions']
                    all_characters[char]['sections'] += 1
                    all_characters[char]['emotions'].update(data['emotions'])
        
        if all_characters:
            st.subheader("👥 Character Overview")
            
            for char, data in sorted(all_characters.items(), key=lambda x: x[1]['total_mentions'], reverse=True):
                with st.expander(f"**{char}** ({data['total_mentions']} mentions in {data['sections']} sections)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Mentions per section:**")
                        avg_per_section = data['total_mentions'] / data['sections']
                        st.write(f"Average: {avg_per_section:.1f} per section")
                        
                    with col2:
                        st.write("**Emotions:**")
                        if data['emotions']:
                            st.write(", ".join(sorted(data['emotions'])))
                        else:
                            st.write("No emotions detected")
        
        # Style issues overview  
        all_style_issues = []
        for result in results:
            if 'style_issues' in result['metrics']:
                all_style_issues.extend(result['metrics']['style_issues'])
        
        if all_style_issues:
            st.subheader("⚠️ Common Style Issues")
            
            # Group similar issues
            issue_categories = {}
            for issue in all_style_issues:
                if 'adverb' in issue.lower():
                    category = 'Too many adverbs'
                elif 'repeated' in issue.lower():
                    category = 'Repeated words'  
                elif 'verb' in issue.lower():
                    category = 'Weak verbs'
                elif 'info-dump' in issue.lower():
                    category = 'Info dumps'
                else:
                    category = 'Other'
                    
                if category not in issue_categories:
                    issue_categories[category] = []
                issue_categories[category].append(issue)
            
            for category, issues in issue_categories.items():
                st.write(f"**{category}** ({len(issues)} cases)")
                with st.expander("View details"):
                    for issue in issues[:5]:  # Max 5 examples
                        st.write(f"• {issue}")
        
        # Recommendations
        st.subheader("💡 Smart Recommendations")
        
        if readability_scores and sum(readability_scores)/len(readability_scores) < 50:
            st.warning("📚 **Readability**: Consider shorter sentences and simpler words for better accessibility.")
        
        if engagement_scores and sum(engagement_scores)/len(engagement_scores) < 6:
            st.warning("⚡ **Engagement**: Add more action, conflict and sensory details to engage readers.")
            
        if show_tell_scores and sum(show_tell_scores)/len(show_tell_scores) < 5:
            st.warning("👁️ **Show vs Tell**: Replace emotion descriptions with actions and body reactions.")

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
        "📦 All files (ZIP)",
        zip_buffer.getvalue(),
        f"manuscript-analysis-{ts}.zip",
        "application/zip"
    )

if __name__ == "__main__":
    main()