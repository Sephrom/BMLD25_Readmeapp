import streamlit as st
from utils.data_manager import DataManager
from utils.log_manager import LogManager
from utils.document_manager import DocumentManager
import random

st.title("📚 Archiv - Meine Dokumente")

# Initialisiere Manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_App_DB")
log_manager = LogManager(data_manager)
document_manager = DocumentManager(data_manager)

# Callback-Funktion für PDF-Anzeige Toggle
def toggle_pdf_view(key):
    st.session_state[key] = not st.session_state.get(key, False)

st.info("Hier findest du alle Dokumente, die dein Lehrer hochgeladen hat.")

st.markdown("**Status-Legende:**")
st.write("🟢 Erledigt: Dokument gelesen und Quiz bestanden")
st.write("🟡 In Arbeit: Dokument gelesen, Quiz noch offen")
st.write("🔴 Überfällig / Nicht begonnen: Dokument nicht vollständig erledigt")


st.divider()

user_class = st.session_state.get('class', None)

def is_assigned_to_user_class(folder_name, doc_name, user_class):
    if not user_class:
        return False
    if folder_name == user_class:
        return True
    assigned = document_manager.load_class_assignments(folder_name, doc_name).get("assigned_classes", [])
    return user_class in assigned

folders = []
for folder in document_manager.get_folders():
    for doc_name in document_manager.get_documents_in_folder(folder):
        if is_assigned_to_user_class(folder, doc_name, user_class):
            folders.append(folder)
            break


if not folders:
    st.info("Keine Dokumente verfügbar.")
else:
    # Wähle Ordner
    selected_folder = st.selectbox("📁 Ordner auswählen", folders)
    
    if selected_folder:
        st.divider()
        st.subheader(f"Dokumente in: {selected_folder}")
        
        # Lade Dokumente des Ordners
        documents = document_manager.get_documents_in_folder(selected_folder)
        
        if not documents:
            st.info(f"Keine Dokumente in '{selected_folder}'.")
        else:
                        # Zeige Dokumente mit "Öffnen"-Button
            for doc_name in documents:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.subheader(f"📄 {doc_name}")
                meta = document_manager.load_document_meta(selected_folder, doc_name)
                due_date = meta.get("due_date")
                logs_df = log_manager.get_document_logs(doc_name)
                student_row = logs_df[(logs_df['student_username'] == st.session_state.get('username'))]
                status = "🔴 Nicht begonnen"
                if not student_row.empty:
                    status = log_manager.get_student_status(student_row.iloc[0], due_date=due_date)

                st.write(f"**Status:** {status}")
                if due_date:
                    st.write(f"**Frist:** {due_date}")

                
                with col2:
                    st.button(f"👁️ Öffnen", 
                        key=f"btn_open_{selected_folder}_{doc_name}",
                        on_click=toggle_pdf_view,
                        args=(f"open_{selected_folder}_{doc_name}",)
                    )
                    
                    # Logging nur einmal beim ersten Öffnen
                    open_state_key = f"open_{selected_folder}_{doc_name}"
                    open_logged_key = f"open_logged_{selected_folder}_{doc_name}"
                    
                    if st.session_state.get(open_state_key) and not st.session_state.get(open_logged_key):
                        student_name = st.session_state.get('name', 'Unbekannt')
                        student_username = st.session_state.get('username', 'Unbekannt')
                        log_manager.mark_document_as_opened(
                            document_name=doc_name,
                            student_name=student_name,
                            student_username=student_username
                        )
                        st.session_state[open_logged_key] = True
                
                with col3:
                    if st.button(f"✅ Gelesen", key=f"read_{selected_folder}_{doc_name}"):
                        # Märkiere als gelesen und logge
                        student_name = st.session_state.get('name', 'Unbekannt')
                        student_username = st.session_state.get('username', 'Unbekannt')
                        
                        log_manager.mark_document_as_read(
                            document_name=doc_name,
                            student_name=student_name,
                            student_username=student_username
                        )
                        
                        st.success(f"✓ '{doc_name}' als gelesen markiert!")
                
                # Quiz-Button hinzufügen
                quiz_def = document_manager.load_quiz(doc_name)
                if quiz_def.get("questions"):
                    if st.button("📝 Quiz starten", key=f"start_quiz_{selected_folder}_{doc_name}"):
                        questions = [q.copy() for q in quiz_def["questions"]]
                        random.shuffle(questions)
                        for q in questions:
                            correct_answer = q["options"][q["correct_index"]]
                            shuffled_options = random.sample(q["options"], len(q["options"]))
                            q["correct_index"] = shuffled_options.index(correct_answer)
                            q["options"] = shuffled_options

                        st.session_state[f"quiz_{selected_folder}_{doc_name}_questions"] = questions
                        st.session_state[f"quiz_{selected_folder}_{doc_name}_current"] = 0
                        st.session_state[f"quiz_{selected_folder}_{doc_name}_answers"] = [None] * len(questions)
                
                # Wenn "Öffnen" geklickt wurde - PDF anzeigen
                if st.session_state.get(f"open_{selected_folder}_{doc_name}"):
                    st.divider()
                    st.write(f"**PDF: {doc_name}**")
                    
                    pdf_content = document_manager.get_document(selected_folder, doc_name)
                    if pdf_content:
                        st.pdf(pdf_content)
                        
                        # Download-Button
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
                
                # Quiz-Fenster
                quiz_key = f"quiz_{selected_folder}_{doc_name}"
                if st.session_state.get(f"{quiz_key}_questions"):
                    questions = st.session_state[f"{quiz_key}_questions"]
                    current = st.session_state[f"{quiz_key}_current"]
                    answers = st.session_state[f"{quiz_key}_answers"]

                    q = questions[current]
                    st.markdown(f"### Frage {current + 1} / {len(questions)}")
                    st.write(q["question"])

                    selected_index = st.radio(
                        "Antwort wählen",
                        options=list(range(len(q["options"]))),
                        format_func=lambda i: q["options"][i],
                        index=answers[current] if answers[current] is not None else 0,
                        key=f"{quiz_key}_answer_{current}"
                    )
                    answers[current] = selected_index
                    st.session_state[f"{quiz_key}_answers"] = answers

                    col_back, col_next = st.columns(2)
                    with col_back:
                        if st.button("Zurück", key=f"{quiz_key}_prev_{doc_name}") and current > 0:
                            st.session_state[f"{quiz_key}_current"] = current - 1
                            st.experimental_rerun()
                    with col_next:
                        if st.button("Weiter", key=f"{quiz_key}_next_{doc_name}") and current < len(questions) - 1:
                            st.session_state[f"{quiz_key}_current"] = current + 1
                            st.experimental_rerun()

                    if current == len(questions) - 1:
                        if st.button("Quiz abschliessen", key=f"{quiz_key}_submit_{doc_name}"):
                            correct = 0
                            for idx, question in enumerate(questions):
                                if answers[idx] == question["correct_index"]:
                                    correct += 1
                            score = correct / len(questions)
                            passed = score >= 0.8

                            student_name = st.session_state.get('name', 'Unbekannt')
                            student_username = st.session_state.get('username', 'Unbekannt')
                            log_manager.record_quiz_attempt(
                                document_name=doc_name,
                                student_name=student_name,
                                student_username=student_username,
                                score=score,
                                passed=passed
                            )

                            st.success(f"Du hast {int(score * 100)}% erreicht. {'Bestanden' if passed else 'Nicht bestanden'}")
                            del st.session_state[f"{quiz_key}_questions"]
                            del st.session_state[f"{quiz_key}_current"]
                            del st.session_state[f"{quiz_key}_answers"]