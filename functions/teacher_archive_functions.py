import streamlit as st




def handle_document_upload(document_manager, selected_folder, uploaded_file, due_date):
    """
    Verarbeitet das Hochladen eines Dokuments
    
    Args:
        document_manager: DocumentManager-Instanz
        selected_folder: Zielordner
        uploaded_file: Hochgeladene Datei
        due_date: Fälligkeitsdatum
    
    Returns:
        bool: True bei Erfolg
    """
    try:
        success = document_manager.save_document(
            file_content=uploaded_file.getbuffer(),
            folder_name=selected_folder,
            file_name=uploaded_file.name
        ) and document_manager.save_document_meta(
            selected_folder,
            uploaded_file.name,
            {"due_date": due_date.strftime("%Y-%m-%d")}
        )
        
        if success:
            st.success(f"✓ '{uploaded_file.name}' in '{selected_folder}' hochgeladen!")
        else:
            st.error("Fehler beim Hochladen")
        
        return success
    except Exception as e:
        st.error(f"Fehler beim Hochladen: {e}")
        return False


def render_quiz_editor(document_manager, selected_doc, selected_folder_logs):
    """
    Rendert den Quiz-Editor und speichert Änderungen
    
    Args:
        document_manager: DocumentManager-Instanz
        selected_doc: Gewähltes Dokument
        selected_folder_logs: Ordner des Dokuments
    """
    with st.expander("✏️ Quiz bearbeiten"):
        quiz_def = document_manager.load_quiz(selected_folder_logs, selected_doc)
        questions = quiz_def.get("questions", [])

        if len(questions) < 10:
            for _ in range(10 - len(questions)):
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
                key=f"quiz_question_{selected_folder_logs}_{selected_doc}_{i}"
            )
            opts = q.get("options", ["", "", "", ""])
            for j in range(4):
                opts[j] = st.text_input(
                    f"Antwort {chr(65 + j)}",
                    value=opts[j],
                    key=f"quiz_option_{selected_folder_logs}_{selected_doc}_{i}_{j}"
                )
            q["options"] = opts
            q["correct_index"] = st.selectbox(
                "Richtige Antwort",
                options=list(range(4)),
                index=q.get("correct_index", 0),
                format_func=lambda x, opts=opts: opts[x] if opts[x] else f"Option {x + 1}",
                key=f"quiz_correct_{selected_folder_logs}_{selected_doc}_{i}"
            )

        if st.button("Quiz speichern", key=f"save_quiz_{selected_folder_logs}_{selected_doc}"):
            if document_manager.save_quiz(selected_folder_logs, selected_doc, {"questions": questions}):
                st.success("Quiz gespeichert.")
            else:
                st.error("Fehler beim Speichern des Quiz.")