import streamlit as st
import os
from utils.data_manager import DataManager
from utils.log_manager import LogManager

st.title("📚 Archiv - Dokumente verwalten")

# Initialisiere Manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_App_DB")
log_manager = LogManager(data_manager)

st.info("Als Lehrer kannst du hier Dokumente hochladen und die Aktivitäten deiner Schüler ansehen.")

st.divider()

# TAB 1: Dokument hochladen
st.subheader("📤 Dokument hochladen")

uploaded_file = st.file_uploader("PDF hochladen", type=['pdf'])
if uploaded_file:
    st.success(f"✓ Datei '{uploaded_file.name}' wurde hochgeladen!")
    st.info("Die Datei wird in das Archiv gespeichert.")

st.divider()

# TAB 2: Schüler-Aktivitäten ansehen
st.subheader("📋 Schüler-Aktivitäten")

# Beispiel-Dokumente
documents = [
    "Dokument_1",
    "Dokument_2",
    "Dokument_3",
]

selected_doc = st.selectbox("Dokument auswählen", documents)

if selected_doc:
    st.write(f"**Aktivitäten für: {selected_doc}**")
    
    # Lade Logs für das Dokument
    logs_df = log_manager.get_document_logs(selected_doc)
    
    if logs_df.empty:
        st.info("Noch keine Aktivitäten für dieses Dokument.")
    else:
        st.dataframe(
            logs_df,
            column_config={
                "timestamp": "Zeitstempel",
                "student_name": "Schüler Name",
                "student_username": "Benutzername",
                "document_name": "Dokument",
                "action": "Aktion",
            },
            hide_index=True,
            use_container_width=True,
        )
        