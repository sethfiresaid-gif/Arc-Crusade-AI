#!/usr/bin/env python3
"""
Setup script voor Arc Crusade Client Export Configuratie
Dit script helpt je bij het instellen van georganiseerde klant exports
"""

import os
import json
from pathlib import Path
from onedrive_integration import OneDriveManager

def main():
    print("🚀 Arc Crusade Client Export Setup")
    print("=" * 50)
    print()
    
    # Initialiseer OneDrive Manager
    onedrive = OneDriveManager()
    
    # Controleer OneDrive beschikbaarheid
    if not onedrive.is_onedrive_available():
        print("❌ OneDrive niet gevonden op dit systeem")
        print("💡 OneDrive is vereist voor georganiseerde client exports")
        return
    
    print("✅ OneDrive gevonden:")
    for i, path in enumerate(onedrive.onedrive_paths):
        print(f"   {i+1}. {path}")
    print()
    
    # Vraag om custom export path
    print("📂 Export Locatie Configuratie")
    print("-" * 30)
    
    default_path = r"G:\Mijn Drive\The arc crusade\Export Arc Crusade Program"
    export_path = input(f"Voer je export pad in (Enter voor standaard):\n[{default_path}]\n> ").strip()
    
    if not export_path:
        export_path = default_path
    
    export_path = Path(export_path)
    
    # Controleer/maak export directory
    try:
        export_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Export pad geconfigureerd: {export_path}")
        
        # Test door een voorbeeld client folder te maken
        test_client = "Test_Client_Setup"
        test_folder = onedrive.create_client_folder(test_client)
        
        if test_folder:
            print(f"✅ Test client folder gemaakt: {test_folder}")
            
            # Vraag om test folder te behouden of verwijderen
            keep_test = input("\n🗑️ Test folder behouden? (y/N): ").lower()
            if keep_test != 'y':
                import shutil
                shutil.rmtree(test_folder)
                print("🗑️ Test folder verwijderd")
        
    except Exception as e:
        print(f"❌ Fout bij configureren export pad: {e}")
        return
    
    # Sla configuratie op
    config = {
        "export_path": str(export_path),
        "onedrive_paths": [str(p) for p in onedrive.onedrive_paths],
        "setup_date": str(Path().cwd()),
        "version": "1.0"
    }
    
    config_file = Path("client_export_config.json")
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print()
    print("🎉 Setup Voltooid!")
    print("=" * 20)
    print(f"📄 Configuratie opgeslagen: {config_file}")
    print(f"📁 Client exports gaan naar: {export_path}")
    print()
    print("💡 Gebruik Tips:")
    print("  • CLI: python cli_manuscript_assistant.py manuscript.docx --client-name \"Jan Janssen\" --export-path \"{}\".format(export_path)")
    print("  • Streamlit: Vul client naam in bij upload voor automatische organisatie")
    print()
    print("📋 Voor elke klant wordt een folder structuur gemaakt:")
    print("   01_Original_Manuscript/")
    print("   02_Analysis_Reports/") 
    print("   03_Rewritten_Sections/")
    print("   04_JSON_Data/")
    print("   05_Complete_Archive/")
    print("   06_Notes_And_Feedback/")
    print()
    print("🔄 Je kunt dit script altijd opnieuw draaien om de configuratie te wijzigen.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Setup geannuleerd")
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")
        print("💬 Neem contact op voor ondersteuning")