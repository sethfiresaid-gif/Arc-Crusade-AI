#!/usr/bin/env python3
"""
Test script voor OneDrive integratie
"""

import sys
from pathlib import Path
import json
import time

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_onedrive_detection():
    """Test OneDrive detectie"""
    print("🔍 Testing OneDrive detection...")
    
    try:
        from onedrive_integration import OneDriveManager
        onedrive = OneDriveManager()
        
        if onedrive.is_onedrive_available():
            print(f"✅ OneDrive gevonden: {onedrive.base_path}")
            
            # Test folder setup
            success, message = onedrive.setup_onedrive_structure()
            print(f"📁 Folder setup: {message}")
            
            if success:
                print("✅ OneDrive integratie is klaar!")
                return True
            else:
                print("❌ OneDrive setup mislukt")
                return False
        else:
            print("⚠️ OneDrive niet gevonden op dit systeem")
            return False
            
    except ImportError:
        print("❌ OneDrive integratie module niet gevonden")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_save_analysis():
    """Test het opslaan van analyse data"""
    print("\n📝 Testing analysis saving...")
    
    try:
        from cli_manuscript_assistant import save_analysis_with_onedrive
        
        # Create test data
        test_analysis = {
            'title': 'Test Analysis',
            'outline': 'Dit is een test outline',
            'top_issues': 'Test issues',
            'improvement_plan': 'Test plan',
            'sections': [
                {
                    'title': 'Test Section 1',
                    'metrics': {'words': 100, 'sentences': 10},
                    'rubric': 'Test feedback',
                    'rewrite': 'Test rewrite'
                }
            ]
        }
        
        test_report = "# Test Report\n\nDit is een test rapport."
        timestamp = time.strftime("%Y%m%d-%H%M%S-TEST")
        
        success, message = save_analysis_with_onedrive(
            analysis_data=test_analysis,
            report_content=test_report,
            rewrite_files=[],
            timestamp=timestamp
        )
        
        if success:
            print(f"✅ Test save succesvol: {message}")
            return True
        else:
            print(f"❌ Test save mislukt: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Save test error: {e}")
        return False

def test_streamlit_integration():
    """Test Streamlit integration"""
    print("\n🌐 Testing Streamlit integration...")
    
    try:
        # Test import
        from streamlit_app import main
        print("✅ Streamlit app import succesvol")
        
        # Check if OneDrive variables are properly handled
        try:
            import streamlit as st
            print("✅ Streamlit beschikbaar")
        except ImportError:
            print("ℹ️ Streamlit niet beschikbaar (normaal tijdens CLI test)")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit integration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Arc Crusade AI - OneDrive Integration Test")
    print("=" * 50)
    
    tests = [
        ("OneDrive Detection", test_onedrive_detection),
        ("Save Analysis", test_save_analysis),
        ("Streamlit Integration", test_streamlit_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n📊 Test Results:")
    print("=" * 30)
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Alle tests geslaagd! OneDrive integratie is klaar.")
    else:
        print("⚠️ Sommige tests gefaald. Check de configuratie.")

if __name__ == "__main__":
    main()