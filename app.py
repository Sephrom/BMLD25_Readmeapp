
import pandas as pd 
import streamlit as st


from utils.data_manager import DataManager
from utils.login_manager import LoginManager

data_manager = DataManager(       # initialize data manager
    fs_protocol='webdav',         # protocol for the filesystem, use webdav for switch drive
    fs_root_folder="BMLD_App_DB"  # folder on switch drive where the data is stored
    ) 
login_manager = LoginManager(data_manager) # handles user login and registration
login_manager.login_register()             # stops if not logged in

# Lade die Rolle des aktuellen Benutzers aus den Credentials
user_role = login_manager.auth_credentials['usernames'].get(st.session_state.get('username'), {}).get('role', 'student')
st.session_state['role'] = user_role


if 'data_df' not in st.session_state:
    st.session_state['data_df'] = data_manager.load_user_data(
        'data.csv',                     # The file on switch drive where the data is stored
        initial_value=pd.DataFrame(),   # Initial value if the file does not exist
        parse_dates=['timestamp']       # Parse timestamp as datetime
    )


st.set_page_config(page_title="Meine App", page_icon=":material/home:")

# Navigation basierend auf Rolle
user_role = st.session_state.get('role', 'student')

if user_role == 'teacher':
    # Lehrer-Navigation
    pg_home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
    pg_archive = st.Page("views/archive_teacher.py", title="Archiv", icon=":material/archive:")
    pg_profile = st.Page("views/profile.py", title="Profil", icon=":material/person:")
    pages = [pg_home, pg_archive, pg_profile]
else:
    # Schüler-Navigation
    pg_home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
    pg_archive = st.Page("views/archive_student.py", title="Archiv", icon=":material/archive:")
    pg_profile = st.Page("views/profile.py", title="Profil", icon=":material/person:")
    pages = [pg_home, pg_archive, pg_profile]

pg = st.navigation(pages)
pg.run()