import streamlit as st
from utils.data_manager import DataManager
from utils.log_manager import LogManager
from utils.document_manager import DocumentManager

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
        # Wähle existierenden Ordner
        selected_folder = st.selectbox("Ordner auswählen", folders if folders else ["Keine Ordner vorhanden"])
        
        if selected_folder != "Keine Ordner vorhanden":
            # Upload in den ausgewählten Ordner
            uploaded_file = st.file_uploader("PDF hochladen", type=['pdf'])
            if uploaded_file:
                if st.button("Hochladen"):
                    if document_manager.save_document(
                        file_content=uploaded_file.getbuffer(),
                        folder_name=selected_folder,
                        file_name=uploaded_file.name
                    ):
                        st.success(f"✓ '{uploaded_file.name}' in '{selected_folder}' hochgeladen!")
                        st.rerun()
                    else:
                        st.error("Fehler beim Hochladen")

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
           
            with st.expander("✏️ Quiz bearbeiten"):
                quiz_def = document_manager.load_quiz(selected_doc)
                questions = quiz_def.get("questions", [])

                if len(questions) < 3:
                    for _ in range(3 - len(questions)):
                        questions.append({
                            "question": "",
                            "options": ["", "", "", ""],
                            "correct_index": 0
                        })

                for i, q in enumerate(questions):
                    st.markdown(f"### Frage {i + 1}")
                    q["question"] = st.text_input(
                        f"Frage {i + 1}",
                        value=q.get("question", ""),
                        key=f"quiz_question_{selected_doc}_{i}"
                    )
                    opts = q.get("options", ["", "", "", ""])
                    for j in range(4):
                        opts[j] = st.text_input(
                            f"Antwort {chr(65 + j)}",
                            value=opts[j],
                            key=f"quiz_option_{selected_doc}_{i}_{j}"
                        )
                    q["options"] = opts
                    q["correct_index"] = st.selectbox(
                        "Richtige Antwort",
                        options=list(range(4)),
                        index=q.get("correct_index", 0),
                        format_func=lambda x, opts=opts: opts[x],
                        key=f"quiz_correct_{selected_doc}_{i}"
                    )

                if st.button("Quiz speichern", key=f"save_quiz_{selected_doc}"):
                    if document_manager.save_quiz(selected_doc, {"questions": questions}):
                        st.success("Quiz gespeichert.")
                    else:
                        st.error("Fehler beim Speichern des Quiz.")  

            # Zeige Logs
            st.write("**Schüler, die dieses Dokument gelesen haben:**")
            
            logs_df = log_manager.get_document_logs(selected_doc)
            
            if logs_df.empty:
                st.info("Noch keine Aktivitäten für dieses Dokument.")
            else:
                st.dataframe(
                    logs_df,
                    column_config={
                        "student_name": "Schüler Name",
                        "student_username": "Benutzername",
                        "document_name": "Dokument",
                        "opened_timestamp": "Geöffnet am",
                        "read_timestamp": "Gelesen am",
                        "quiz_passed_timestamp": "Quiz bestanden am",
                        "quiz_attempts": "Quiz-Versuche",
                        "last_quiz_score": "Letzte Quiz-Note",
                    },
                    hide_index=True,
                    use_container_width=True,
                )
