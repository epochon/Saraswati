import json
import re

def safe_json_extract(text):
    """
    Safely extracts JSON from LLM output.
    Returns dict or None.
    """
    if not text:
        return None

    try:
        # Direct JSON
        return json.loads(text)
    except Exception:
        pass

    # Try extracting JSON inside text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            return None

    return None
