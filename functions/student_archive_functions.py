import streamlit as st
import random


def toggle_pdf_view(key):
    """Callback-Funktion für PDF-Anzeige Toggle"""
    st.session_state[key] = not st.session_state.get(key, False)


def is_assigned_to_user_class(folder_name, doc_name, user_class, document_manager):
    """
    Prüft, ob ein Dokument dem aktuellen Schüler zugeordnet ist

    Args:
        folder_name: Name des Ordners (Klasse)
        doc_name: Name des Dokuments
        user_class: Klasse des Schülers
        document_manager: DocumentManager-Instanz

    Returns:
        bool: True wenn Schüler Zugriff hat
    """
    if not user_class:
        return False
    if folder_name == user_class:
        return True
    assigned = document_manager.load_class_assignments(folder_name, doc_name).get("assigned_classes", [])
    return user_class in assigned


def get_available_folders_for_user(document_manager, user_class):
    """
    Filtert verfügbare Ordner für einen Schüler

    Args:
        document_manager: DocumentManager-Instanz
        user_class: Klasse des Schülers

    Returns:
        list: Verfügbare Ordner-Namen
    """
    folders = []
    for folder in document_manager.get_folders():
        for doc_name in document_manager.get_documents_in_folder(folder):
            if is_assigned_to_user_class(folder, doc_name, user_class, document_manager):
                folders.append(folder)
                break
    return folders


def get_document_status_and_meta(document_manager, log_manager, selected_folder, doc_name, username):
    """
    Sammelt Status und Metadaten eines Dokuments

    Returns:
        tuple: (status, due_date)
    """
    meta = document_manager.load_document_meta(selected_folder, doc_name)
    due_date = meta.get("due_date")
    logs_df = log_manager.get_document_logs(selected_folder, doc_name)
    student_row = logs_df[(logs_df['student_username'] == username)]

    status = "🔴 Nicht begonnen"
    if not student_row.empty:
        quiz_required = document_manager.quiz_exists(selected_folder, doc_name)
        status = log_manager.get_student_status(
            student_row.iloc[0],
            due_date=due_date,
            quiz_required=quiz_required
        )

    return status, due_date


def render_document_header(doc_name, selected_folder, user_class, document_manager, log_manager, username):
    """
    Rendert den Header eines Dokuments (Titel, Status, Frist)
    """
    st.subheader(f"📄 {doc_name}")
    status, due_date = get_document_status_and_meta(
        document_manager, log_manager, selected_folder, doc_name, username
    )
    st.write(f"**Status:** {status}")
    if due_date:
        st.write(f"**Frist:** {due_date}")

    return status, due_date


def render_document_buttons(log_manager, selected_folder, doc_name):
    """Zeigt die Open-/Read-Buttons und schreibt gegebenenfalls Log-Einträge."""
    open_key = f"open_{selected_folder}_{doc_name}"
    open_logged_key = f"open_logged_{selected_folder}_{doc_name}"
    student_name = st.session_state.get('name', 'Unbekannt')
    student_username = st.session_state.get('username', 'Unbekannt')

    if st.button("👁️ Öffnen", key=f"btn_open_{selected_folder}_{doc_name}"):
        toggle_pdf_view(open_key)

    if st.session_state.get(open_key) and not st.session_state.get(open_logged_key):
        log_manager.mark_document_as_opened(
            folder_name=selected_folder,
            document_name=doc_name,
            student_name=student_name,
            student_username=student_username
        )
        st.session_state[open_logged_key] = True

    if st.button("✅ Gelesen", key=f"read_{selected_folder}_{doc_name}"):
        log_manager.mark_document_as_read(
            folder_name=selected_folder,
            document_name=doc_name,
            student_name=student_name,
            student_username=student_username
        )
        st.success(f"✓ '{doc_name}' als gelesen markiert!")


def _get_valid_quiz_questions(quiz_def):
    """Filtert nur vollständige Fragen aus dem Quiz-Objekt."""
    return [
        q.copy() for q in quiz_def.get("questions", [])
        if q.get("question", "").strip()
        and any(opt.strip() for opt in q.get("options", []))
    ]


def _shuffle_questions_and_answers(questions):
    """Mischt Fragen und deren Antwortoptionen."""
    random.shuffle(questions)
    for q in questions:
        correct_answer = q["options"][q["correct_index"]]
        shuffled_options = random.sample(q["options"], len(q["options"]))
        q["options"] = shuffled_options
        q["correct_answer"] = correct_answer
    return questions


def _store_quiz_in_session(selected_folder, doc_name, questions):
    """Speichert Quiz-Status im Session State."""
    st.session_state[f"quiz_{selected_folder}_{doc_name}_questions"] = questions
    st.session_state[f"quiz_{selected_folder}_{doc_name}_current"] = 0
    st.session_state[f"quiz_{selected_folder}_{doc_name}_answers"] = [None] * len(questions)


def handle_quiz_start(document_manager, selected_folder, doc_name):
    """
    Initialisiert ein Quiz im Session State
    """
    quiz_def = document_manager.load_quiz(selected_folder, doc_name)
    if quiz_def.get("questions"):
        if st.button("📝 Quiz starten", key=f"start_quiz_{selected_folder}_{doc_name}"):
            questions = _get_valid_quiz_questions(quiz_def)
            questions = _shuffle_questions_and_answers(questions)
            _store_quiz_in_session(selected_folder, doc_name, questions)


def render_pdf_viewer(document_manager, selected_folder, doc_name):
    """
    Rendert die PDF-Anzeige und Download-Button
    """
    st.divider()
    st.write(f"**PDF: {doc_name}**")

    pdf_session_key = f"pdf_content_{selected_folder}_{doc_name}"
    if pdf_session_key not in st.session_state:
        st.session_state[pdf_session_key] = document_manager.get_document(selected_folder, doc_name)

    pdf_content = st.session_state[pdf_session_key]
    if pdf_content:
        st.pdf(pdf_content)
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


def render_quiz_form(selected_folder, doc_name):
    """
    Rendert das Quiz-Formular mit allen Fragen

    Returns:
        bool: True wenn Quiz abgesendet wurde
    """
    quiz_key = f"quiz_{selected_folder}_{doc_name}"
    if st.session_state.get(f"{quiz_key}_questions"):
        questions = st.session_state[f"{quiz_key}_questions"]
        form_key = f"{quiz_key}_form_{doc_name}"

        with st.form(key=form_key):
            for idx, q in enumerate(questions):
                st.markdown(f"### Frage {idx + 1} / {len(questions)}")
                st.write(q["question"])

                selected = st.radio(
                    "",
                    options=list(range(len(q["options"]))),
                    format_func=lambda i, opts=q["options"]: f"{chr(65+i)}) {opts[i]}",
                    key=f"{quiz_key}_answer_{idx}"
                )

                if selected is not None:
                    chosen_label = chr(65 + selected)
                    st.markdown(f"**Ausgewählt:** {chosen_label}) {q['options'][selected]}")

                st.divider()

            submit = st.form_submit_button("Quiz abschliessen")

        return submit is not None

    return False