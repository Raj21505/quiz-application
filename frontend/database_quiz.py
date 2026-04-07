# frontend/database_quiz.py
import requests
import streamlit as st
# from backend.schema import Quiz
import os
from pydantic import BaseModel
from typing import Optional

class Quiz(BaseModel):
    id: Optional[int]
    Que: str
    A: str
    B: str
    C: str
    D: str
    Ans: str

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Use environment variable for API_BASE, default to local backend for non-docker runs.
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

class SqlQuiz:
    """Handles all communication with FastAPI backend."""

    def _auth_headers(self):
        token = st.session_state.get("id_token")
        if not token:
            st.error("Please login first. Firebase token is missing.")
            return None
        return {"Authorization": f"Bearer {token}"}
    
    def _load(self) -> list[Quiz]:
        try:
            r = requests.get(f"{API_BASE}/questions", timeout=5)
            if r.status_code == 200:
                data = r.json()
                # Ensure data is parsed correctly as Quiz objects
                return sorted([Quiz(**item) for item in data], key=lambda q: q.id)
            elif r.status_code == 404 and r.text and "detail" in r.json().keys():
                st.error(f"API Error (404): {r.json()['detail']}")
            else:
                st.error(f"Failed to fetch questions from API. Status: {r.status_code}")
                st.write(f"Check if the backend service is running and accessible at '{API_BASE}'.")
        except requests.exceptions.ConnectionError:
            st.error(f"Connection Error: Could not connect to the FastAPI backend ({API_BASE}).")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            
        return []

    def insert_question(self, que, A, B, C, D, Ans):
        payload = {"Que": que, "A": A, "B": B, "C": C, "D": D, "Ans": Ans}
        try:
            headers = self._auth_headers()
            if not headers:
                return False
            r = requests.post(f"{API_BASE}/questions", json=payload, headers=headers, timeout=5)
            return r.status_code in (200, 201)
        except:
            return False

    # def insert_question(self, que, A, B, C, D, Ans):
    #     st.write("Posting to:", f"{API_BASE}/questions")
    #     payload = {"Que": que, "A": A, "B": B, "C": C, "D": D, "Ans": Ans}
    #     try:
    #         r = requests.post(f"{API_BASE}/questions", json=payload, timeout=5)
    #         if r.status_code != 200 and r.status_code != 201:
    #             st.error(f"Failed to add question via API. Status: {r.status_code}. Response: {r.text}")
    #     except requests.exceptions.ConnectionError:
    #         st.error("Connection Error: Could not connect to the FastAPI backend.")

    def delete_question(self, qid):
        try:
            headers = self._auth_headers()
            if not headers:
                return
            r = requests.delete(f"{API_BASE}/questions/{qid}", headers=headers, timeout=5)
            if r.status_code != 200:
                st.error(f"Failed to delete question via API. Status: {r.status_code}. Response: {r.text}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the FastAPI backend.")

    def update_question(self, qid, field, new_value):
        try:
            # 1. Fetch existing data
            r = requests.get(f"{API_BASE}/questions/{qid}", timeout=5)
            if r.status_code != 200:
                st.error("Question not found or API failed to fetch.")
                return

            q_data = r.json()
            # 2. Update the specific field
            q_data[field] = new_value
            
            # 3. Send the update
            headers = self._auth_headers()
            if not headers:
                return
            r2 = requests.put(f"{API_BASE}/questions/{qid}", json=q_data, headers=headers, timeout=5)
            if r2.status_code != 200:
                st.error(f"Failed to update question via API. Status: {r2.status_code}. Response: {r2.text}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the FastAPI backend.")


    def show_all_questions(self):
        questions = self._load()
        if not questions:
            st.info("No questions available.")
            return
        st.markdown("### 📋 All Questions")
        for i, q in enumerate(questions, start=1):
            st.markdown(
                f"**{i}. {q.Que}** \n"
                f"A. {q.A} \n"
                f"B. {q.B} \n"
                f"C. {q.C} \n"
                f"D. {q.D} \n"
                f"✅ Correct: {q.Ans}"
            )