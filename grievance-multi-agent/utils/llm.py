from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os

def get_llm(provider="groq"):
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0
    )

    
