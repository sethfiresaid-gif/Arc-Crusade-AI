#!/usr/bin/env python3
"""
Debug versie van Streamlit app om te zien waar het vastloopt
"""
import streamlit as st
import os
from pathlib import Path

# Test de imports
st.title("🔍 Debug Mode - Arc Crusade AI")

st.header("1. Environment Check")

# Check .env file
env_path = Path(".env")
if env_path.exists():
    st.success("✅ .env bestand gevonden")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        st.success(f"✅ OpenAI API key gevonden: {api_key[:10]}...")
    else:
        st.error("❌ Geen geldige OpenAI API key gevonden")
else:
    st.error("❌ .env bestand niet gevonden")

st.header("2. Import Check")

try:
    from cli_manuscript_assistant import call_model, get_api_config
    st.success("✅ cli_manuscript_assistant geïmporteerd")
except Exception as e:
    st.error(f"❌ Import error cli_manuscript_assistant: {e}")

try:
    from enhanced_analysis import analyze_character_development
    st.success("✅ enhanced_analysis geïmporteerd")
except Exception as e:
    st.error(f"❌ Import error enhanced_analysis: {e}")

try:
    from onedrive_integration import OneDriveManager
    st.success("✅ onedrive_integration geïmporteerd")
except Exception as e:
    st.error(f"❌ Import error onedrive_integration: {e}")

st.header("3. API Test")

if st.button("🧪 Test OpenAI API Call"):
    try:
        from cli_manuscript_assistant import call_model
        
        with st.spinner("Testing API call..."):
            response = call_model(
                "Zeg alleen 'API werkt!' in het Nederlands.",
                provider="openai",
                model="gpt-4o-mini",
                temperature=0.1
            )
        
        st.success(f"✅ API Response: {response}")
        
    except Exception as e:
        st.error(f"❌ API Test failed: {str(e)}")

st.header("4. File Upload Test")

uploaded_file = st.file_uploader("Upload een test bestand", type=['txt', 'md'])

if uploaded_file:
    st.success(f"✅ Bestand geüpload: {uploaded_file.name}")
    
    # Test file reading
    try:
        from cli_manuscript_assistant import read_file
        
        # Write temp file
        temp_path = Path(f"temp_{uploaded_file.name}")
        temp_path.write_bytes(uploaded_file.getvalue())
        
        # Read it back
        content = read_file(temp_path)
        
        st.success(f"✅ Bestand gelezen: {len(content)} karakters")
        st.text_area("Inhoud preview:", content[:500] + "..." if len(content) > 500 else content)
        
        # Clean up
        temp_path.unlink()
        
    except Exception as e:
        st.error(f"❌ File reading error: {e}")

st.header("5. OneDrive Test")

if st.button("🧪 Test OneDrive"):
    try:
        from onedrive_integration import OneDriveManager
        
        onedrive = OneDriveManager()
        
        if onedrive.is_onedrive_available():
            st.success(f"✅ OneDrive gevonden: {onedrive.base_path}")
        else:
            st.warning("⚠️ OneDrive niet gevonden")
            
    except Exception as e:
        st.error(f"❌ OneDrive test error: {e}")

st.header("6. Complete Analysis Test")

if st.button("🚀 Test Complete Analysis (Small)"):
    try:
        from cli_manuscript_assistant import call_model, split_sections, p_outline
        
        test_text = """
        # Hoofdstuk 1: De Ontmoeting
        
        Maria liep door de donkere straat. De wind floot door de bomen.
        
        "Wie is daar?" riep ze uit.
        
        Een schaduw bewoog achter de hoek.
        """
        
        with st.spinner("Testing analysis pipeline..."):
            # Test 1: Split sections
            sections = split_sections(test_text)
            st.success(f"✅ Sections split: {len(sections)} secties gevonden")
            
            # Test 2: API call
            outline = call_model(
                p_outline(test_text),
                provider="openai", 
                model="gpt-4o-mini",
                temperature=0.2
            )
            
            st.success("✅ Analysis pipeline werkt!")
            st.text_area("Outline result:", outline)
            
    except Exception as e:
        st.error(f"❌ Analysis test failed: {str(e)}")
        st.exception(e)