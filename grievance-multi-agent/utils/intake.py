# utils/intake.py
"""
Responsible ONLY for validating user grievance intake.
No UI code. No agent code.
"""

REQUIRED_FIELDS = {
    "Name": [
        "my name is",
        "i am ",
        "this is ",
    ],
    "Place / Location": [
        " in ",
        " at ",
        " from ",
        " located in ",
    ],
    "What happened": [
        "happened",
        "occurred",
        "issue",
        "problem",
        "complaint",
        "incident",
    ],
    "Who caused the issue": [
        "by ",
        "because",
        "due to",
        "caused by",
        "responsible",
    ],
}


def validate_intake(text: str):
    """
    Validates whether the grievance contains required details.

    Returns:
        is_valid (bool): True if all required fields are present
        missing_fields (list[str]): List of missing field names
    """
    if not text or not text.strip():
        return False, list(REQUIRED_FIELDS.keys())

    text = text.lower()
    missing_fields = []

    for field, keywords in REQUIRED_FIELDS.items():
        if not any(keyword in text for keyword in keywords):
            missing_fields.append(field)

    return len(missing_fields) == 0, missing_fields
