#!/usr/bin/env python3
"""
Test script om API key configuratie te verifiëren
"""
import os
from dotenv import load_dotenv

# Zelfde setup als in de main app
load_dotenv()

# Test Streamlit import
try:
    import streamlit as st
    HAS_STREAMLIT = True
    print("✅ Streamlit import: OK")
except ImportError:
    HAS_STREAMLIT = False
    print("❌ Streamlit import: FAILED")

def get_api_config():
    """Get API configuration from Streamlit secrets or environment variables"""
    def get_secret(key, default=None):
        # Try Streamlit secrets first
        if HAS_STREAMLIT:
            try:
                # In test context, st.secrets might not work, so we skip
                pass
            except (KeyError, FileNotFoundError, AttributeError):
                pass
        
        # Fallback to environment variables
        return os.getenv(key, default)
    
    config = {
        'api_key': get_secret("OPENAI_API_KEY"),
        'org': get_secret("OPENAI_ORG_ID"),
        'project': get_secret("OPENAI_PROJECT"),
        'base': get_secret("OPENAI_BASE")
    }
    
    return config

if __name__ == "__main__":
    print("🔍 Testing API Configuration...")
    
    config = get_api_config()
    
    print("\n📋 Configuration:")
    for key, value in config.items():
        if value:
            if key == 'api_key':
                masked = value[:7] + "..." + value[-4:] if len(value) > 11 else "***"
                print(f"  {key}: {masked}")
            else:
                print(f"  {key}: {value}")
        else:
            print(f"  {key}: ❌ NOT SET")
    
    # Test OpenAI import
    print(f"\n🤖 Testing OpenAI import...")
    try:
        from openai import OpenAI
        print("✅ OpenAI import: OK")
        
        if config['api_key']:
            print("✅ API Key: FOUND")
            
            # Test client creation (without actual API call)
            client_args = {'api_key': config['api_key']}
            if config['org']:
                client_args['organization'] = config['org']
            if config['project']:
                client_args['project'] = config['project']
            
            client = OpenAI(**client_args)
            print("✅ OpenAI Client: CREATED")
        else:
            print("❌ API Key: NOT FOUND")
            
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
    
    print(f"\n🎯 Status: {'✅ READY' if config['api_key'] else '❌ NEEDS API KEY'}")