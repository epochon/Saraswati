import google.generativeai as genai
import os
import time
from google.api_core.exceptions import ResourceExhausted

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def gemini_call(system_prompt, user_prompt, retries=2):
    for attempt in range(retries):
        try:
            response = model.generate_content(
                f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}"
            )
            return response.text.strip()

        except ResourceExhausted as e:
            if attempt < retries - 1:
                time.sleep(8)  # wait as Gemini suggests
            else:
                # 🔥 graceful fallback signal
                return None

        except Exception:
            return None
