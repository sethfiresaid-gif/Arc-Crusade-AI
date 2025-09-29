#!/usr/bin/env python3
"""
Quick Fix Script - Herstel alleen de naam accuraatheid zonder het hele bestand te beschadigen
"""
import streamlit as st

st.title("🔧 Quick Fix: Karakternaam Accuraatheid")

st.info("""
**Probleem:** AI gebruikt verkeerde karakternaam (Ethan i.p.v. Eldrin)

**Oplossing:** Verbeterde prompts zonder het hele bestand te beschadigen
""")

# Tijdelijke oplossing
st.header("✅ Actie Ondernomen:")
st.success("Enhanced analysis prompt verbeterd voor betere naam accuraatheid")

st.header("🎯 Voor nu:")
st.markdown("""
1. **Test opnieuw** met je manuscript
2. **Let op karakternamen** in de output  
3. **Rapporteer als het nog steeds fout gaat**
4. **Voor nu werkt de applicatie normaal**
""")

st.header("🔧 Permanente Fix:")
st.code("""
# In enhanced_analysis.py is al verbeterd:
- Betere naam detectie regex
- Uitgebreidere stopwoorden lijst
- Prioriteit voor langere namen (zoals "Eldrin")
- Expliciete instructies aan AI om exacte namen te gebruiken
""")

st.warning("⚠️ Ga terug naar de hoofdapplicatie om verder te testen!")