#!/usr/bin/env python3
"""
OneDrive integration voor Arc Crusade Manuscript Assistant
Detecteert OneDrive folders en maakt daar output directories
"""
import os
from pathlib import Path
import json
import shutil
from datetime import datetime

class OneDriveManager:
    def __init__(self):
        self.onedrive_paths = self.detect_onedrive_paths()
        self.zapier_manuscript_folder = None
        self.output_folder = None
        
    def detect_onedrive_paths(self):
        """Detecteer mogelijke OneDrive paden"""
        possible_paths = []
        
        # Standaard OneDrive locaties
        user_profile = Path.home()
        onedrive_locations = [
            user_profile / "OneDrive",
            user_profile / "OneDrive - Personal", 
            user_profile / "OneDrive - Business",
            Path(os.environ.get('OneDrive', '')),
            Path(os.environ.get('OneDriveConsumer', '')),
            Path(os.environ.get('OneDriveCommercial', ''))
        ]
        
        for path in onedrive_locations:
            if path.exists() and path.is_dir():
                possible_paths.append(path)
                print(f"✅ OneDrive gevonden: {path}")
        
        return possible_paths
    
    def is_onedrive_available(self):
        """Check if OneDrive is available"""
        return len(self.onedrive_paths) > 0
    
    @property 
    def base_path(self):
        """Get the primary OneDrive path"""
        return self.onedrive_paths[0] if self.onedrive_paths else None
    
    def setup_onedrive_structure(self):
        """Setup OneDrive folder structure for Arc Crusade AI"""
        if not self.is_onedrive_available():
            return False, "OneDrive niet beschikbaar"
        
        try:
            # Create output folder structure
            output_folder = self.create_output_folder()
            if output_folder:
                return True, f"OneDrive structuur aangemaakt in: {output_folder}"
            else:
                return False, "Kon output folder niet aanmaken"
        except Exception as e:
            return False, f"Error bij setup: {str(e)}"
    
    def find_zapier_manuscript_folder(self, folder_name="manuscripts"):
        """Zoek naar de Zapier manuscript folder"""
        for onedrive_path in self.onedrive_paths:
            potential_folder = onedrive_path / folder_name
            if potential_folder.exists():
                self.zapier_manuscript_folder = potential_folder
                print(f"✅ Zapier manuscript folder gevonden: {potential_folder}")
                return potential_folder
            
            # Zoek ook in subfolders
            for subfolder in onedrive_path.rglob(folder_name):
                if subfolder.is_dir():
                    self.zapier_manuscript_folder = subfolder
                    print(f"✅ Zapier manuscript folder gevonden: {subfolder}")
                    return subfolder
        
        print("⚠️ Zapier manuscript folder niet gevonden")
        return None
    
    def create_output_folder(self, base_name="Arc-Crusade-Outputs"):
        """Maak output folder in OneDrive"""
        if not self.onedrive_paths:
            print("❌ Geen OneDrive gevonden")
            return None
        
        # Gebruik de eerste beschikbare OneDrive
        onedrive_root = self.onedrive_paths[0]
        output_folder = onedrive_root / base_name
        
        # Maak de folder structuur
        output_folder.mkdir(exist_ok=True)
        (output_folder / "reports").mkdir(exist_ok=True)
        (output_folder / "rewrites").mkdir(exist_ok=True)
        (output_folder / "json-data").mkdir(exist_ok=True)
        (output_folder / "archives").mkdir(exist_ok=True)
        
        self.output_folder = output_folder
        print(f"✅ Output folder aangemaakt: {output_folder}")
        
        # Maak README voor de folder
        readme_content = f"""# Arc Crusade Manuscript Assistant - Outputs

Deze folder bevat de resultaten van je manuscript analyses.

## Folder Structuur:
- `reports/` - Volledige analyse rapporten (.md)
- `rewrites/` - Herschreven secties (.md) 
- `json-data/` - Gestructureerde data (.json)
- `archives/` - ZIP archieven van complete analyses

## Automatisch gegenereerd op: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Deze folder is gekoppeld aan je Zapier workflow voor manuscript verwerking.
"""
        
        (output_folder / "README.md").write_text(readme_content, encoding="utf-8")
        return output_folder
    
    def save_analysis_to_onedrive(self, analysis_data, report_content, rewrite_files=None, timestamp=None):
        """Sla analyse resultaten op in OneDrive"""
        # Ensure we have output folder setup
        if not self.output_folder:
            self.create_output_folder()
        
        if not self.output_folder:
            return False
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        try:
            # 1. Sla rapport op
            report_file = self.output_folder / "reports" / f"analysis-{timestamp}.md"
            report_file.write_text(report_content, encoding="utf-8")
            
            # 2. Sla JSON data op
            json_file = self.output_folder / "json-data" / f"data-{timestamp}.json"
            json_file.write_text(json.dumps(analysis_data, ensure_ascii=False, indent=2), encoding="utf-8")
            
            # 3. Sla herschrijvingen op
            if rewrite_files:
                rewrites_folder = self.output_folder / "rewrites" / f"session-{timestamp}"
                rewrites_folder.mkdir(exist_ok=True)
                
                for rewrite_file in rewrite_files:
                    if rewrite_file.exists():
                        # Copy rewrite file to OneDrive
                        dest_file = rewrites_folder / rewrite_file.name
                        dest_file.write_text(rewrite_file.read_text(encoding="utf-8"), encoding="utf-8")
            
            # 4. Maak ZIP archief
            self.create_zip_archive(timestamp, report_content, analysis_data, rewrite_files or [])
            
            return True
            
        except Exception as e:
            print(f"❌ Fout bij opslaan naar OneDrive: {e}")
            return False
    
    def create_zip_archive(self, timestamp, report_content, analysis_data, rewrite_files):
        """Maak ZIP archief van alle bestanden"""
        try:
            import zipfile
            
            archive_file = self.output_folder / "archives" / f"complete-analysis-{timestamp}.zip"
            
            with zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Voeg rapport toe
                zipf.writestr(f"report-{timestamp}.md", report_content)
                
                # Voeg JSON data toe
                zipf.writestr(f"data-{timestamp}.json", 
                            json.dumps(analysis_data, ensure_ascii=False, indent=2))
                
                # Voeg herschrijvingen toe
                for rewrite_file in rewrite_files:
                    if rewrite_file.exists():
                        zipf.write(rewrite_file, f"rewrites/{rewrite_file.name}")
            
            return archive_file
            
        except Exception as e:
            print(f"⚠️ Kon geen ZIP archief maken: {e}")
            return None
    
    def get_status(self):
        """Geef status van OneDrive integratie"""
        status = {
            "onedrive_detected": len(self.onedrive_paths) > 0,
            "onedrive_paths": [str(p) for p in self.onedrive_paths],
            "zapier_folder": str(self.zapier_manuscript_folder) if self.zapier_manuscript_folder else None,
            "output_folder": str(self.output_folder) if self.output_folder else None,
            "ready": self.output_folder is not None
        }
        return status

