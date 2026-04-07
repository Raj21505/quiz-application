# frontend/admin/admin_main.py
import streamlit as st
import os

try:
    from database_quiz import SqlQuiz
except ImportError:
    from frontend.database_quiz import SqlQuiz

class AdminQuiz:
    def __init__(self):
        self._username = os.getenv("ADMIN_USERNAME", "admin")
        self._password = os.getenv("ADMIN_PASSWORD", "2005")
        self.data_handler = SqlQuiz()

    def _authenticate(self, username: str, password: str) -> bool:
        return username == self._username and password == self._password

    def run(self):  
        st.header("👩‍💼 Admin Panel")

        if "admin_authenticated" not in st.session_state:
            st.session_state.admin_authenticated = False

        if not st.session_state.admin_authenticated:
            self._login_ui()
            return

        self._dashboard()

    def _login_ui(self):
        if self._username == "admin" and self._password == "2005":
            st.warning("Default admin credentials are active. Set ADMIN_USERNAME and ADMIN_PASSWORD in deployment.")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if self._authenticate(username.strip(), password):
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_action = "menu"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    def _dashboard(self):
        # Always display the menu select box
        choice = st.selectbox(
            "Select Activity",
            ["Select", "Add Question", "Delete Question", "Update Question", "View All", "Logout"],
            key="menu_select",
            on_change=self._on_menu_change
        )
        
        if choice == "Logout":
            st.session_state.admin_authenticated = False
            st.session_state.admin_action = "menu"
            for key in [
                "menu_select",
                "add_done",
                "delete_done",
                "update_done",
                "delete_select",
                "update_select",
                "update_field",
                "update_new_value",
                "update_new_ans",
                "add_q_question",
                "add_q_a",
                "add_q_b",
                "add_q_c",
                "add_q_d",
                "add_q_ans",
                "repeat_add_radio",
                "repeat_delete_radio",
                "repeat_update_radio",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            return

        # Handle actions based on session state
        action = st.session_state.get("admin_action")
        
        if action == "Add Question":
            self._ui_add_question()
        elif action == "Delete Question":
            self._ui_delete_question()
        elif action == "Update Question":
            self._ui_update_question()
        elif action == "View All":
            self.data_handler.show_all_questions()
            if st.button("🔙 Back to Menu"):
                st.session_state.admin_action = "menu"
                st.rerun()
        # else: action is "menu" or "Select", show nothing more

    def _on_menu_change(self):
        sel = st.session_state.get("menu_select")
        if sel and sel != "Select" and sel != "Logout":
            st.session_state.admin_action = sel
            # Clear previous action state flags to ensure fresh UI
            for key in ["add_done", "delete_done", "update_done"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun() # Rerun to switch view immediately

    def _repeat_or_return_after_action(self, action: str, success_message: str, keys_to_clear: list):
        st.success(success_message)
        repeat_key = f"repeat_{action}_radio"

        repeat = st.radio(
            f"Do you want to {action} again?",
            ["Yes", "No"],
            index=None,
            key=repeat_key
        )
    
        if repeat == "Yes":
            # Clear all relevant keys for a fresh form
            for key in keys_to_clear + [repeat_key]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state[f"{action}_done"] = False
            st.rerun()

        elif repeat == "No":
            st.session_state.admin_action = "menu"
            st.session_state[f"{action}_done"] = False
            # Clear temporary radio key
            if repeat_key in st.session_state:
                del st.session_state[repeat_key]
            st.rerun()

    def _ui_add_question(self):
        st.subheader("➕ Add a New Question")

        if "add_done" not in st.session_state:
            st.session_state.add_done = False

        if not st.session_state.add_done:
            # Use a form structure to capture all inputs before running logic
            with st.form("add_question_form", clear_on_submit=False):
                # Note: The 'value' argument here uses session state for stickiness, which is fine.
                question = st.text_input("Enter Question:", key="add_q_question", value=st.session_state.get("add_q_question", "")).strip()
                opt_a = st.text_input("Option A:", key="add_q_a", value=st.session_state.get("add_q_a", "")).strip()
                opt_b = st.text_input("Option B:", key="add_q_b", value=st.session_state.get("add_q_b", "")).strip()
                opt_c = st.text_input("Option C:", key="add_q_c", value=st.session_state.get("add_q_c", "")).strip()
                opt_d = st.text_input("Option D:", key="add_q_d", value=st.session_state.get("add_q_d", "")).strip()
                answer = st.selectbox("Correct Answer:", ["Select", "A", "B", "C", "D"], index=0, key="add_q_ans")
                
                submitted = st.form_submit_button("Submit Question")
                
                if submitted:
                    if not all([question, opt_a, opt_b, opt_c, opt_d]):
                        st.error("❌ All fields are required.")
                        return
                    if answer == "Select":
                        st.error("❌ Please select the correct answer.")
                        return

                    # Use the local variables (question, opt_a, etc.) which hold the submitted value
                    # self.data_handler.insert_question(question, opt_a, opt_b, opt_c, opt_d, answer)
                    success = self.data_handler.insert_question(question, opt_a, opt_b, opt_c, opt_d, answer)
                    if success:
                        st.session_state.add_done = True
                        st.rerun() # Rerun to display success message outside of form
                    else:
                        st.error("Failed to add question")

                    # st.session_state.add_done = True
        else:
            self._repeat_or_return_after_action(
                action="add",
                success_message="✅ Question added successfully!",
                keys_to_clear=["add_q_question", "add_q_a", "add_q_b", "add_q_c", "add_q_d", "add_q_ans"]
            )

    def _ui_delete_question(self):
        st.subheader("🗑️ Delete Question")

        if "delete_done" not in st.session_state:
            st.session_state.delete_done = False

        if not st.session_state.delete_done:
            qlist = self.data_handler._load()
            if not qlist:
                st.info("ℹ️ No questions available to delete.")
                return

            options = [
                f"{i+1}. Question : {q.Que}, A : {q.A}, B : {q.B}, "
                f"C : {q.C}, D : {q.D}, Answer : {q.Ans}"
                for i, q in enumerate(qlist)
            ]
            options_dict = {options[i]: qlist[i].id for i in range(len(options))}
            
            sel_text = st.selectbox("Select a question to delete:", options, index=None, key="delete_select")
            
            if sel_text and st.button("Delete Question"):
                qid = options_dict[sel_text]
                self.data_handler.delete_question(qid)
                st.session_state.delete_done = True
                st.rerun()
        else:
            self._repeat_or_return_after_action(
                action="delete",
                success_message="✅ Deleted Successfully!",
                keys_to_clear=["delete_select"]
            )

    def _ui_update_question(self):
        st.subheader("✏️ Update Question")

        if "update_done" not in st.session_state:
            st.session_state.update_done = False
            
        if not st.session_state.update_done:
            qlist = self.data_handler._load()
            if not qlist:
                st.info("ℹ️ No questions available to update.")
                return

            options = [
                f"{i+1}. Question : {q.Que}, A : {q.A}, B : {q.B}, "
                f"C : {q.C}, D : {q.D}, Answer : {q.Ans}"
                for i, q in enumerate(qlist)
            ]
            options_dict = {options[i]: qlist[i] for i in range(len(options))}
            
            sel_text = st.selectbox("Select a question to update:", options, index=None, key="update_select")
            
            if not sel_text:
                st.warning("⚠️ Please select a question to update.")
                return
                
            q = options_dict[sel_text]
            qid = q.id
            
            # Mapping field selection to model attribute name
            field_map = {
                "Question": "Que", 
                "A": "A", 
                "B": "B", 
                "C": "C", 
                "D": "D", 
                "Answer": "Ans"
            }
            
            field_display = st.selectbox("Which field do you want to update?", 
                                         ["Select"] + list(field_map.keys()), 
                                         key="update_field")
            
            field_name = field_map.get(field_display)

            if field_name:
                current_value = getattr(q, field_name)
                
                if field_name == "Ans":
                    new_value = st.selectbox("Select new correct answer:", ["A", "B", "C", "D"], 
                                             index=["A", "B", "C", "D"].index(current_value) if current_value in ["A", "B", "C", "D"] else None,
                                             key="update_new_ans")
                else:
                    new_value = st.text_input(f"Enter new value for {field_display}:", 
                                              value=current_value, 
                                              key="update_new_value").strip()
                    
                if st.button("Save Update"):
                    if not new_value:
                        st.error("❌ Value cannot be empty.")
                        return

                    self.data_handler.update_question(qid, field_name, new_value)
                    st.session_state.update_done = True
                    st.rerun()
        else:
            self._repeat_or_return_after_action(
                action="update",
                success_message="✅ Update completed successfully!",
                keys_to_clear=["update_select", "update_field", "update_new_value", "update_new_ans"]
            )

    