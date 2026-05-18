import pandas as pd
import streamlit as st

from functions.class_management_functions import (
    assign_student_to_class,
    get_all_students_list,
    get_classes_with_students,
)
from utils.app_config import get_data_manager
from utils.document_manager import DocumentManager


st.title("Klassenverwaltung & Zuteilung")

data_manager = get_data_manager()
document_manager = DocumentManager(data_manager)

st.info("Hier kannst du Klassen erstellen und Schueler zu Klassen zuordnen.")

st.divider()

st.subheader("Neue Klasse erstellen")
new_class_name = st.text_input("Neue Klasse (z.B. 1A, 2B):", key="new_class_name")

if st.button("Klasse erstellen"):
    if new_class_name.strip():
        if document_manager.create_class(new_class_name):
            st.success(f"Klasse '{new_class_name.strip()}' erstellt!")
            st.rerun()
        else:
            st.error(document_manager.get_last_error() or "Klasse konnte nicht erstellt werden.")
    else:
        st.error("Klassenname kann nicht leer sein.")

st.divider()

st.subheader("Alle Schueler & ihre Klassen")
students = get_all_students_list(data_manager)

if students:
    st.dataframe(pd.DataFrame(students), hide_index=True, use_container_width=True)
else:
    st.info("Keine Schueler vorhanden.")

st.divider()

st.subheader("Schueler Klasse zuordnen")
available_classes = document_manager.get_all_classes_from_students()

if students:
    student_names = [f"{s['Name']} ({s['Benutzername']})" for s in students]
    selected_student_display = st.selectbox("Schueler waehlen", student_names)
    selected_student = selected_student_display.split("(")[1].rstrip(")")

    selected_class = st.selectbox(
        "Klasse zuordnen",
        available_classes if available_classes else ["Keine Klassen vorhanden"],
    )

    if st.button("Zuordnung speichern"):
        if selected_class and selected_class != "Keine Klassen vorhanden":
            if assign_student_to_class(data_manager, selected_student, selected_class):
                st.rerun()
        else:
            st.error("Bitte erstelle zuerst eine Klasse.")
else:
    st.info("Registriere zuerst einen Schueleraccount, dann kannst du ihn hier zuweisen.")

st.divider()

st.subheader("Alle Klassen")

if available_classes:
    classes_dict = get_classes_with_students(students)
    for class_name in available_classes:
        class_students = classes_dict.get(class_name, [])
        st.markdown(f"**{class_name}** ({len(class_students)} Schueler)")
        for student in class_students:
            st.write(f"- {student['Name']} ({student['Benutzername']})")
else:
    st.info("Keine Klassen vorhanden.")
