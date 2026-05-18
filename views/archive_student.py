import streamlit as st
from utils.app_config import get_data_manager
from utils.log_manager import LogManager
from utils.document_manager import DocumentManager
from functions.student_archive_functions import (
    is_assigned_to_user_class,
    get_available_folders_for_user,
    render_document_header,
    render_document_buttons,
    handle_quiz_start,
    render_pdf_viewer,
    render_quiz_form,
    handle_quiz_submit
)
from functions.ui_helpers import render_status_legend

st.title("📚 Archiv - Meine Dokumente")

data_manager = get_data_manager()
log_manager = LogManager(data_manager)
document_manager = DocumentManager(data_manager)

st.info("Hier findest du alle Dokumente, die dein Lehrer hochgeladen hat.")
render_status_legend()
st.divider()

user_class = st.session_state.get('class', None)
folders = get_available_folders_for_user(document_manager, user_class)

if document_manager.get_last_error():
    st.error(f"⚠️ {document_manager.get_last_error()}")

if not folders:
    st.info("Keine Dokumente verfügbar.")
else:
    selected_folder = st.selectbox("📁 Ordner auswählen", folders)

    if selected_folder:
        st.divider()
        st.subheader(f"Dokumente in: {selected_folder}")

        documents = [
            doc_name
            for doc_name in document_manager.get_documents_in_folder(selected_folder)
            if is_assigned_to_user_class(selected_folder, doc_name, user_class, document_manager)
        ]

        if not documents:
            st.info(f"Keine Dokumente in '{selected_folder}'.")
        else:
            for doc_name in documents:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    render_document_header(
                        doc_name,
                        selected_folder,
                        user_class,
                        document_manager,
                        log_manager,
                        st.session_state.get('username')
                    )

                with col2:
                    render_document_buttons(
                        log_manager,
                        selected_folder,
                        doc_name
                    )

                with col3:
                    handle_quiz_start(document_manager, selected_folder, doc_name)

                if st.session_state.get(f"open_{selected_folder}_{doc_name}"):
                    render_pdf_viewer(document_manager, selected_folder, doc_name)

                submit = render_quiz_form(selected_folder, doc_name)
                if submit:
                    quiz_key = f"quiz_{selected_folder}_{doc_name}"
                    questions = st.session_state.get(f"{quiz_key}_questions", [])
                    if questions:
                        handle_quiz_submit(log_manager, selected_folder, doc_name, questions)