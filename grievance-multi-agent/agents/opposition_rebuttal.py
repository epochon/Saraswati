from utils.llm import get_llm

def run_opposition_rebuttal(state):
    llm = get_llm()
    prompt = open("prompts/opposition_rebuttal.txt").read()
    return llm.invoke(
        prompt + "\n\nAdvocate:\n" + state["rounds"]["advocate_raw"]
    ).content
