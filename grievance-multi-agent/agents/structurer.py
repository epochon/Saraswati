from utils.llm import get_llm
from utils.json_utils import extract_json

def run_structurer(state):
    llm = get_llm()

    with open("prompts/structurer.txt", encoding="utf-8") as f:
        prompt = f.read()

    response = llm.invoke(
        prompt
        + "\n\nUser grievance:\n"
        + state["user_input"]
        + "\n\nLegal analysis:\n"
        + str(state["legal_validation"])
    )

    return response.content
