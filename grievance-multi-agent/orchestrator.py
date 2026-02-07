from agents.advocate import run_advocate
from agents.opposition import run_opposition
from agents.legal_advisor import run_legal
from agents.structurer import run_structurer

def run_debate(state):
    state["rounds"]["advocate"] = run_advocate(state)
    state["rounds"]["opposition"] = run_opposition(state)
    state["legal_validation"] = run_legal(state)
    state["final_report"] = run_structurer(state)
    return state
