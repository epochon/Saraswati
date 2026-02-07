import json
import re
from llm.gemini_client import gemini_call

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except:
        return None

def legal_debate(text, context):
    response = gemini_call(
        "You are a legal expert agent.",
        f"Context:\n{context}\nComplaint:\n{text}\nReturn JSON."
    )

    if response is None:
        return """{
            "category": "General",
            "argument": "Gemini quota exceeded, fallback applied",
            "confidence": 0.4
        }"""

    return response
