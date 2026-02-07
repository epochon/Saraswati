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
# Streamlit UI setup
# -------------------------------------------------
st.set_page_config(
    page_title="AI Grievance System (India)",
    layout="centered"
)

st.title("🇮🇳 Multi-Agent AI Grievance System")

st.markdown(
    """
This system runs a **transparent, multi-round, adversarial AI analysis**.

### Analysis Phases:
1. 🟢 Advocate Agent
2. 🔴 Opposition Agent
3. 🔁 Rebuttal Round
4. ⚖️ Legal Validation
5. 📄 Complaint Structuring

You can **see progress live** while analysis is running.
"""
)

# -------------------------------------------------
# User input
# -------------------------------------------------
user_input = st.text_area(
    "Describe your grievance",
    placeholder=(
        "Example:\n"
        "My name is Ravi Kumar. I live in Bengaluru.\n"
        "I filed a complaint to BESCOM on 3 March 2026.\n"
        "Complaint No: 456789. Power outage lasted 7 days.\n"
        "This caused loss of income as I work from home."
    ),
    height=220
)

# -------------------------------------------------
# Run analysis button
# -------------------------------------------------
if st.button("Analyze & Generate Complaint", type="primary"):

    if not user_input.strip():
        st.warning("⚠️ Please describe your grievance before proceeding.")
        st.stop()

    # ---------------- Intake validation ----------------
    is_valid, missing_fields = validate_intake(user_input)

    if not is_valid:
        st.error("❌ Your grievance is missing required information.")
        st.markdown("### Please add the following details:")
        for field in missing_fields:
            st.write(f"- **{field}**")
        st.stop()

    # ---------------- Initialize state ----------------
    state = init_state(user_input)

    # ---------------- Live Progress UI ----------------
    progress_bar = st.progress(0)

    with st.status("🧠 Running multi-agent grievance analysis...", expanded=True) as status:

        # ---- Round 1: Advocate ----
        status.update(label="🟢 Advocate agent analysing grievance...")
        progress_bar.progress(10)
        state["rounds"] = {}
        from agents.advocate import run_advocate
        state["rounds"]["advocate_raw"] = run_advocate(state)
        status.write("✔ Advocate agent completed")

        # ---- Round 1: Opposition ----
        status.update(label="🔴 Opposition agent analysing counter-arguments...")
        progress_bar.progress(30)
        from agents.opposition import run_opposition
        state["rounds"]["opposition_raw"] = run_opposition(state)
        status.write("✔ Opposition agent completed")

        # ---- Round 2: Rebuttals ----
        status.update(label="🔁 Running rebuttal round...")
        progress_bar.progress(55)
        from agents.advocate_rebuttal import run_advocate_rebuttal
        from agents.opposition_rebuttal import run_opposition_rebuttal
        state["rounds"]["advocate_rebuttal_raw"] = run_advocate_rebuttal(state)
        state["rounds"]["opposition_rebuttal_raw"] = run_opposition_rebuttal(state)
        status.write("✔ Rebuttal round completed")

        # ---- Round 3: Legal Validation ----
        status.update(label="⚖️ Legal advisor validating under Indian law...")
        progress_bar.progress(75)
        from agents.legal_advisor import run_legal
        state["legal_validation"] = run_legal(state)
        status.write("✔ Legal validation completed")

        # ---- Round 4: Structuring ----
        status.update(label="📄 Structuring final complaint...")
        progress_bar.progress(90)
        from agents.structurer import run_structurer
        state["final_report"] = run_structurer(state)
        status.write("✔ Final complaint structured")

        progress_bar.progress(100)
        status.update(label="✅ Analysis completed", state="complete")

    # Save result safely
    st.session_state["result"] = run_debate(init_state(user_input))

# -------------------------------------------------
# Display results ONLY if available
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
