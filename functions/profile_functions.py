import streamlit as st
import pandas as pd


def get_user_info_dict(session_state):
    return {
        'name': session_state.get('name', 'Unbekannt'),
        'username': session_state.get('username', 'Unbekannt'),
        'email': session_state.get('email', 'Unbekannt'),
        'role': session_state.get('role', 'student')
    }


def get_role_display(role):
    return "Lehrer" if role == "teacher" else "Schüler"


def get_assigned_documents_status(document_manager, log_manager, username, user_class):
    if not user_class:
        return []

    status_rows = []
    folders = document_manager.get_folders()

    for folder in folders:
        for doc_name in document_manager.get_documents_in_folder(folder):
            assigned = (
                folder == user_class
                or user_class in document_manager.load_class_assignments(folder, doc_name).get("assigned_classes", [])
            )
            if not assigned:
                continue

            meta = document_manager.load_document_meta(folder, doc_name)
            due_date = meta.get("due_date")
            logs_df = log_manager.get_document_logs(folder, doc_name)
            student_row = logs_df[(logs_df['student_username'] == username)]

            if student_row.empty:
                status = "🔴 Nicht begonnen"
            else:
                quiz_required = document_manager.quiz_exists(folder, doc_name)
                status = log_manager.get_student_status(
                    student_row.iloc[0],
                    due_date=due_date,
                    quiz_required=quiz_required
                )

            status_rows.append({
                "Dokument": doc_name,
                "Klasse": folder,
                "Status": status,
                "Frist": due_date or "Keine"
            })

    return status_rows


def render_document_status_legend():
    st.divider()
    st.markdown("**Legende:**")
    st.write("🟢 Erledigt = gelesen (+ Quiz bestanden, falls Quiz vorhanden)")
    st.write("🟡 In Arbeit = gelesen, Quiz noch offen")
    st.write("🔴 Überfällig / Nicht begonnen = Aufgabe noch offen oder Frist abgelaufen")