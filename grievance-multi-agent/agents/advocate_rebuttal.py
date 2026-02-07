from utils.llm import get_llm

def run_advocate_rebuttal(state):
    llm = get_llm()
    prompt = open("prompts/advocate_rebuttal.txt").read()
    return llm.invoke(
        prompt + "\n\nOpposition:\n" + state["rounds"]["opposition_raw"]
    ).content
