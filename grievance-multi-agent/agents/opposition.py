from utils.llm import get_llm

def run_opposition(state):
    llm = get_llm("groq")
    return llm.invoke(
        f"Challenge this grievance:\n{state['user_input']}"
    ).content
