import streamlit as st
from utils.data_manager import DataManager
from utils.document_manager import DocumentManager

st.title("👥 Klassenverwaltung & Zuteilung")

# Initialisiere Manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_App_DB")
document_manager = DocumentManager(data_manager)

st.info("Hier kannst du Schüler zu Klassen zuordnen und Dokumente klassifizieren.")

st.divider()

# TAB 1: Alle Schüler anzeigen
st.subheader("📋 Alle Schüler & ihre Klassen")

creds = data_manager.load_app_data('credentials.yaml', initial_value={"usernames": {}})
students = []

for username, user_data in creds.get("usernames", {}).items():
    if user_data.get("role") == "student":
        students.append({
            "Benutzername": username,
            "Name": user_data.get("name", "Unbekannt"),
            "Klasse": user_data.get("class") or "Keine Klasse",
            "Email": user_data.get("email", "")
        })

if students:
    import pandas as pd
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
            creds['usernames'][selected_student]['class'] = selected_class
            data_manager.save_app_data(creds, 'credentials.yaml')
            st.success(f"✓ {selected_student} wurde der Klasse '{selected_class}' zugeordnet!")
            st.rerun()
        else:
            st.error("Bitte wähle oder erstelle eine Klasse.")

st.divider()

# TAB 3: Alle Klassen übersicht
st.subheader("📊 Alle Klassen")

all_classes_list = document_manager.get_all_classes_from_students()

if all_classes_list:
    for class_name in all_classes_list:
        class_students = [s for s in students if s["Klasse"] == class_name]
        st.markdown(f"**{class_name}** ({len(class_students)} Schüler)")
        for student in class_students:
            st.write(f"  • {student['Name']} ({student['Benutzername']})")
else:
    st.info("Keine Klassen vorhanden.")