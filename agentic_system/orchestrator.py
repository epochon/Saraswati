import json
from mcp import mcp
from agents.debate_legal import legal_debate
from agents.debate_citizen import citizen_debate
from agents.debate_infra import infra_debate
from agents.consensus_agent import decide

import json
import re

def safe_parse_json(text):
    """
    Safely extract and parse the first JSON object from text.
    """
    if not text:
        return None

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None
def normalize_response(resp):
    """
    Ensure agent response has all required keys.
    """
    return {
        "category": resp.get("category", "General"),
        "argument": resp.get("argument", "No clear argument provided"),
        "confidence": float(resp.get("confidence", 0.2))
    }

def run_debate(text, rounds=2):
    context = ""
    dialogue = []

    agents = [
        ("LegalAgent", legal_debate),
        ("CitizenAgent", citizen_debate),
        ("InfraAgent", infra_debate)
    ]

    for r in range(1, rounds + 1):
        for name, agent in agents:
            raw = agent(text, context)
            response = safe_parse_json(raw)

            if not response:
                response = {}

            response = normalize_response(response)

            dialogue.append(
                mcp(name, "ConsensusAgent", "ARGUMENT", response, r)
            )

            context += f"\n{name}: {response['argument']}"

    category = decide(dialogue)
    return category, dialogue
