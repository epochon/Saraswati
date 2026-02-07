from utils.llm import get_llm

def run_advocate(state):
    llm = get_llm()
    with open("prompts/advocate.txt") as f:
        system_prompt = f.read()

    return llm.invoke(
        system_prompt + "\n\nGrievance:\n" + state["user_input"]
    ).content
