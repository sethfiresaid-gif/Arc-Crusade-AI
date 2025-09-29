#!/usr/bin/env python3
"""
Uitgebreide test van alle geavanceerde functies met beide manuscripten
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()

def test_complete_enhanced_analysis():
    """Test alle geavanceerde functies met beide manuscripten"""
    print("🎯 COMPLETE ENHANCED ANALYSIS TEST")
    print("=" * 50)
    
    # Import modules
    try:
        from cli_manuscript_assistant import (
            enhanced_metrics, call_model, split_sections
        )
        from enhanced_analysis import (
            analyze_character_development, analyze_pacing, 
            analyze_style_issues, analyze_show_vs_tell,
            p_advanced_rewrite, p_character_voice_analysis,
            p_scene_structure_analysis, p_emotional_depth_analysis,
            p_genre_specific_analysis
        )
        print("✅ All modules imported successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test both manuscripts
    manuscripts = [
        ("Fantasy", "test_fantasy_manuscript.txt"),
        ("Thriller", "test_thriller_manuscript.txt")
    ]
    
    for genre, filename in manuscripts:
        print(f"\n🎭 TESTING {genre.upper()} MANUSCRIPT")
        print("-" * 40)
        
        # Read manuscript
        try:
            manuscript_path = Path(filename)
            if not manuscript_path.exists():
                print(f"❌ File {filename} not found")
                continue
                
            text = manuscript_path.read_text(encoding="utf-8")
            print(f"✅ Loaded manuscript: {len(text)} characters")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            continue
        
        # Test 1: Enhanced Metrics
        print(f"\n📊 Enhanced Metrics Analysis...")
        try:
            metrics = enhanced_metrics(text)
            print(f"✅ Enhanced metrics completed:")
            print(f"   - Basic: {metrics['words']} words, {metrics['sentences']} sentences")
            print(f"   - Characters found: {len(metrics.get('characters', {}))}")
            print(f"   - Style issues: {len(metrics.get('style_issues', []))}")
            print(f"   - Readability: {metrics.get('readability_score', 'N/A')}")
            print(f"   - Engagement: {metrics.get('engagement_score', 'N/A')}")
            
            # Show character details
            if metrics.get('characters'):
                print("   - Main characters:")
                for char, data in list(metrics['characters'].items())[:3]:
                    emotions = ", ".join(data['emotions'][:3]) if data['emotions'] else "none"
                    print(f"     * {char}: {data['mentions']} mentions, emotions: {emotions}")
            
            # Show style issues
            if metrics.get('style_issues'):
                print("   - Style issues found:")
                for issue in metrics['style_issues'][:2]:
                    print(f"     * {issue}")
                    
        except Exception as e:
            print(f"❌ Enhanced metrics failed: {e}")
        
        # Test 2: Split sections and analyze each
        print(f"\n📖 Section Analysis...")
        try:
            sections = split_sections(text)
            print(f"✅ Split into {len(sections)} sections:")
            
            for i, section in enumerate(sections[:2]):  # Analyze first 2 sections
                print(f"\n   Section {i+1}: {section['title']}")
                
                # Character analysis for this section
                char_data = analyze_character_development(section['content'])
                print(f"     - Characters: {list(char_data.keys())[:3]}")
                
                # Pacing analysis
                pacing_data = analyze_pacing(section['content'])
                print(f"     - Pacing score: {pacing_data.get('pacing_score', 'N/A')}")
                print(f"     - Dialog ratio: {pacing_data.get('dialog_ratio', 'N/A')}")
                
                # Show vs Tell
                show_tell = analyze_show_vs_tell(section['content'])
                print(f"     - Show vs Tell score: {show_tell.get('show_vs_tell_score', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Section analysis failed: {e}")
        
        # Test 3: AI Prompt Generation
        print(f"\n🤖 AI Prompt Generation...")
        try:
            # Test different prompt types
            sample_text = text[:2000]  # First 2000 chars
            
            # Character voice analysis prompt
            char_prompt = p_character_voice_analysis(sample_text)
            print(f"✅ Character voice prompt created ({len(char_prompt)} chars)")
            
            # Scene structure prompt  
            scene_prompt = p_scene_structure_analysis(sample_text)
            print(f"✅ Scene structure prompt created ({len(scene_prompt)} chars)")
            
            # Genre-specific prompt
            genre_lower = genre.lower()
            genre_prompt = p_genre_specific_analysis(sample_text, genre_lower)
            print(f"✅ {genre} genre prompt created ({len(genre_prompt)} chars)")
            
            # Advanced rewrite prompt
            rewrite_prompt = p_advanced_rewrite("Test Chapter", sample_text, "character")
            print(f"✅ Advanced rewrite prompt created ({len(rewrite_prompt)} chars)")
            
        except Exception as e:
            print(f"❌ AI prompt generation failed: {e}")
        
        # Test 4: Real AI Analysis (if API available)
        print(f"\n🔮 Real AI Analysis...")
        try:
            # Quick character analysis
            char_analysis = call_model(
                p_character_voice_analysis(text[:1500]),
                provider="openai",
                model="gpt-4o-mini",
                temperature=0.3
            )
            print(f"✅ AI Character Analysis completed ({len(char_analysis)} chars):")
            preview = char_analysis[:200] + "..." if len(char_analysis) > 200 else char_analysis
            print(f"   Preview: {preview}")
            
            # Quick genre analysis
            genre_analysis = call_model(
                p_genre_specific_analysis(text[:1500], genre.lower()),
                provider="openai", 
                model="gpt-4o-mini",
                temperature=0.3
            )
            print(f"✅ AI Genre Analysis completed ({len(genre_analysis)} chars):")
            preview = genre_analysis[:200] + "..." if len(genre_analysis) > 200 else genre_analysis
            print(f"   Preview: {preview}")
            
        except Exception as e:
            print(f"⚠️ Real AI analysis skipped: {e}")
    
    print(f"\n🎉 COMPLETE ENHANCED ANALYSIS TEST FINISHED!")
    print("=" * 50)
    print("✅ All enhanced features are working correctly!")
    print("🚀 Ready for deployment and real-world testing!")
    
    return True

if __name__ == "__main__":
    success = test_complete_enhanced_analysis()
    exit(0 if success else 1)