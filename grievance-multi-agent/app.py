import os
import streamlit as st
from dotenv import load_dotenv
from utils.pdf import generate_complaint_pdf

# -------------------------------------------------
# Load environment variables safely
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -------------------------------------------------
# Fail fast if no API key exists (Groq is sufficient)
# -------------------------------------------------
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "❌ No LLM API key found.\n\n"
        "Please add GROQ_API_KEY in your .env file."
    )
    st.stop()

# -------------------------------------------------
# Imports AFTER env is loaded
# -------------------------------------------------
from utils.state import init_state
from utils.intake import validate_intake
from orchestrator import run_debate
from utils.render import (
    render_arguments_md,
    render_rebuttals_md,
    render_legal_md
)

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
This system runs a **structured, adversarial AI debate** to evaluate grievances.

### Agents involved:
- 🟢 **Advocate Agent** – supports the user (scored arguments)
- 🔴 **Opposition Agent** – challenges the user (scored objections)
- 🔁 **Rebuttal Round** – both sides counter each other
- ⚖️ **Legal Advisor** – applies Indian law
- 📄 **Structuring Agent** – produces a formal complaint

⚠️ Please provide **clear factual details**.
"""
)

# -------------------------------------------------
# User input
# -------------------------------------------------
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
# Main action
# -------------------------------------------------
if st.button("Analyze & Generate Complaint", type="primary"):

    if not user_input.strip():
        st.warning("⚠️ Please describe your grievance before proceeding.")
        st.stop()

    # ---------------- Step 1: Intake validation ----------------
    is_valid, missing_fields = validate_intake(user_input)

    if not is_valid:
        st.error("❌ Your grievance is missing required information.")
        st.markdown("### Please add the following details:")
        for field in missing_fields:
            st.write(f"- **{field}**")
        st.stop()

    # ---------------- Step 2: Run debate ----------------
    with st.spinner("Running multi-agent adversarial debate..."):
        state = init_state(user_input)
        st.session_state["result"] = run_debate(state)

# -------------------------------------------------
# DISPLAY RESULTS (only if they exist)
# -------------------------------------------------
if "result" in st.session_state:
    result = st.session_state["result"]

    st.divider()

    # ---------------- Round 1 ----------------
    st.subheader("🟢 Advocate Agent — Supporting Arguments")
    st.markdown(
        render_arguments_md(
            "Arguments Supporting the Complaint",
            result["rounds"]["advocate"]["arguments"]
        )
    )

    st.subheader("🔴 Opposition Agent — Critical Observations")
    st.markdown(
        render_arguments_md(
            "Weaknesses in the Complaint",
            result["rounds"]["opposition"]["arguments"]
        )
    )

    # ---------------- Round 2 ----------------
    st.subheader("🟢 Advocate Rebuttals")
    st.markdown(
        render_rebuttals_md(
            "Responses to Opposition",
            result["rounds"]["advocate_rebuttal"]["rebuttals"],
            key="rebuttal"
        )
    )

    st.subheader("🔴 Opposition Rebuttals")
    st.markdown(
        render_rebuttals_md(
            "Counter-Responses",
            result["rounds"]["opposition_rebuttal"]["counter_rebuttals"],
            key="counter"
        )
    )

    # ---------------- Legal ----------------
    st.markdown(
        render_legal_md(result["legal_validation"])
    )

    # ---------------- Final Report ----------------
    st.subheader("📄 Final Complaint / Report")
    st.markdown(result["final_report"])

    # ---------------- PDF Export ----------------
    st.divider()
    st.subheader("⬇️ Download Complaint")

    pdf_path = generate_complaint_pdf(
        result["final_report"],
        filename="AI_Grievance_Complaint.pdf"
    )

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📄 Download Complaint as PDF",
            data=f,
            file_name="AI_Grievance_Complaint.pdf",
            mime="application/pdf"
        )
