import streamlit as st
from utils.data_manager import DataManager
from utils.log_manager import LogManager
from utils.document_manager import DocumentManager
from functions.teacher_archive_functions import handle_document_upload, render_quiz_editor
from functions.ui_helpers import render_status_legend

st.title("📚 Archiv - Dokumente verwalten")

# Initialisiere Manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_App_DB")
log_manager = LogManager(data_manager)
document_manager = DocumentManager(data_manager)

st.info("Als Lehrer kannst du hier Dokumente hochladen und die Aktivitäten deiner Schüler ansehen.")

st.divider()

# TAB 1: Dokument hochladen
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Dokument hochladen")
    
    # Lade vorhandene Ordner
    folders = document_manager.get_folders()
    
    # Option: Neuer Ordner erstellen
    create_new_folder = st.checkbox("Neuen Ordner erstellen")
    
    if create_new_folder:
        new_folder_name = st.text_input("Ordnername")
        if st.button("Ordner erstellen"):
            if document_manager.create_folder(new_folder_name):
                st.success(f"✓ Ordner '{new_folder_name}' erstellt!")
                st.rerun()
            else:
                st.error("Fehler beim Erstellen des Ordners")
    else:
        selected_folder = st.selectbox("Klasse / Ordner auswählen", folders if folders else ["Keine Ordner vorhanden"])
        due_date = st.date_input("Frist setzen", help="Datum, bis wann das Dokument gelesen und das Quiz erledigt sein sollte.")

        if selected_folder != "Keine Ordner vorhanden":
            # Upload in den ausgewählten Ordner
            uploaded_file = st.file_uploader("PDF hochladen", type=['pdf'])
            if uploaded_file:
                if st.button("Hochladen"):
                    if handle_document_upload(
                        document_manager, selected_folder, 
                        uploaded_file, due_date
                    ):
                        st.rerun()

st.divider()

# TAB 2: Schüler-Aktivitäten + Dokumente anschauen
st.subheader("📋 Schüler-Aktivitäten & Dokumente")

# Wähle Ordner
folders_for_logs = document_manager.get_folders()

if not folders_for_logs:
    st.info("Keine Ordner vorhanden.")
else:
    selected_folder_logs = st.selectbox("Ordner auswählen", folders_for_logs, key="logs_folder")
    
    # Wähle Dokument im Ordner
    documents_in_folder = document_manager.get_documents_in_folder(selected_folder_logs)
    
    if not documents_in_folder:
        st.info("Keine Dokumente in diesem Ordner.")
    else:
        selected_doc = st.selectbox("Dokument auswählen", documents_in_folder, key="logs_doc")
        
        if selected_doc:
            meta = document_manager.load_document_meta(selected_folder_logs, selected_doc)
            due_date_text = meta.get("due_date") or "Keine Frist"
            st.markdown(f"**Frist:** {due_date_text}")
            
            st.write(f"**Aktivitäten für: {selected_doc}**")
            
            # Buttons nebeneinander
            col_view, col_delete = st.columns(2)
            
            with col_view:
                with st.expander("📖 Dokument anschauen"):
                    pdf_content = document_manager.get_document(selected_folder_logs, selected_doc)
                    if pdf_content:
                        st.pdf(pdf_content)
                        
                        # Download-Button
                        st.download_button(
                            label="⬇️ PDF herunterladen",
                            data=pdf_content,
                            file_name=selected_doc,
                            mime="application/pdf",
                            key=f"download_teacher_{selected_folder_logs}_{selected_doc}"
                        )
                    else:
                        st.error("PDF konnte nicht geladen werden.")
            
            with col_delete:
                if st.button("🗑️ Löschen", key=f"delete_teacher_{selected_folder_logs}_{selected_doc}"):
                    if document_manager.delete_document(selected_folder_logs, selected_doc):
                        st.success(f"✓ '{selected_doc}' gelöscht!")
                        st.rerun()
                    else:
                        st.error("Fehler beim Löschen")
           
            render_quiz_editor(document_manager, selected_doc, selected_folder_logs)

            with st.expander("🎯 Klassen zuweisen"):
                available_classes = document_manager.get_all_classes_from_students()
                
                # Lade aktuelle Zuordnungen
                current_assignments = document_manager.load_class_assignments(selected_folder_logs, selected_doc)
                assigned_classes = current_assignments.get("assigned_classes", [])
                
                st.write(f"**Aktuell zugewiesen:** {', '.join(assigned_classes) if assigned_classes else 'Keine'}")
                
                # Multi-Select für Klassen
                selected_classes = st.multiselect(
                    "Wähle Klassen zum Zuweisen",
                    available_classes,
                    default=assigned_classes,
                    key=f"class_assign_{selected_doc}"
                )
                
                if st.button("Klassenzuordnung speichern", key=f"save_class_assign_{selected_doc}"):
                    if document_manager.save_class_assignments(selected_folder_logs, selected_doc, selected_classes):
                        st.success(f"✓ Dokument wurde den Klassen zugewiesen: {', '.join(selected_classes) if selected_classes else 'keine'}")
                        st.rerun()
                    else:
                        st.error("Fehler beim Speichern der Klassenzuordnung")
            
            # Zeige Logs
            st.write("**Schüler, die dieses Dokument gelesen haben:**")
            
            logs_df = log_manager.get_document_logs(selected_doc)
            
            if logs_df.empty:
                st.info("Noch keine Aktivitäten für dieses Dokument.")
            else:
                logs_df['status'] = logs_df.apply(
                    lambda row: log_manager.get_student_status(row, due_date=meta.get("due_date")),
                    axis=1
                )

                st.dataframe(
                    logs_df,
                    column_config={
                        "student_name": "Schüler Name",
                        "student_username": "Benutzername",
                        "document_name": "Dokument",
                        "status": "Status",
                        "opened_timestamp": "Geöffnet am",
                        "read_timestamp": "Gelesen am",
                        "quiz_passed_timestamp": "Quiz bestanden am",
                        "quiz_attempts": "Quiz-Versuche",
                        "last_quiz_score": "Letzte Quiz-Note",
                    },
                    hide_index=True,
                    use_container_width=True,
                )