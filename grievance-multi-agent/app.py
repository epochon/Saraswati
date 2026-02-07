import os
import streamlit as st
from dotenv import load_dotenv

# -------------------------------------------------
# Force-load .env using absolute path (Streamlit-safe)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -------------------------------------------------
# Validate environment variables early (FAIL FAST)
# -------------------------------------------------
if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GROQ_API_KEY"):
    st.error(
        "❌ No LLM API key found.\n\n"
        "Please set GOOGLE_API_KEY or GROQ_API_KEY in your .env file."
    )
    st.stop()

# -------------------------------------------------
# App imports (AFTER env is loaded)
# -------------------------------------------------
from utils.state import init_state
from orchestrator import run_debate

# -------------------------------------------------
# Streamlit UI
# -------------------------------------------------
st.set_page_config(page_title="AI Grievance System (India)", layout="centered")

st.title("🇮🇳 Multi-Agent AI Grievance System")

st.markdown(
    """
This system uses **multiple debating AI agents**:
- 🟢 Advocate (supports you)
- 🔴 Opposition (challenges your case)
- ⚖️ Legal Advisor (Indian law)
- 📄 Structuring Agent (final complaint)

The best outcome emerges through **controlled debate**.
"""
)

user_input = st.text_area(
    "Describe your grievance",
    placeholder="Explain the issue, location, authority involved, timeline, and impact...",
    height=200
)

# -------------------------------------------------
# Run Debate
# -------------------------------------------------
if st.button("Analyze & Generate Complaint", type="primary"):
    if not user_input.strip():
        st.warning("⚠️ Please describe your grievance before proceeding.")
        st.stop()

    with st.spinner("Running multi-agent legal debate..."):
        state = init_state(user_input)
        result = run_debate(state)

    st.divider()

    st.subheader("🟢 Advocate Agent (For You)")
    st.write(result["rounds"]["advocate"])

    st.subheader("🔴 Opposition Agent (Against You)")
    st.write(result["rounds"]["opposition"])

    st.subheader("⚖️ Legal Advisor (India)")
    st.write(result["legal_validation"])

    st.subheader("📄 Final Complaint / Report")
    st.write(result["final_report"])
