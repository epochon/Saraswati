import streamlit as st
from utils.llm import get_llm
from utils.cache import cache_key


@st.cache_data(show_spinner=False)
def _cached_advocate_rebuttal(user_input: str, opponent_json: str, key: str):
    llm = get_llm()
    prompt = open("prompts/advocate_rebuttal.txt", encoding="utf-8").read()

    return llm.invoke(
        prompt
        + "\n\nGrievance:\n" + user_input
        + "\n\nOpposition:\n" + opponent_json
    ).content


def run_advocate_rebuttal(state):
    if "opposition" not in state["rounds"]:
        raise RuntimeError("Opposition arguments not available for rebuttal")

    return _cached_advocate_rebuttal(
        state["user_input"],
        str(state["rounds"]["opposition"]),
        cache_key(state["user_input"])
    )

