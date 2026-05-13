import streamlit as st


def render_status_legend():
    """Zeigt die Status-Legende an"""
    st.markdown("**Status-Legende:**")
    st.write("🟢 Erledigt: Dokument gelesen und Quiz bestanden")
    st.write("🟡 In Arbeit: Dokument gelesen, Quiz noch offen")
    st.write("🔴 Überfällig / Nicht begonnen: Dokument nicht vollständig erledigt")


def render_user_info_columns(name, username, email, role):
    """Rendert 2-Spalten Layout für Benutzerinfo"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Name:**")
        st.write("**Benutzername:**")
        st.write("**Email:**")
        st.write("**Rolle:**")
    
    with col2:
        st.write(name)
        st.write(username)
        st.write(email)
        st.write(role)