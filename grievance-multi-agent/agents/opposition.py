from utils.llm import get_llm

def run_opposition(state):
    llm = get_llm("groq")
    with open("prompts/opposition.txt") as f:
        system_prompt = f.read()

    return llm.invoke(
        system_prompt + "\n\nGrievance:\n" + state["user_input"]
    ).content
