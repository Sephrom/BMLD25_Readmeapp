import streamlit as st
import pandas as pd


def get_all_students_list(data_manager):
    """
    Lädt alle Schüler aus credentials.yaml
    
    Args:
        data_manager: DataManager-Instanz
    
    Returns:
        list: Liste von Dicts mit Schüler-Infos
    """
    creds = data_manager.load_app_data('credentials.yaml', initial_value={"usernames": {}})
    students = []
    
    for username, user_data in creds.get("usernames", {}).items():
        if user_data.get("role") == "student":
            display_name = user_data.get("name") or user_data.get("username") or username
            students.append({
                "Benutzername": username,
                "Name": display_name,
                "Klasse": user_data.get("class") or "Keine Klasse",
                "Email": user_data.get("email", "")
            })
    
    return students


def assign_student_to_class(data_manager, student_username, class_name):
    """
    Ordnet Schüler zu Klasse zu und speichert
    
    Args:
        data_manager: DataManager-Instanz
        student_username: Benutzername des Schülers
        class_name: Name der Klasse
    
    Returns:
        bool: True bei Erfolg
    """
    try:
        creds = data_manager.load_app_data('credentials.yaml', initial_value={"usernames": {}})
        
        if student_username in creds['usernames']:
            creds['usernames'][student_username]['class'] = class_name
            data_manager.save_app_data(creds, 'credentials.yaml')
            st.success(f"✓ {student_username} wurde der Klasse '{class_name}' zugeordnet!")
            return True
        else:
            st.error("Schüler nicht gefunden.")
            return False
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False


def get_classes_with_students(students_list):
    """
    Organisiert Schüler nach Klassen
    
    Args:
        students_list: Liste von Schüler-Dicts
    
    Returns:
        dict: {class_name: [students]}
    """
    classes_dict = {}
    for student in students_list:
        class_name = student["Klasse"]
        if class_name not in classes_dict:
            classes_dict[class_name] = []
        classes_dict[class_name].append(student)
    
    return classes_dict