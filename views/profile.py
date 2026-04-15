import streamlit as st

st.title("👤 Mein Profil")

st.divider()

# Benutzerdaten aus Session State
name = st.session_state.get('name', 'Unbekannt')
username = st.session_state.get('username', 'Unbekannt')
email = st.session_state.get('email', 'Unbekannt')
role = st.session_state.get('role', 'student')

# Rolle als Deutsch anzeigen
role_display = "Lehrer" if role == "teacher" else "Schüler"

# Anzeigen in Spalten
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
    st.write(role_display)

st.divider()

st.info("Weitere Profileinstellungen kommen bald...")