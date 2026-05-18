import streamlit as st
import pandas as pd
from utils.app_config import get_data_manager
from utils.log_manager import LogManager
from utils.document_manager import DocumentManager
from functions.profile_functions import (
    get_user_info_dict,
    get_role_display,
    get_assigned_documents_status,
    render_document_status_legend
)
from functions.ui_helpers import render_user_info_columns

st.title("👤 Mein Profil")

data_manager = get_data_manager()
log_manager = LogManager(data_manager)
document_manager = DocumentManager(data_manager)

# Benutzerdaten aus Session State
user_info = get_user_info_dict(st.session_state)
role_display = get_role_display(user_info['role'])

# Anzeigen in Spalten
render_user_info_columns(
    user_info['name'],
    user_info['username'],
    user_info['email'],
    role_display
)

st.divider()

# Zeige Dokumentstatus für Schüler
user_class = st.session_state.get('class', None)

if not user_class:
    st.info("Du bist keiner Klasse zugeordnet.")
else:
    status_rows = get_assigned_documents_status(
        document_manager,
        log_manager,
        user_info['username'],
        user_class
    )
    
    if status_rows:
        st.dataframe(pd.DataFrame(status_rows), hide_index=True, use_container_width=True)
    else:
        st.info("Für deine Klasse sind keine Dokumente vorhanden.")

render_document_status_legend()