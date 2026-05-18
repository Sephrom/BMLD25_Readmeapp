import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton class that manages user authentication for the application.

    Handles user login, registration, and session management using
    streamlit-authenticator. Credentials are stored in a YAML file via
    the DataManager.
    """

    def __new__(cls, *args, **kwargs):
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        instance = super(LoginManager, cls).__new__(cls)
        st.session_state.login_manager = instance
        return instance

    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        if hasattr(self, 'authenticator'):
            return
        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name

        try:
            auth_settings = st.secrets.get("auth", {})
            self.auth_cookie_key = auth_settings.get("cookie_key")
            self.teacher_code_secret = auth_settings.get("teacher_code")
        except Exception:
            st.error("❌ Fehler: .streamlit/secrets.toml nicht gefunden oder nicht lesbar.")
            st.stop()

        if not self.teacher_code_secret:
            st.error("❌ Fehler: 'auth.teacher_code' nicht in .streamlit/secrets.toml konfiguriert.")
            st.stop()

        if not self.auth_cookie_key:
            self.auth_cookie_key = secrets.token_urlsafe(32)

        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(
            self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key
        )

    def _load_auth_credentials(self):
        return self.data_manager.load_app_data(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        self.data_manager.save_app_data(self.auth_credentials, self.auth_credentials_file)

    def login_register(self, login_title='Login', register_title='Register new user'):
        if st.session_state.get("authentication_status") is True:
            with st.sidebar:
                st.write(f"Angemeldet als: **{st.session_state.get('name')}**")
                self.authenticator.logout()
        else:
            page_fn = lambda: self._login_register_page(login_title, register_title)
            pg = st.navigation([st.Page(page_fn, title="Login", icon=":material/login:")])
            pg.run()
            st.stop()

    def _login_register_page(self, login_title, register_title):
        login_tab, register_tab = st.tabs((login_title, register_title))
        with login_tab:
            self._login()
        with register_tab:
            self._register()

    def _login(self):
        self.authenticator.login()
        if st.session_state["authentication_status"] is False:
            st.error("Username/password is incorrect")
        else:
            st.warning("Please enter your username and password")

    def _register(self):
        st.info("""
        The password must be 8-20 characters long and include at least one uppercase letter,
        one lowercase letter, one digit, and one special character from @$!%*?&.
        """)

        try:
            teacher_code_secret = st.secrets.get("auth", {}).get("teacher_code")
            if not teacher_code_secret:
                st.error("❌ Fehler: 'auth.teacher_code' nicht in .streamlit/secrets.toml konfiguriert.")
                st.stop()
        except Exception:
            st.error("❌ Fehler: .streamlit/secrets.toml nicht gefunden oder nicht lesbar.")
            st.stop()

        teacher_code = st.text_input(
            "Lehrerzugangscode (optional)",
            type="password",
            help="Nur ausfüllen, wenn Sie ein Lehrer sind"
        )

        res = self.authenticator.register_user(captcha=True)

        if res[1] is not None:
            if teacher_code == teacher_code_secret:
                role = "teacher"
                st.success("✓ Lehrer-Account erstellt")
            else:
                role = "student"
                st.success("✓ Schüler-Account erstellt")
                st.info("Dein Account wurde erstellt. Eine Lehrperson weist dich später einer Klasse zu.")

            if res[1] in self.auth_credentials['usernames']:
                self.auth_credentials['usernames'][res[1]]['role'] = role
                self.auth_credentials['usernames'][res[1]]['class'] = None

            try:
                self._save_auth_credentials()
                st.success(f"✓ User {res[1]} registered successfully")
            except Exception as e:
                st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")