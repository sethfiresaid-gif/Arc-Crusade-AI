# 🎯 Quick Start: Client Georganiseerde Exports

## Voor Jou: Snelle Setup

### 1. 🔧 Setup Client Export (eenmalig)
```bash
python setup_client_export.py
```
- Configureer je export pad: `G:\Mijn Drive\The arc crusade\Export Arc Crusade Program`
- Test de functionaliteit

### 2. 📋 Test de Functionaliteit
```bash
python test_client_export.py
```
- Maakt een test client folder
- Verifieert dat alles werkt

### 3. 🚀 Gebruik Opties

#### Via Streamlit Web App
1. Open `streamlit run streamlit_app.py`
2. Vul bij "Client Information" de naam in
3. Zet "Organized Export" aan
4. Upload manuscript
5. Klik "Analyze Manuscript"

#### Via Command Line
```bash
# Voor elke nieuwe klant
python cli_manuscript_assistant.py manuscript.docx \
  --client-name "John Smith" \
  --export-path "G:\Mijn Drive\The arc crusade\Export Arc Crusade Program"
```

### 4. 📁 Resultaat Per Klant

Voor elke klant krijg je een folder zoals:
```
John_Smith_Manuscript_Name_20250929/
├── 01_Original_Manuscript/
│   └── manuscript.docx
├── 02_Analysis_Reports/  
│   └── Complete_Analysis_20250929-143022.md
├── 03_Rewritten_Sections/
│   ├── Chapter_1_20250929-143022.md
│   └── Chapter_2_20250929-143022.md
├── 04_JSON_Data/
│   └── Analysis_Data_20250929-143022.json
├── 05_Complete_Archive/
│   └── John_Smith_Complete_Analysis_20250929-143022.zip
├── 06_Notes_And_Feedback/
│   └── (leeg - voor jouw notities)
└── 00_ANALYSE_SAMENVATTING.md
```

### 5. 💼 Workflow per Client

1. **Upload**: Klant stuurt manuscript
2. **Analyse**: Draai Arc Crusade AI met `--client-name "Klant Naam"`
3. **Delivery**: Complete folder wordt gemaakt met alles erin
4. **Archive**: ZIP bestand voor eenvoudige versturen
5. **Communication**: Gebruik `06_Notes_And_Feedback` voor correspondentie

### 6. 🎨 Aanpassingen

Je kunt de folder template aanpassen in `onedrive_integration.py`:
- Andere folder namen
- Extra subfolders
- Aangepaste README templates
- Andere naamgeving conventies

### 7. 🔄 Automation Tips

- **Zapier**: Webhook naar API voor automatische verwerking
- **Batch**: Process meerdere manuscripten tegelijk
- **Templates**: Vooraf gemaakte client folders voor reguliere klanten

## Troubleshooting

**❓ "Export path not accessible"**
- Controleer of Google Drive gesynchroniseerd is
- Gebruik forward slashes: `G:/Mijn Drive/...` 
- Run als administrator indien nodig

**❓ "Client export failed"**
- Controleer schrijfrechten op export locatie
- Zorg dat OneDrive integration werkt
- Check de error logs

**❓ Folder niet gemaakt**
- Draai `python test_client_export.py` voor diagnostics
- Controleer `client_export_config.json` bestand

## Support

Voor vragen of problemen:
1. Check de console output voor specifieke errors
2. Test met `test_client_export.py`
3. Controleer de README.md voor meer details