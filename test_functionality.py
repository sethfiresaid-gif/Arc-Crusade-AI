#!/usr/bin/env python3
"""
Test de core manuscript assistant functionaliteit
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from cli_manuscript_assistant import call_model, read_file, split_sections, rough_metrics

load_dotenv()

def test_basic_functionality():
    """Test basis functionaliteit van de manuscript assistant"""
    print("🧪 Testing Arc Crusade Manuscript Assistant...")
    
    # Test 1: File reading
    print("\n📖 Test 1: Reading test manuscript...")
    try:
        manuscript_path = Path("test_manuscript.txt")
        content = read_file(manuscript_path)
        print(f"✅ File read successfully ({len(content)} characters)")
    except Exception as e:
        print(f"❌ File reading failed: {e}")
        return False
    
    # Test 2: Split sections
    print("\n📄 Test 2: Splitting sections...")
    try:
        sections = split_sections(content)
        print(f"✅ Found {len(sections)} sections")
        for i, section in enumerate(sections[:3]):  # Show first 3
            preview = section['content'][:100] + "..." if len(section['content']) > 100 else section['content']
            print(f"   Section {i+1}: {preview}")
    except Exception as e:
        print(f"❌ Section splitting failed: {e}")
        return False
    
    # Test 3: Basic metrics
    print("\n📊 Test 3: Calculating metrics...")
    try:
        metrics = rough_metrics(content)
        print(f"✅ Metrics calculated:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Metrics calculation failed: {e}")
        return False
    
    # Test 4: OpenAI API call (simple test)
    print("\n🤖 Test 4: Testing OpenAI API...")
    try:
        response = call_model(
            prompt="Geef een korte samenvatting (max 50 woorden) van deze tekst: " + content[:500],
            provider="openai",
            model="gpt-4o-mini",
            temperature=0.3
        )
        print(f"✅ API call successful!")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False
    
    print(f"\n🎉 All tests passed! The manuscript assistant is working correctly.")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)