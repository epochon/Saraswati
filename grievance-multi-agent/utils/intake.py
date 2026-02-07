import re

REQUIRED_FIELDS = {
    "Name": [
        r"\bmy name is\b",
        r"\bi am\b"
    ],
    "Location": [
        r"\bi live in\b",
        r"\bresident of\b",
        r"\bin\b\s+[A-Za-z ]+"
    ],
    "Incident Description": [
        r"\bpower outage\b",
        r"\bno power\b",
        r"\bissue\b",
        r"\bproblem\b"
    ],
    "Responsible Authority": [
        r"\bbescom\b",
        r"\belectricity board\b",
        r"\bkerala state electricity board\b",
        r"\bdiscom\b"
    ],
    "Impact": [
        r"\baffected\b",
        r"\bloss\b",
        r"\bincome\b",
        r"\bwork\b",
        r"\bdaily\b"
    ]
}


def validate_intake(text: str):
    """
    Validates whether the grievance contains semantically required information.
    Returns (is_valid, missing_fields)
    """

    text = text.lower()
    missing = []

    for field, patterns in REQUIRED_FIELDS.items():
        if not any(re.search(p, text) for p in patterns):
            missing.append(field)

    return len(missing) == 0, missing
