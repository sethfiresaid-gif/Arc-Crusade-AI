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
        self.custom_export_path = None
        self.client_folders = {}  # Track client-specific folders
        
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
    
    def set_custom_export_path(self, export_path):
        """Stel aangepaste export locatie in voor klant organisatie
        
        Args:
            export_path: Pad naar de export folder (bijv. G:\\Mijn Drive\\The arc crusade\\Export Arc Crusade Program)
        """
        export_path = Path(export_path)
        if export_path.exists():
            self.custom_export_path = export_path
            print(f"✅ Aangepaste export locatie ingesteld: {export_path}")
            return True
        else:
            print(f"❌ Export pad bestaat niet: {export_path}")
            return False
    
    def create_client_folder(self, client_name, manuscript_filename=None):
        """Maak klant-specifieke folder in de export locatie
        
        Args:
            client_name: Naam van de klant
            manuscript_filename: Optioneel - bestandsnaam van het manuscript voor automatische naamgeving
            
        Returns:
            Path naar de aangemaakte klantfolder
        """
        if not self.custom_export_path:
            print("❌ Geen aangepaste export locatie ingesteld")
            return None
        
        # Maak veilige folder naam
        safe_client_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_client_name = safe_client_name.replace(' ', '_')
        
        # Voeg datum toe voor uniekheid
        timestamp = datetime.now().strftime("%Y%m%d")
        
        if manuscript_filename:
            # Gebruik manuscript naam als basis
            manuscript_base = Path(manuscript_filename).stem
            safe_manuscript_name = "".join(c for c in manuscript_base if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_manuscript_name = safe_manuscript_name.replace(' ', '_')
            folder_name = f"{safe_client_name}_{safe_manuscript_name}_{timestamp}"
        else:
            folder_name = f"{safe_client_name}_{timestamp}"
        
        client_folder = self.custom_export_path / folder_name
        
        try:
            # Maak klantfolder en subfolders
            client_folder.mkdir(parents=True, exist_ok=True)
            
            # Maak standaard subfolders voor georganiseerde export
            subfolders = [
                "01_Original_Manuscript",
                "02_Analysis_Reports", 
                "03_Rewritten_Sections",
                "04_JSON_Data",
                "05_Complete_Archive",
                "06_Notes_And_Feedback"
            ]
            
            for subfolder in subfolders:
                (client_folder / subfolder).mkdir(exist_ok=True)
            
            # Bewaar klant info
            self.client_folders[client_name] = client_folder
            
            # Maak klant-specifieke README
            readme_content = self.generate_client_readme(client_name, folder_name)
            (client_folder / "README.md").write_text(readme_content, encoding="utf-8")
            
            print(f"✅ Klantfolder aangemaakt: {client_folder}")
            return client_folder
            
        except Exception as e:
            print(f"❌ Fout bij aanmaken klantfolder: {e}")
            return None
    
    def generate_client_readme(self, client_name, folder_name):
        """Genereer README voor klant-specifieke folder"""
        return f"""# Arc Crusade Manuscript Analysis - {client_name}

**Datum**: {datetime.now().strftime("%d %B %Y")}
**Folder**: {folder_name}

## Folder Structuur

### 📄 01_Original_Manuscript
Het originele manuscript bestand zoals ontvangen.

### 📊 02_Analysis_Reports  
Volledige analyse rapporten in Markdown formaat:
- Genre analyse
- Karakter ontwikkeling
- Plot structuur
- Schrijfstijl evaluatie
- Aanbevelingen voor verbetering

### ✍️ 03_Rewritten_Sections
Herschreven hoofdstukken en secties met verbeteringen:
- Aangepaste dialogen
- Verbeterde beschrijvingen  
- Sterkere plot ontwikkeling
- Karakterontwikkeling

### 💾 04_JSON_Data
Gestructureerde analyse data voor verdere verwerking:
- Gedetailleerde scores per categorie
- Metadata van de analyse
- Exporteerbare data voor rapportages

### 📦 05_Complete_Archive
ZIP archief met alle bestanden voor eenvoudige distributie.

### 📝 06_Notes_And_Feedback
Ruimte voor aanvullende notities en feedback:
- Klant communicatie
- Bijzondere aandachtspunten
- Follow-up acties

---

**Gegenereerd door Arc Crusade Manuscript Assistant**
**© {datetime.now().year} - Professionele Manuscript Analyse Service**
"""
    
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
    
    def save_analysis_to_client_folder(self, client_name, analysis_data, report_content, 
                                     original_file=None, rewrite_files=None, timestamp=None):
        """Sla analyse resultaten op in klant-specifieke folder"""
        
        # Controleer of klant folder bestaat, zo niet maak deze aan
        if client_name not in self.client_folders:
            manuscript_filename = original_file.name if original_file else None
            client_folder = self.create_client_folder(client_name, manuscript_filename)
            if not client_folder:
                return False
        else:
            client_folder = self.client_folders[client_name]
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        try:
            # 1. Kopieer origineel manuscript
            if original_file and original_file.exists():
                dest_original = client_folder / "01_Original_Manuscript" / original_file.name
                shutil.copy2(original_file, dest_original)
                print(f"✅ Origineel manuscript gekopieerd: {dest_original}")
            
            # 2. Sla analyse rapport op
            report_file = client_folder / "02_Analysis_Reports" / f"Complete_Analysis_{timestamp}.md"
            report_file.write_text(report_content, encoding="utf-8")
            print(f"✅ Analyse rapport opgeslagen: {report_file}")
            
            # 3. Sla JSON data op
            json_file = client_folder / "04_JSON_Data" / f"Analysis_Data_{timestamp}.json"
            json_file.write_text(json.dumps(analysis_data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"✅ JSON data opgeslagen: {json_file}")
            
            # 4. Sla herschreven secties op
            if rewrite_files:
                rewrites_folder = client_folder / "03_Rewritten_Sections"
                
                for rewrite_file in rewrite_files:
                    if rewrite_file.exists():
                        dest_file = rewrites_folder / f"{rewrite_file.stem}_{timestamp}.md"
                        dest_file.write_text(rewrite_file.read_text(encoding="utf-8"), encoding="utf-8")
                        print(f"✅ Herschreven sectie opgeslagen: {dest_file}")
            
            # 5. Maak complete ZIP archief
            archive_file = self.create_client_zip_archive(
                client_folder, client_name, timestamp, report_content, 
                analysis_data, original_file, rewrite_files or []
            )
            
            if archive_file:
                print(f"✅ Complete archief gemaakt: {archive_file}")
            
            # 6. Genereer samenvatting
            self.generate_client_summary(client_folder, client_name, analysis_data, timestamp)
            
            return True
            
        except Exception as e:
            print(f"❌ Fout bij opslaan naar klantfolder: {e}")
            return False
    
    def save_analysis_to_onedrive(self, analysis_data, report_content, rewrite_files=None, timestamp=None):
        """Sla analyse resultaten op in OneDrive (bestaande functionaliteit)"""
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
    
    def create_client_zip_archive(self, client_folder, client_name, timestamp, 
                                report_content, analysis_data, original_file, rewrite_files):
        """Maak compleet ZIP archief voor klant in de klantfolder"""
        try:
            import zipfile
            
            archive_file = client_folder / "05_Complete_Archive" / f"{client_name}_Complete_Analysis_{timestamp}.zip"
            
            with zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Voeg origineel manuscript toe
                if original_file and original_file.exists():
                    zipf.write(original_file, f"01_Original/{original_file.name}")
                
                # Voeg analyse rapport toe
                zipf.writestr(f"02_Analysis/Complete_Analysis_{timestamp}.md", report_content)
                
                # Voeg JSON data toe
                zipf.writestr(f"04_Data/Analysis_Data_{timestamp}.json", 
                            json.dumps(analysis_data, ensure_ascii=False, indent=2))
                
                # Voeg herschrijvingen toe
                for rewrite_file in rewrite_files:
                    if rewrite_file.exists():
                        zipf.write(rewrite_file, f"03_Rewrites/{rewrite_file.name}")
                
                # Voeg README toe
                readme_path = client_folder / "README.md"
                if readme_path.exists():
                    zipf.write(readme_path, "README.md")
            
            return archive_file
            
        except Exception as e:
            print(f"⚠️ Kon geen klant ZIP archief maken: {e}")
            return None
    
    def create_zip_archive(self, timestamp, report_content, analysis_data, rewrite_files):
        """Maak ZIP archief van alle bestanden (bestaande functionaliteit)"""
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
    
    def generate_client_summary(self, client_folder, client_name, analysis_data, timestamp):
        """Genereer samenvatting voor klant"""
        try:
            # Haal belangrijke scores op
            genre_score = analysis_data.get('genre_analysis', {}).get('overall_genre_alignment', 'N/A')
            character_score = analysis_data.get('character_analysis', {}).get('average_development_score', 'N/A')
            plot_score = analysis_data.get('plot_analysis', {}).get('overall_structure_score', 'N/A')
            
            summary_content = f"""# Analyse Samenvatting - {client_name}

**Datum**: {datetime.now().strftime("%d %B %Y om %H:%M")}
**Analyse ID**: {timestamp}

## 📈 Scores Overzicht

- **Genre Alignering**: {genre_score}/10
- **Karakter Ontwikkeling**: {character_score}/10  
- **Plot Structuur**: {plot_score}/10

## 📁 Geleverde Bestanden

✅ Origineel manuscript
✅ Complete analyse rapport
✅ Herschreven secties (indien van toepassing)
✅ Gestructureerde data (JSON)
✅ Complete archief (ZIP)

## 🎯 Volgende Stappen

1. **Review het analyse rapport** in folder `02_Analysis_Reports`
2. **Bekijk de herschreven secties** in folder `03_Rewritten_Sections`
3. **Download het complete archief** uit folder `05_Complete_Archive` voor backup

## 💬 Contact & Follow-up

Voor vragen over deze analyse of aanvullende services:
- Gebruik folder `06_Notes_And_Feedback` voor communicatie
- Alle bestanden zijn georganiseerd voor eenvoudige toegang

---
*Gegenereerd door Arc Crusade Manuscript Assistant*
*Professional Manuscript Analysis Service*
"""
            
            summary_file = client_folder / "00_ANALYSE_SAMENVATTING.md"
            summary_file.write_text(summary_content, encoding="utf-8")
            print(f"✅ Klant samenvatting gegenereerd: {summary_file}")
            
        except Exception as e:
            print(f"⚠️ Kon geen samenvatting genereren: {e}")
    
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