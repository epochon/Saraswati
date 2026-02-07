from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os

def get_llm(provider="gemini"):
    if provider == "groq":
        return ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY")
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
