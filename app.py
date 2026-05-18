import streamlit as st

from utils.app_config import get_data_manager
from utils.login_manager import LoginManager

st.set_page_config(page_title="ReadMeApp", page_icon=":material/home:")

data_manager = get_data_manager()
login_manager = LoginManager(data_manager)
login_manager.login_register()

# Lade die Rolle und Klasse des aktuellen Benutzers aus den Credentials
user_info = login_manager.auth_credentials['usernames'].get(st.session_state.get('username'), {})
user_role = user_info.get('role', 'student')
user_class = user_info.get('class', None)

st.session_state['role'] = user_role
st.session_state['class'] = user_class

# Navigation basierend auf Rolle
user_role = st.session_state.get('role', 'student')

if user_role == 'teacher':
    # Lehrer-Navigation
    pg_home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
    pg_archive = st.Page("views/archive_teacher.py", title="Archiv", icon=":material/archive:")
    pg_classes = st.Page("views/class_assignment.py", title="Klassen", icon=":material/people:")
    pg_profile = st.Page("views/profile.py", title="Profil", icon=":material/person:")
    pages = [pg_home, pg_archive, pg_classes, pg_profile]
else:
    # Schüler-Navigation
    pg_home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
    pg_archive = st.Page("views/archive_student.py", title="Archiv", icon=":material/archive:")
    pg_profile = st.Page("views/profile.py", title="Profil", icon=":material/person:")
    pages = [pg_home, pg_archive, pg_profile]

pg = st.navigation(pages)
pg.run()