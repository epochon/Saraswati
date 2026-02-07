from utils.llm import get_llm

def run_legal(state):
    llm = get_llm()
    prompt = open("prompts/legal.txt").read()
    context = (
        state["rounds"]["advocate_raw"] + "\n" +
        state["rounds"]["opposition_raw"] + "\n" +
        state["rounds"]["advocate_rebuttal_raw"] + "\n" +
        state["rounds"]["opposition_rebuttal_raw"]
    )
    return llm.invoke(prompt + "\n\nContext:\n" + context).content
