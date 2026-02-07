from utils.llm import get_llm

def run_legal(state):
    llm = get_llm("gemini")
    with open("prompts/legal.txt") as f:
        system_prompt = f.read()

    combined_context = (
        state["user_input"] + "\n\n"
        + state["rounds"]["advocate"] + "\n\n"
        + state["rounds"]["opposition"]
    )

    return llm.invoke(
        system_prompt + "\n\nContext:\n" + combined_context
    ).content
