#!/usr/bin/env python3
"""
Test de nieuwe geavanceerde functies van de manuscript assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_enhanced_features():
    """Test de nieuwe geavanceerde functies"""
    print("🚀 Testing Enhanced Arc Crusade Manuscript Assistant...")
    
    # Test 1: Import enhanced modules
    print("\n📦 Test 1: Importing enhanced modules...")
    try:
        from enhanced_analysis import (
            analyze_character_development, analyze_pacing, analyze_style_issues,
            p_advanced_rewrite, p_character_voice_analysis
        )
        from cli_manuscript_assistant import enhanced_metrics
        print("✅ All enhanced modules imported successfully")
    except Exception as e:
        print(f"❌ Enhanced import failed: {e}")
        return False
    
    # Test 2: Read enhanced test manuscript
    print("\n📖 Test 2: Testing with enhanced manuscript...")
    manuscript_path = Path("test_manuscript.txt")
    
    if not manuscript_path.exists():
        # Create a better test manuscript for enhanced analysis
        enhanced_text = """
        Hoofdstuk 1: De Ontmoeting
        
        Sarah keek nerveus naar de donkere lucht. Haar handen trilden terwijl ze de brief vasthield.
        
        "Ben je er klaar voor?" fluisterde Tom, zijn stem gespannen van de adrenaline.
        
        Ze knikte, hoewel haar hart bonkte als een razende. Dit was het moment waar ze maanden naar hadden toegewerkt.
        
        Opeens scheurde een bliksemflits door de hemel. Sarah rook de metalige geur van de naderende storm.
        
        "Nu!" riep Tom.
        
        Ze renden samen naar het oude huis, hun voetstappen echoden op de natte straatstenen. Sarah voelde de kou door haar kleren snijden.
        
        Hoofdstuk 2: Het Mysterie
        
        Binnen was het donker en stil. Te stil, dacht Sarah. Ze was bang, maar probeerde het niet te laten merken.
        
        "Hoor je dat?" vroeg Tom zachtjes.
        
        Ergens in het huis kraakte een plankenvloer. Sarah greep Tom's arm steviger vast. Haar ogen priemden door de duisternis.
        
        Een deur sloeg dicht. Dan nog een. Het geluid echode door de lege kamers als spoken uit het verleden.
        
        "We zijn niet alleen," fluisterde Sarah, haar stem nauwelijks hoorbaar.
        
        Tom knikte. Hij voelde het ook - een aanwezigheid, koud en dreigend, die om hen heen cirkelde.
        
        Plotseling lichtte een kaars op in de verte. Iemand - of iets - was hier.
        """
        
        manuscript_path.write_text(enhanced_text, encoding="utf-8")
        print("✅ Enhanced test manuscript created")
    
    text = manuscript_path.read_text(encoding="utf-8")
    
    # Test 3: Character analysis
    print("\n👥 Test 3: Character development analysis...")
    try:
        char_analysis = analyze_character_development(text)
        print(f"✅ Found {len(char_analysis)} characters:")
        for char, data in char_analysis.items():
            print(f"   - {char}: {data['mentions']} mentions, {len(data['emotions'])} emotions")
    except Exception as e:
        print(f"❌ Character analysis failed: {e}")
    
    # Test 4: Pacing analysis
    print("\n🎭 Test 4: Pacing analysis...")
    try:
        pacing_data = analyze_pacing(text)
        print("✅ Pacing analysis completed:")
        for key, value in pacing_data.items():
            print(f"   - {key}: {value}")
    except Exception as e:
        print(f"❌ Pacing analysis failed: {e}")
    
    # Test 5: Style issues
    print("\n⚠️ Test 5: Style issues detection...")
    try:
        style_issues = analyze_style_issues(text)
        print(f"✅ Found {len(style_issues)} style issues:")
        for issue in style_issues[:3]:  # Show first 3
            print(f"   - {issue}")
    except Exception as e:
        print(f"❌ Style analysis failed: {e}")
    
    # Test 6: Enhanced metrics
    print("\n📊 Test 6: Enhanced metrics...")
    try:
        metrics = enhanced_metrics(text)
        print("✅ Enhanced metrics calculated:")
        print(f"   - Basic metrics: {metrics['words']} words, {metrics['sentences']} sentences")
        print(f"   - Readability: {metrics.get('readability_score', 'N/A')}")
        print(f"   - Engagement: {metrics.get('engagement_score', 'N/A')}")
        print(f"   - Characters: {len(metrics.get('characters', {}))}")
        print(f"   - Style issues: {len(metrics.get('style_issues', []))}")
    except Exception as e:
        print(f"❌ Enhanced metrics failed: {e}")
    
    # Test 7: Advanced AI prompts (if API available)
    try:
        from cli_manuscript_assistant import call_model
        print("\n🤖 Test 7: Advanced AI prompts...")
        
        # Test character voice analysis prompt
        char_prompt = p_character_voice_analysis(text[:1000])
        print("✅ Character voice analysis prompt created")
        
        # Test advanced rewrite prompt
        advanced_rewrite_prompt = p_advanced_rewrite("Test Chapter", text[:1000], "character")
        print("✅ Advanced rewrite prompt created")
        
        # Quick API test
        api_test = call_model(
            "Geef 1 kort compliment over deze tekst: " + text[:200],
            provider="openai",
            model="gpt-4o-mini"
        )
        print(f"✅ API test successful: {api_test[:100]}...")
        
    except Exception as e:
        print(f"⚠️ Advanced AI prompts test: {e}")
    
    print(f"\n🎉 Enhanced features testing completed!")
    return True

if __name__ == "__main__":
    success = test_enhanced_features()
    exit(0 if success else 1)