import streamlit as st

#Funktion 1: toggle_pdf_view(key)
#  - Callback für PDF-Anzeige Toggle
#  - Befindet sich aktuell in archive_student.py, Zeile ~11



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


#Funktion 2: is_assigned_to_user_class(folder_name, doc_name, user_class, document_manager)
#  - Prüft ob Schüler Zugriff auf Dokument hat
#  - Befindet sich aktuell in def-quizz.py
#  - WICHTIG: parameter hinzufügen!

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