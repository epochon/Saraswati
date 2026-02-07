import os
import urllib.parse
import streamlit as st
from dotenv import load_dotenv

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

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
from utils.json_utils import extract_json
from utils.render import (
    render_arguments_md,
    render_rebuttals_md,
    render_legal_md
)
from utils.pdf import generate_complaint_pdf

# Agents
from agents.advocate import run_advocate
from agents.opposition import run_opposition
from agents.advocate_rebuttal import run_advocate_rebuttal
from agents.opposition_rebuttal import run_opposition_rebuttal
from agents.legal_advisor import run_legal
from agents.structurer import run_structurer

# -------------------------------------------------
# Streamlit UI config
# -------------------------------------------------
st.set_page_config(
    page_title="AI Grievance System (India)",
    layout="centered"
)

st.title("🇮🇳 Multi-Agent AI Grievance System")

st.markdown(
    """
This system performs a **transparent, multi-round, adversarial AI analysis**
and produces a **submission-ready legal complaint**.

### Analysis Flow
1. 🟢 Advocate Agent  
2. 🔴 Opposition Agent  
3. 🔁 Rebuttal Round  
4. ⚖️ Legal Validation  
5. 📄 Complaint Structuring  
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
# Run analysis
# -------------------------------------------------
if st.button("Analyze & Generate Complaint", type="primary"):

    if not user_input.strip():
        st.warning("⚠️ Please describe your grievance before proceeding.")
        st.stop()

    # -------- Intake validation --------
    is_valid, missing_fields = validate_intake(user_input)
    if not is_valid:
        st.error("❌ Your grievance is missing required information.")
        st.markdown("### Please add the following details:")
        for field in missing_fields:
            st.write(f"- **{field}**")
        st.stop()

    # -------- Initialize state --------
    state = init_state(user_input)
    state["rounds"] = {}

    progress = st.progress(0)

    with st.status("🧠 Running multi-agent grievance analysis...", expanded=True) as status:

        # -------- Round 1: Advocate --------
        status.update(label="🟢 Advocate agent analysing grievance...")
        progress.progress(10)
        state["rounds"]["advocate_raw"] = run_advocate(state)
        status.write("✔ Advocate agent completed")

        # -------- Round 1: Opposition --------
        status.update(label="🔴 Opposition agent analysing counter-arguments...")
        progress.progress(30)
        state["rounds"]["opposition_raw"] = run_opposition(state)
        status.write("✔ Opposition agent completed")

        # -------- Parse Round 1 JSON --------
        status.update(label="🧩 Parsing Round 1 arguments...")
        state["rounds"]["advocate"] = extract_json(
            state["rounds"]["advocate_raw"]
        )
        state["rounds"]["opposition"] = extract_json(
            state["rounds"]["opposition_raw"]
        )
        status.write("✔ Round 1 arguments parsed")

        # -------- Round 2: Rebuttals --------
        status.update(label="🔁 Running rebuttal round...")
        progress.progress(55)
        state["rounds"]["advocate_rebuttal_raw"] = run_advocate_rebuttal(state)
        state["rounds"]["opposition_rebuttal_raw"] = run_opposition_rebuttal(state)

        state["rounds"]["advocate_rebuttal"] = extract_json(
            state["rounds"]["advocate_rebuttal_raw"]
        )
        state["rounds"]["opposition_rebuttal"] = extract_json(
            state["rounds"]["opposition_rebuttal_raw"]
        )
        status.write("✔ Rebuttal round completed")

        # -------- Round 3: Legal --------
        status.update(label="⚖️ Legal advisor validating under Indian law...")
        progress.progress(75)
        state["legal_validation_raw"] = run_legal(state)
        state["legal_validation"] = extract_json(
            state["legal_validation_raw"]
        )
        status.write("✔ Legal validation completed")

        # -------- Round 4: Structurer (ONLY CHANGE HERE) --------
        status.update(label="📄 Structuring final complaint...")
        progress.progress(90)

        structurer_raw = run_structurer(state)
        structured = extract_json(structurer_raw)

        state["short_summary"] = structured["short_summary"]
        state["final_report"] = structured["detailed_report"]

        status.write("✔ Final complaint structured")

        progress.progress(100)
        status.update(label="✅ Analysis completed", state="complete")

    # Save result
    st.session_state["result"] = state

# -------------------------------------------------
# Display results
# -------------------------------------------------
if "result" in st.session_state:
    result = st.session_state["result"]

    st.divider()

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

    
    st.markdown(
        render_legal_md(result["legal_validation"])
    )

    st.subheader("📄 Final Complaint / Report")
    st.markdown(result["final_report"])

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

    # -------------------------------------------------
    # Submit section (ONLY CHANGE HERE)
    # -------------------------------------------------
    st.divider()
    st.subheader("🚀 Submit Complaint")

    st.text_area(
        "Complaint Summary (Copy this)",
        value=result["short_summary"],
        height=250
    )

    st.link_button(
        "🌐 Open Filing Website",
        "http://127.0.0.1:5000/",
        use_container_width=True
    )
