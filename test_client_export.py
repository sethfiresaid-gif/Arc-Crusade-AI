#!/usr/bin/env python3
"""
Test script voor client export functionaliteit
"""

from pathlib import Path
from onedrive_integration import OneDriveManager
import json
from datetime import datetime

def test_client_export():
    print("🧪 Test Client Export Functionaliteit")
    print("=" * 40)
    
    # Initialiseer OneDrive Manager
    onedrive = OneDriveManager()
    
    # Test OneDrive detectie
    print(f"OneDrive gevonden: {onedrive.is_onedrive_available()}")
    if onedrive.onedrive_paths:
        print(f"OneDrive paden: {onedrive.onedrive_paths}")
    
    # Test custom export path
    test_export_path = Path.cwd() / "test_exports"
    print(f"\nTest export path: {test_export_path}")
    
    if onedrive.set_custom_export_path(test_export_path):
        print("✅ Custom export path ingesteld")
    else:
        print("❌ Custom export path mislukt")
        return
    
    # Test client folder aanmaken
    test_client_name = "Test_Client_Demo"
    test_manuscript = "sample_manuscript.txt"
    
    print(f"\nClient folder aanmaken voor: {test_client_name}")
    client_folder = onedrive.create_client_folder(test_client_name, test_manuscript)
    
    if client_folder:
        print(f"✅ Client folder gemaakt: {client_folder}")
        
        # Test data voor analyse
        test_analysis_data = {
            "title": "Test Manuscript Analysis",
            "genre_analysis": {"overall_genre_alignment": 8},
            "character_analysis": {"average_development_score": 7.5},
            "plot_analysis": {"overall_structure_score": 8.2},
            "sections": [
                {"title": "Hoofdstuk 1", "score": 8.0},
                {"title": "Hoofdstuk 2", "score": 7.5}
            ]
        }
        
        test_report = """# Test Manuscript Analysis Report

## Samenvatting
Dit is een test analyse rapport voor demonstratie doeleinden.

## Genre Analyse
Het manuscript toont sterke fantasy elementen met goede wereld ontwikkeling.

## Karakter Ontwikkeling  
Karakters tonen groei door het verhaal heen.

## Aanbevelingen
1. Versterk de opening scene
2. Ontwikkel meer dialoog variatie
3. Verbeter pacing in het midden
"""

        # Test origineel bestand maken
        original_file = Path("test_manuscript.txt")
        original_file.write_text("Dit is een test manuscript voor de Arc Crusade AI analyse.", encoding="utf-8")
        
        # Test client export
        print("\nTest client export...")
        success = onedrive.save_analysis_to_client_folder(
            client_name=test_client_name,
            analysis_data=test_analysis_data,
            report_content=test_report,
            original_file=original_file,
            rewrite_files=[],
            timestamp="20250929-120000"
        )
        
        if success:
            print("✅ Client export succesvol!")
            
            # Toon folder structuur
            print("\n📁 Gemaakte folder structuur:")
            for item in client_folder.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(client_folder)
                    print(f"   📄 {relative_path}")
                elif item.is_dir() and item != client_folder:
                    relative_path = item.relative_to(client_folder)
                    print(f"   📂 {relative_path}/")
        else:
            print("❌ Client export mislukt")
            
        # Cleanup test files
        if original_file.exists():
            original_file.unlink()
            
    else:
        print("❌ Client folder aanmaken mislukt")
    
    print(f"\n📍 Test export locatie: {test_export_path}")
    print("🔄 Je kunt de test export folder verwijderen na inspectie")

if __name__ == "__main__":
    try:
        test_client_export()
    except Exception as e:
        print(f"❌ Test fout: {e}")
        import traceback
        traceback.print_exc()