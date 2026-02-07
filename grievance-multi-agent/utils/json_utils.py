import json
import re

def extract_json(text: str):
    """
    Extracts the first valid JSON object from a string.
    Raises ValueError if none found.
    """
    if not text or not text.strip():
        raise ValueError("Empty response")

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")

    return json.loads(match.group())
