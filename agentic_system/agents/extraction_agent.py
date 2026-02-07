import re
from llm.gemini_client import gemini_call
from .utils import safe_json_extract

def extract_info(text):
    response = gemini_call(
        system_prompt="You extract structured personal info from complaints.",
        user_prompt=f"""
Extract the following fields as JSON:
- name
- email
- phone

Use null if missing.
Complaint:
{text}
"""
    )

    # ✅ If Gemini worked, try JSON extraction
    if response:
        from .utils import safe_json_extract  # or wherever you defined it
        data = safe_json_extract(response)
        if data:
            return data

    # 🔁 FALLBACK (VERY IMPORTANT)
    name_match = re.search(
        r"(?:my name is|i am|this is)\s*([A-Za-z ]{3,})",
        text,
        re.IGNORECASE
    )

    phone_match = re.search(r"\b\d{10}\b", text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)

    return {
        "name": name_match.group(1).strip() if name_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "email": email_match.group(0) if email_match else None
    }
