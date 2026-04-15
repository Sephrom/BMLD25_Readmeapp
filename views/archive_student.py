import streamlit as st
from utils.data_manager import DataManager
from utils.log_manager import LogManager

st.title("📚 Archiv - Meine Dokumente")

# Initialisiere Manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_App_DB")
log_manager = LogManager(data_manager)

st.info("Hier findest du alle Dokumente, die dein Lehrer hochgeladen hat.")

st.divider()

# Beispiel-Dokumente (später von der Datenbank laden)
documents = [
    {"name": "Dokument_1", "title": "Mathematik - Kapitel 1", "description": "Einführung in die Algebra"},
    {"name": "Dokument_2", "title": "Deutsch - Lektüre", "description": "Geschichtenanalyse"},
    {"name": "Dokument_3", "title": "Englisch - Vokabeln", "description": "Unit 1-5 Vokabeln"},
]

# Zeige Dokumente in Karten
for doc in documents:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(doc["title"])
        st.write(doc["description"])
    
    with col2:
        if st.button(f"✅ Gelesen", key=doc["name"]):
            # Märkiere als gelesen und logge
            student_name = st.session_state.get('name', 'Unbekannt')
            student_username = st.session_state.get('username', 'Unbekannt')
            
            log_manager.mark_document_as_read(
                document_name=doc["name"],
                student_name=student_name,
                student_username=student_username
            )
            
            st.success(f"✓ '{doc['title']}' als gelesen markiert!")
    
    st.divider()