import streamlit as st
from utils.data_manager import DataManager
from utils.log_manager import LogManager
from utils.document_manager import DocumentManager

st.title("📚 Archiv - Meine Dokumente")

# Initialisiere Manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_App_DB")
log_manager = LogManager(data_manager)
document_manager = DocumentManager(data_manager)

st.info("Hier findest du alle Dokumente, die dein Lehrer hochgeladen hat.")

st.divider()

# TODO: Später - Klassen-Filter hinzufügen
# user_class = st.session_state.get('class', None)  # Wird später gespeichert
# if user_class:
#     folders = [f for f in document_manager.get_folders() if f.startswith(user_class)]
# else:
#     folders = document_manager.get_folders()

# BASIS: Zeige alle Ordner + Dokumente
folders = document_manager.get_folders()

if not folders:
    st.info("Keine Dokumente verfügbar.")
else:
    # Wähle Ordner
    selected_folder = st.selectbox("📁 Ordner auswählen", folders)
    
    if selected_folder:
        st.divider()
        st.subheader(f"Dokumente in: {selected_folder}")
        
        # Lade Dokumente des Ordners
        documents = document_manager.get_documents_in_folder(selected_folder)
        
        if not documents:
            st.info(f"Keine Dokumente in '{selected_folder}'.")
        else:
            # Zeige Dokumente mit "Öffnen"-Button
            for doc_name in documents:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.subheader(f"📄 {doc_name}")
                
                with col2:
                    if st.button(f"👁️ Öffnen", key=f"open_{selected_folder}_{doc_name}"):
                        st.session_state[f"open_{selected_folder}_{doc_name}"] = True
                
                with col3:
                    if st.button(f"✅ Gelesen", key=f"read_{selected_folder}_{doc_name}"):
                        # Märkiere als gelesen und logge
                        student_name = st.session_state.get('name', 'Unbekannt')
                        student_username = st.session_state.get('username', 'Unbekannt')
                        
                        log_manager.mark_document_as_read(
                            document_name=doc_name,
                            student_name=student_name,
                            student_username=student_username
                        )
                        
                        st.success(f"✓ '{doc_name}' als gelesen markiert!")
                
                # Wenn "Öffnen" geklickt wurde - PDF anzeigen
                if st.session_state.get(f"open_{selected_folder}_{doc_name}"):
                    st.divider()
                    st.write(f"**PDF: {doc_name}**")
                    
                    pdf_content = document_manager.get_document(selected_folder, doc_name)
                    if pdf_content:
                        st.pdf_viewer(pdf_content)
                        
                        # Download-Button
                        st.download_button(
                            label="⬇️ PDF herunterladen",
                            data=pdf_content,
                            file_name=doc_name,
                            mime="application/pdf",
                            key=f"download_{selected_folder}_{doc_name}"
                        )
                    else:
                        st.error("PDF konnte nicht geladen werden.")
                    
                    st.divider()