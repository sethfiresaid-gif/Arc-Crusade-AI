#!/usr/bin/env python3
"""
Minimal Streamlit test app
"""
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="📚 Arc Crusade Test",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Arc Crusade Manuscript Assistant - Test Version")

st.success("✅ Streamlit is working correctly!")

st.markdown("""
## 🧪 Basic Functionality Test

This is a minimal version to test if Streamlit is working properly.
""")

# Test basic imports
try:
    from cli_manuscript_assistant import rough_metrics, call_model
    st.success("✅ Basic CLI functions imported successfully")
except Exception as e:
    st.error(f"❌ CLI import failed: {e}")

# Test enhanced imports
try:
    from enhanced_analysis import analyze_character_development
    st.success("✅ Enhanced analysis imported successfully")
except Exception as e:
    st.error(f"❌ Enhanced analysis import failed: {e}")

# Test API config
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        st.success(f"✅ API key found: {api_key[:10]}...")
    else:
        st.warning("⚠️ No API key found in environment")
except Exception as e:
    st.error(f"❌ API config error: {e}")

# File upload test
uploaded_file = st.file_uploader("Test file upload", type=['txt'])
if uploaded_file:
    content = uploaded_file.read().decode()
    st.text_area("File content:", content[:500], height=200)
    st.success("✅ File upload working!")

st.markdown("---")
st.info("If you can see this interface, the basic Streamlit functionality is working correctly.")