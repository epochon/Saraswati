from llm.groq_client import groq_call

def citizen_debate(text, context):
    return groq_call(
        system_prompt="You represent the perspective of a common citizen affected by the issue.",
        user_prompt=f"""
Context:
{context}

Complaint:
{text}

Respond ONLY in valid JSON with:
- category
- argument
- confidence (0 to 1)
"""
    )
