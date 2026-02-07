import os
import streamlit as st
from dotenv import load_dotenv

# -------------------------------------------------
# Load environment variables safely
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -------------------------------------------------
# Fail fast if no API key exists
# -------------------------------------------------
if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GROQ_API_KEY"):
    st.error(
        "❌ No LLM API key found.\n\n"
        "Please add GOOGLE_API_KEY or GROQ_API_KEY in your .env file."
    )
    st.stop()

# -------------------------------------------------
# Imports AFTER env is loaded
# -------------------------------------------------
from utils.state import init_state
from utils.intake import validate_intake
from orchestrator import run_debate

# -------------------------------------------------
# Streamlit UI
# -------------------------------------------------
st.set_page_config(
    page_title="AI Grievance System (India)",
    layout="centered"
)

st.title("🇮🇳 Multi-Agent AI Grievance System")

st.markdown(
    """
This system uses **multiple debating AI agents**:

- 🟢 **Advocate Agent** – argues in your favor  
- 🔴 **Opposition Agent** – challenges your case  
- ⚖️ **Legal Advisor** – evaluates under Indian law  
- 📄 **Structuring Agent** – produces a formal complaint  

⚠️ Your grievance **must include required details** before analysis.
"""
)

user_input = st.text_area(
    "Describe your grievance",
    placeholder=(
        "Example:\n"
        "My name is Evan. I live in Kochi, Kerala.\n"
        "There has been a power cut for 5 days caused by the Electricity Board.\n"
        "This has affected daily life and work."
    ),
    height=220
)

# -------------------------------------------------
# Run analysis ONLY after intake validation
# -------------------------------------------------
if st.button("Analyze & Generate Complaint", type="primary"):

    is_valid, missing_fields = validate_intake(user_input)

    if not is_valid:
        st.error("❌ Your grievance is missing required information.")
        st.markdown("### Please add the following details:")
        for field in missing_fields:
            st.write(f"- **{field}**")
        st.info(
            "Providing complete information helps generate a legally valid complaint."
        )
        st.stop()

    # Intake is valid → proceed to agents
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
