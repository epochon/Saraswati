import os
import streamlit as st
from utils.llm import get_llm
from utils.cache import cache_key

# -------------------------------------------------
# Resolve prompt path safely
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "..", "prompts", "legal.txt")



@st.cache_data(show_spinner=False)
def _cached_legal(user_input: str, rounds_json: str, key: str):
    llm = get_llm()

    with open(PROMPT_PATH, encoding="utf-8") as f:
        system_prompt = f.read()

    response = llm.invoke(
        system_prompt
        + "\n\nGrievance:\n" + user_input
        + "\n\nDebate Rounds:\n" + rounds_json
    )

    return response.content


def run_legal(state):
    return _cached_legal(
        state["user_input"],
        str(state["rounds"]),
        cache_key(state["user_input"])
    )
