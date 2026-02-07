from utils.llm import get_llm

def run_advocate(state):
    llm = get_llm()
    return llm.invoke(
        f"User grievance:\n{state['user_input']}"
    ).content
