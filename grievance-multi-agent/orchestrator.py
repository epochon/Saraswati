from utils.json_utils import extract_json
from agents.advocate import run_advocate
from agents.opposition import run_opposition
from agents.advocate_rebuttal import run_advocate_rebuttal
from agents.opposition_rebuttal import run_opposition_rebuttal
from agents.legal_advisor import run_legal
from agents.structurer import run_structurer


def run_debate(state):

    state["rounds"] = {}

    # ---------------- Round 1: Initial Arguments ----------------
    state["rounds"]["advocate_raw"] = run_advocate(state)
    state["rounds"]["opposition_raw"] = run_opposition(state)

    try:
        state["rounds"]["advocate"] = extract_json(
            state["rounds"]["advocate_raw"]
        )
    except Exception:
        raise RuntimeError(
            "Advocate agent returned invalid JSON.\n\n"
            f"Raw output:\n{state['rounds']['advocate_raw']}"
        )

    try:
        state["rounds"]["opposition"] = extract_json(
            state["rounds"]["opposition_raw"]
        )
    except Exception:
        raise RuntimeError(
            "Opposition agent returned invalid JSON.\n\n"
            f"Raw output:\n{state['rounds']['opposition_raw']}"
        )

    # ---------------- Round 2: Rebuttals (Symmetric) ----------------
    state["rounds"]["advocate_rebuttal_raw"] = run_advocate_rebuttal(state)
    state["rounds"]["opposition_rebuttal_raw"] = run_opposition_rebuttal(state)

    try:
        state["rounds"]["advocate_rebuttal"] = extract_json(
            state["rounds"]["advocate_rebuttal_raw"]
        )
    except Exception:
        raise RuntimeError(
            "Advocate rebuttal returned invalid JSON.\n\n"
            f"{state['rounds']['advocate_rebuttal_raw']}"
        )

    try:
        state["rounds"]["opposition_rebuttal"] = extract_json(
            state["rounds"]["opposition_rebuttal_raw"]
        )
    except Exception:
        raise RuntimeError(
            "Opposition rebuttal returned invalid JSON.\n\n"
            f"{state['rounds']['opposition_rebuttal_raw']}"
        )

    # ---------------- Round 3: Legal Validation (FIXED) ----------------
    raw_legal = run_legal(state)

    try:
        state["legal_validation"] = extract_json(raw_legal)
    except Exception:
        # Safe fallback: legal agent failed or refused
        state["legal_validation"] = {
            "legal_assessment": [
                {
                    "argument": "Legal analysis could not be reliably generated.",
                    "status": "invalid",
                    "law": "N/A",
                    "reason": raw_legal
                }
            ]
        }

    # ---------------- Round 4: Final Structured Report ----------------
    state["final_report"] = run_structurer(state)

    return state
