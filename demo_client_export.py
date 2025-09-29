#!/usr/bin/env python3
"""
Demo script voor client export functionaliteit zonder AI
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from onedrive_integration import OneDriveManager

def demo_client_export():
    print("🎯 Demo: Client Export Functionaliteit")
    print("=" * 50)
    
    # Initialiseer OneDrive Manager
    onedrive = OneDriveManager()
    
    # Setup custom export path
    export_path = r"G:\Mijn Drive\The arc crusade\Export Arc Crusade Program"
    if onedrive.set_custom_export_path(export_path):
        print(f"✅ Export pad ingesteld: {export_path}")
    else:
        print(f"❌ Export pad niet toegankelijk: {export_path}")
        return
    
    # Demo client informatie
    client_name = "Demo Klant Test"
    manuscript_file = Path("test_manuscript.txt")
    
    # Mock analysis data (alsof AI analyse heeft plaatsgevonden)
    mock_analysis_data = {
        "title": f"Manuscript Analysis voor {client_name}",
        "genre_analysis": {"overall_genre_alignment": 8.5},
        "character_analysis": {"average_development_score": 7.8},
        "plot_analysis": {"overall_structure_score": 8.2},
        "sections": [
            {
                "title": "Hoofdstuk 1: De Vreemdeling",
                "score": 8.0,
                "feedback": "Sterke opening, goede karakterintroductie"
            },
            {
                "title": "Hoofdstuk 2: De Ontmoeting", 
                "score": 7.5,
                "feedback": "Goede spanning, dialoog kan verbeterd worden"
            }
        ],
        "recommendations": [
            "Versterk dialoog variatie",
            "Verbeter pacing in het midden",
            "Ontwikkel meer sensory details"
        ]
    }
    
    # Mock rapport content
    mock_report = f"""# Manuscript Analyse Rapport - {client_name}

**Datum**: {datetime.now().strftime("%d %B %Y")}
**Manuscript**: {manuscript_file.name}

## 📋 Executieve Samenvatting

Dit manuscript toont sterke potentie met een score van **8.2/10** voor de overall structuur. 
De karakterontwikkeling is goed ontwikkeld (7.8/10) en de genre-alignering is uitstekend (8.5/10).

## 🎯 Analyse per Hoofdstuk

### Hoofdstuk 1: De Vreemdeling
- **Score**: 8.0/10
- **Feedback**: Sterke opening, goede karakterintroductie
- **Aanbevelingen**: Uitbreiden van wereld-beschrijvingen

### Hoofdstuk 2: De Ontmoeting  
- **Score**: 7.5/10
- **Feedback**: Goede spanning, dialoog kan verbeterd worden
- **Aanbevelingen**: Meer emotionele diepte in conversaties

## 🚀 Aanbevelingen voor Verbetering

1. **Dialoog Variatie**: Versterk de unieke stemmen van karakters
2. **Pacing**: Verbeter de flow in het middendeel
3. **Sensory Details**: Voeg meer zintuiglijke beschrijvingen toe

## 📊 Scores Samenvatting

- Genre Alignering: 8.5/10
- Karakter Ontwikkeling: 7.8/10  
- Plot Structuur: 8.2/10
- **Gemiddelde**: 8.2/10

---
*Gegenereerd door Arc Crusade Manuscript Assistant*
*Professional Manuscript Analysis Service*
"""

    print(f"\n📝 Bezig met export voor: {client_name}")
    
    # Timestamp voor deze analyse
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Client export uitvoeren
    success = onedrive.save_analysis_to_client_folder(
        client_name=client_name,
        analysis_data=mock_analysis_data,
        report_content=mock_report,
        original_file=manuscript_file,
        rewrite_files=[],  # Geen rewrites voor deze demo
        timestamp=timestamp
    )
    
    if success:
        print(f"\n🎉 Client export succesvol voltooid!")
        
        # Toon wat er gemaakt is
        client_folder = onedrive.client_folders.get(client_name)
        if client_folder:
            print(f"\n📁 Client folder gemaakt: {client_folder}")
            print("\n📋 Folder inhoud:")
            
            for item in client_folder.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(client_folder)
                    file_size = item.stat().st_size
                    print(f"   📄 {relative_path} ({file_size} bytes)")
                elif item.is_dir() and item != client_folder:
                    relative_path = item.relative_to(client_folder)
                    print(f"   📂 {relative_path}/")
        
        print(f"\n✨ Voor elke klant krijg je nu:")
        print("   • Complete georganiseerde folder")
        print("   • Alle analyse bestanden")
        print("   • ZIP archief voor eenvoudige levering") 
        print("   • Professionele presentatie")
        print("   • Ruimte voor communicatie")
        
    else:
        print("❌ Client export mislukt")

if __name__ == "__main__":
    try:
        demo_client_export()
    except Exception as e:
        print(f"\n❌ Demo fout: {e}")
        import traceback
        traceback.print_exc()