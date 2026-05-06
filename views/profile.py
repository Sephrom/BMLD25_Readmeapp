import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.log_manager import LogManager
from utils.document_manager import DocumentManager


st.title("👤 Mein Profil")

st.divider()

# Benutzerdaten aus Session State
name = st.session_state.get('name', 'Unbekannt')
username = st.session_state.get('username', 'Unbekannt')
email = st.session_state.get('email', 'Unbekannt')
role = st.session_state.get('role', 'student')

# Rolle als Deutsch anzeigen
role_display = "Lehrer" if role == "teacher" else "Schüler"
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_App_DB")
log_manager = LogManager(data_manager)
document_manager = DocumentManager(data_manager)



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
user_class = st.session_state.get('class', None)

if not user_class:
    st.info("Du bist keiner Klasse zugeordnet.")
else:
    folders = [user_class] if user_class in document_manager.get_folders() else []
    status_rows = []

    for folder in folders:
        for doc_name in document_manager.get_documents_in_folder(folder):
            meta = document_manager.load_document_meta(folder, doc_name)
            due_date = meta.get("due_date")
            logs_df = log_manager.get_document_logs(doc_name)
            student_row = logs_df[(logs_df['student_username'] == st.session_state.get('username'))]

            if student_row.empty:
                status = "🔴 Nicht begonnen"
            else:
                status = log_manager.get_student_status(student_row.iloc[0], due_date=due_date)

            status_rows.append({
                "Dokument": doc_name,
                "Klasse": folder,
                "Status": status,
                "Frist": due_date or "Keine"
            })

    if status_rows:
        st.dataframe(pd.DataFrame(status_rows), hide_index=True, use_container_width=True)
    else:
        st.info("Für deine Klasse sind keine Dokumente vorhanden.")
st.divider()
st.markdown("**Legende:**")
st.write("🟢 Erledigt = Dokument gelesen + Quiz bestanden")
st.write("🟡 In Arbeit = Dokument gelesen, Quiz noch nicht bestanden")
st.write("🔴 Überfällig / Nicht begonnen = Aufgabe noch offen oder Frist abgelaufen")