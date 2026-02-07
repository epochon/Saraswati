from utils.llm import get_llm

def run_legal(state):
    llm = get_llm()
    combined = "\n".join(state["rounds"].values())
    return llm.invoke(
        f"Assess legality under Indian law:\n{combined}"
    ).content
