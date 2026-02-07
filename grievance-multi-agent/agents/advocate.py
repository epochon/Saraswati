import streamlit as st
from utils.llm import get_llm
from utils.cache import cache_key


@st.cache_data(show_spinner=False)
def _cached_advocate(user_input: str, key: str):
    llm = get_llm()

    system_prompt = open("prompts/advocate.txt", encoding="utf-8").read()

    response = llm.invoke(
        system_prompt + "\n\nGrievance:\n" + user_input
    )

    return response.content


def run_advocate(state):
    user_input = state["user_input"]
    return _cached_advocate(user_input, cache_key(user_input))