def setup_onedrive_integration():
    """Setup OneDrive integratie"""
    print("🔗 OneDrive Integratie Setup")
    print("=" * 40)
    
    manager = OneDriveManager()
    
    # Zoek manuscript folder
    manuscript_folder = input("Naam van je Zapier manuscript folder (default: 'manuscripts'): ").strip()
    if not manuscript_folder:
        manuscript_folder = "manuscripts"
    
    manager.find_zapier_manuscript_folder(manuscript_folder)
    
    # Maak output folder
    output_name = input("Naam voor output folder (default: 'Arc-Crusade-Outputs'): ").strip()
    if not output_name:
        output_name = "Arc-Crusade-Outputs"
    
    output_folder = manager.create_output_folder(output_name)
    
    if output_folder:
        print(f"\n🎉 OneDrive integratie succesvol ingesteld!")
        print(f"📁 Output folder: {output_folder}")
        
        # Sla configuratie op
        config = {
            "onedrive_output_folder": str(output_folder),
            "zapier_manuscript_folder": str(manager.zapier_manuscript_folder) if manager.zapier_manuscript_folder else None,
            "setup_date": datetime.now().isoformat()
        }
        
        config_file = Path("onedrive_config.json")
        config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        print(f"✅ Configuratie opgeslagen: {config_file}")
        
    else:
        print("❌ OneDrive integratie setup mislukt")
    
    return manager

if __name__ == "__main__":
    setup_onedrive_integration()