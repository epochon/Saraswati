import streamlit as st
from utils.llm import get_llm
from utils.cache import cache_key
import json


@st.cache_data(show_spinner=False)
def _cached_structurer(user_input: str, legal_json: str, key: str):
    llm = get_llm()
    prompt = open("prompts/structurer.txt", encoding="utf-8").read()

    return llm.invoke(
        prompt
        + "\n\nGrievance:\n" + user_input
        + "\n\nLegal:\n" + legal_json
    ).content


def run_structurer(state):
    return _cached_structurer(
        state["user_input"],
        json.dumps(state["legal_validation"], indent=2),
        cache_key(state["user_input"])
    )
