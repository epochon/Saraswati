import os

from utils.llm import get_llm


def _get_tavily_key():
    return os.getenv("TAVILY_API") or os.getenv("TAVILY_API_KEY")


def _tavily_rag(query, max_results=5):
    api_key = _get_tavily_key()
    if not api_key:
        return ""

    try:
        from tavily import TavilyClient
    except Exception:
        return ""

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=True,
        )
    except Exception:
        return ""

    answer = (response.get("answer") or "").strip()
    results = response.get("results", [])

    lines = []
    if answer:
        lines.append(f"Summary: {answer}")

    for item in results:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        content = (item.get("content") or item.get("snippet") or "").strip()
        if content:
            content = " ".join(content.split())
        parts = [part for part in (title, content, url) if part]
        if parts:
            lines.append(" - ".join(parts))

    return "\n".join(lines).strip()

def run_legal(state):
    llm = get_llm()
    prompt = open("prompts/legal.txt").read()
    rag_context = _tavily_rag(
        f"latest judgments or laws in India relevant to: {state['user_input']}"
    )
    context = (
        state["rounds"]["advocate_raw"] + "\n" +
        state["rounds"]["opposition_raw"] + "\n" +
        state["rounds"]["advocate_rebuttal_raw"] + "\n" +
        state["rounds"]["opposition_rebuttal_raw"]
    )
    rag_block = ""
    if rag_context:
        rag_block = "\n\nRAG (Tavily - Latest Laws/Judgments):\n" + rag_context
    return llm.invoke(prompt + "\n\nContext:\n" + context + rag_block).content
