from groq import Groq
import os

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY not found. Check .env file.")

client = Groq(api_key=api_key)

# ✅ Use a STABLE model
GROQ_MODEL = "mixtral-8x7b-32768"
# Alternative fallback:
# GROQ_MODEL = "llama-3.1-8b-instant"

def groq_call(system_prompt, user_prompt):
    try:
        res = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return res.choices[0].message.content.strip()

    except Exception as e:
        # 🔥 graceful degradation (agent does NOT crash system)
        return """{
            "category": "General",
            "argument": "Groq model unavailable, fallback applied",
            "confidence": 0.2
        }"""
