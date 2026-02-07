from utils.llm import get_llm

def run_structurer(state):
    llm = get_llm()
    return llm.invoke(
        f"""
User grievance: {state['user_input']}

Legal assessment:
{state['legal_validation']}

Write a formal complaint:
"""
    ).content
