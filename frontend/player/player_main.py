# frontend/player/player_main.py
import streamlit as st

try:
    from database_quiz import SqlQuiz
except ImportError:
    from frontend.database_quiz import SqlQuiz

class PlayerQuiz:
    """Player UI — shows one question at a time with Previous/Next and Submit at end."""
    
    def __init__(self):
        self.data_handler = SqlQuiz()
        # Initialize session state keys for the quiz
        if "current_q" not in st.session_state:
            st.session_state.current_q = 0
        if "answers" not in st.session_state:
            st.session_state.answers = {}
        if "quiz_submitted" not in st.session_state:
            st.session_state.quiz_submitted = False
        if "questions_list" not in st.session_state:
            st.session_state.questions_list = []

    def run(self):
        st.header("🎯 Quiz Player")
        st.markdown(
            """
            *Rules*
            - Each correct answer = +1 point  
            - Navigate using Previous and Next buttons  
            - Submit only at the last question
            """
        )

        # Load questions once and store in session state
        if not st.session_state.questions_list:
            questions = self.data_handler._load()
            if not questions:
                st.warning("⚠ No questions available. Ask Admin to add questions.")
                return
            st.session_state.questions_list = questions
        
        questions = st.session_state.questions_list
        total = len(questions)

        if st.session_state.quiz_submitted:
            self._show_results(questions, total)
            return

        self._show_quiz_interface(questions, total)

    def _show_results(self, questions, total):
        score = sum(
            1 for i, question in enumerate(questions)
            if st.session_state.answers.get(question.id) == question.Ans
        )
        st.success(f"🎉 You scored {score} out of {total}!")
        
        st.markdown("---")
        st.subheader("Answer Key")
        
        for i, q in enumerate(questions, start=1):
            player_answer = st.session_state.answers.get(q.id)
            is_correct = player_answer == q.Ans
            icon = "✅" if is_correct else "❌"
            
            st.markdown(f"**{i}. {q.Que}**")
            st.markdown(f"Your Answer: **{player_answer if player_answer else 'Skipped'}** {icon}")
            if not is_correct:
                st.markdown(f"Correct Answer: **{q.Ans}**")
            st.markdown("---")

        if st.button("🔁 Try Again"):
            self._reset_quiz()
            st.rerun()

    def _show_quiz_interface(self, questions, total):
        idx = st.session_state.current_q
        q = questions[idx]
        
        st.markdown(f"### Question {idx + 1} / {total}")
        st.markdown(f"**{q.Que}**")
        st.write(f"A: {q.A}")
        st.write(f"B: {q.B}")
        st.write(f"C: {q.C}")
        st.write(f"D: {q.D}")
        
        # Determine current selection from session state
        default_answer = st.session_state.answers.get(q.id)
        default_index = ["A", "B", "C", "D"].index(default_answer) + 1 if default_answer else 0
        
        # Use a common key structure for the selectbox value
        answer_key = f"answer_q_{q.id}"

        with st.form(key=f"form_q_{q.id}"):
            selected = st.radio(
                "Choose your answer:",
                ["A", "B", "C", "D"],
                index=default_index if default_index > 0 else None,
                key=answer_key
            )
            
            col1, col2 = st.columns([1, 1])
            
            # Previous Button (col1)
            if idx > 0:
                if col1.form_submit_button("⬅ Previous"):
                    # Save current answer before moving
                    st.session_state.answers[q.id] = selected
                    st.session_state.current_q -= 1
                    st.rerun()

            # Next/Submit Button (col2)
            submit_label = "Submit Quiz" if idx == total - 1 else "Next ➡"
            if col2.form_submit_button(submit_label):
                # Save the answer for the current question
                st.session_state.answers[q.id] = selected

                if idx < total - 1:
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    # Logic for Submit
                    answered_count = len(st.session_state.answers)
                    if answered_count < total:
                        st.warning(f"⚠ You have only answered {answered_count} out of {total} questions. Please answer all to submit.")
                        # Do not submit, stay on current page
                    else:
                        st.session_state.quiz_submitted = True
                        st.rerun()

    def _reset_quiz(self):
        # Clear all quiz-related session state keys
        keys_to_clear = [key for key in st.session_state.keys() 
                         if key in ["current_q", "answers", "quiz_submitted", "questions_list"] 
                         or key.startswith("answer_q_")]
        
        for key in keys_to_clear:
            del st.session_state[key]