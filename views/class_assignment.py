import streamlit as st
import pandas as pd
from utils.app_config import get_data_manager
from utils.document_manager import DocumentManager
from functions.class_management_functions import (
    get_all_students_list,
    assign_student_to_class,
    get_classes_with_students
)

st.title("👥 Klassenverwaltung & Zuteilung")

data_manager = get_data_manager()
document_manager = DocumentManager(data_manager)

st.info("Hier kannst du Schüler zu Klassen zuordnen und Dokumente klassifizieren.")

st.divider()

# TAB 1: Alle Schüler anzeigen
st.subheader("📋 Alle Schüler & ihre Klassen")

students = get_all_students_list(data_manager)

if students:
    st.dataframe(pd.DataFrame(students), hide_index=True, use_container_width=True)
else:
    st.info("Keine Schüler vorhanden.")

st.divider()

# TAB 2: Schüler einer Klasse zuordnen
st.subheader("✏️ Schüler Klasse zuordnen")

if students:
    student_names = [f"{s['Name']} ({s['Benutzername']})" for s in students]
    selected_student_display = st.selectbox("Schüler wählen", student_names)
    selected_student = selected_student_display.split("(")[1].rstrip(")")
    
    available_classes = document_manager.get_all_classes_from_students()
    all_classes = available_classes + ["Neue Klasse erstellen"]
    
    selected_class_option = st.selectbox("Klasse zuordnen", all_classes)
    
    if selected_class_option == "Neue Klasse erstellen":
        new_class = st.text_input("Neue Klasse (z.B. 1A, 2B):")
        if new_class:
            selected_class = new_class
        else:
            selected_class = None
    else:
        selected_class = selected_class_option
    
    if st.button("Zuordnung speichern"):
        if selected_class:
            if assign_student_to_class(data_manager, selected_student, selected_class):
                st.rerun()
        else:
            st.error("Bitte wähle oder erstelle eine Klasse.")

st.divider()

# TAB 3: Alle Klassen übersicht
st.subheader("📊 Alle Klassen")

all_classes_list = document_manager.get_all_classes_from_students()

if all_classes_list:
    classes_dict = get_classes_with_students(students)
    for class_name in all_classes_list:
        class_students = classes_dict.get(class_name, [])
        st.markdown(f"**{class_name}** ({len(class_students)} Schüler)")
        for student in class_students:
            st.write(f"  • {student['Name']} ({student['Benutzername']})")
else:
    st.info("Keine Klassen vorhanden.")