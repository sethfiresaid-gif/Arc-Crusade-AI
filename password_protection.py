import streamlit as st

def add_password_protection():
    """
    Voeg simpele wachtwoord beveiliging toe aan je Streamlit app
    """
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("### 🔒 Arc Crusade AI - Private Access")
        st.text_input("Wachtwoord vereist", type="password", 
                     on_change=password_entered, key="password")
        st.info("💡 Voer het wachtwoord in om toegang te krijgen tot de manuscript analyzer")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("### 🔒 Arc Crusade AI - Private Access")
        st.text_input("Wachtwoord vereist", type="password", 
                     on_change=password_entered, key="password")
        st.error("❌ Incorrect wachtwoord. Probeer opnieuw.")
        return False
    else:
        return True

# Gebruik in je main streamlit_app.py:
# if add_password_protection():
#     # Hier komt je bestaande app code