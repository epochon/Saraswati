import streamlit as st
from utils.llm import get_llm
from utils.cache import cache_key


@st.cache_data(show_spinner=False)
def _cached_opposition(user_input: str, key: str):
    llm = get_llm()
    system_prompt = open("prompts/opposition.txt", encoding="utf-8").read()

    return llm.invoke(
        system_prompt + "\n\nGrievance:\n" + user_input
    ).content


def run_opposition(state):
    user_input = state["user_input"]
    return _cached_opposition(user_input, cache_key(user_input))
