from llm.tavily_client import tavily_search
from llm.gemini_client import gemini_call

def legal_reasoning(category):
    sources = tavily_search(f"{category} law India")

    return gemini_call(
        "You are a legal advisor.",
        f"Sources:\n{sources}\nExplain applicable law and next steps."
    )
