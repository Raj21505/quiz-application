# frontend/main.py
import streamlit as st
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from firebase_auth import sign_in, sign_up
except ImportError:
    from frontend.firebase_auth import sign_in, sign_up

try:
    from admin.admin_main import AdminQuiz
    from player.player_main import PlayerQuiz
except ImportError:
    from frontend.admin.admin_main import AdminQuiz
    from frontend.player.player_main import PlayerQuiz

class QuizApp:
    def _init_session(self):
        if "id_token" not in st.session_state:
            st.session_state.id_token = None
        if "firebase_email" not in st.session_state:
            st.session_state.firebase_email = None
        if "firebase_authenticated" not in st.session_state:
            st.session_state.firebase_authenticated = False
        if "admin_authenticated" not in st.session_state:
            st.session_state.admin_authenticated = False

    def _auth_ui(self):
        api_key = os.getenv("FIREBASE_WEB_API_KEY", "")
        if not api_key:
            st.error("Set FIREBASE_WEB_API_KEY in environment or frontend/.env to enable Firebase login.")
            return False

        if st.session_state.id_token:
            st.success(f"Logged in as {st.session_state.firebase_email}")
            if st.button("Logout"):
                st.session_state.id_token = None
                st.session_state.firebase_email = None
                st.session_state.firebase_authenticated = False
                st.session_state.admin_authenticated = False
                st.rerun()
            return True

        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            with st.form("firebase_login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    ok, data, err = sign_in(email.strip(), password, api_key)
                    if ok:
                        st.session_state.id_token = data.get("idToken")
                        st.session_state.firebase_email = data.get("email")
                        st.session_state.firebase_authenticated = True
                        st.rerun()
                    else:
                        st.error(f"Login failed: {err}")

        with tab_signup:
            with st.form("firebase_signup_form"):
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                submitted = st.form_submit_button("Create Account")
                if submitted:
                    ok, _data, err = sign_up(email.strip(), password, api_key)
                    if ok:
                        st.success("Account created. Please login from the Login tab.")
                    else:
                        st.error(f"Signup failed: {err}")

        return False

    def main(self):
        st.set_page_config(page_title="Quiz Application", layout="centered")
        st.title("🎓 Quiz Application")
        self._init_session()
        st.write("Authenticate with Firebase, then choose your role:")

        if not self._auth_ui():
            return

        # Initialize database connection on startup
        # Note: In a Docker setup, this might still run before DB is ready,
        # but FastAPI's startup event handles table creation more reliably.
        # Keeping it here for local non-docker runs as well.
        # init_db()

        role = st.selectbox("Select your role", ["Select", "Admin", "Player", "Leave"], index=0)

        if role == "Admin":
            admin = AdminQuiz()
            admin.run()

        elif role == "Player":
            player = PlayerQuiz()
            player.run()

        elif role == "Leave":
            st.info("👋 Exiting... Goodbye!")


if __name__ == "__main__":
    app = QuizApp()
    app.main()