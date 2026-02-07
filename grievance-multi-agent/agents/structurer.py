from utils.llm import get_llm

def run_structurer(state):
    llm = get_llm("gemini")
    with open("prompts/structurer.txt") as f:
        system_prompt = f.read()

    return llm.invoke(
        system_prompt
        + "\n\nGrievance:\n" + state["user_input"]
        + "\n\nLegal Analysis:\n" + state["legal_validation"]
    ).content
