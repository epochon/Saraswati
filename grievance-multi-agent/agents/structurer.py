import json
from utils.llm import get_llm

def run_structurer(state):
    llm = get_llm()
    prompt = open("prompts/structurer.txt", encoding="utf-8").read()

    legal_text = json.dumps(
        state["legal_validation"],
        indent=2,
        ensure_ascii=False
    )

    return llm.invoke(
        prompt
        + "\n\nGrievance:\n" + state["user_input"]
        + "\n\nLegal Analysis (JSON):\n" + legal_text
    ).content
