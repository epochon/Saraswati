# MUST be first
import env_loader  

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask, request, jsonify, render_template

from db import init_db, insert_complaint
from orchestrator import run_debate
from agents.extraction_agent import extract_info
from agents.legal_agent import legal_reasoning

app = Flask(__name__)

# Initialize DB once at startup
init_db()


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/agent", methods=["POST"])
def agent():
    # ✅ Accept both JSON and HTML form input
    text = (
        request.json.get("instruction")
        if request.is_json
        else request.form.get("instruction") or request.form.get("text")
    )

    if not text:
        return jsonify({"error": "No complaint text provided"}), 400

    # 1️⃣ Extract structured info
    extracted = extract_info(text)

    # 2️⃣ Validate minimum info
    if not extracted.get("name") or not extracted.get("phone"):
        return jsonify({
            "status": "NEEDS_MORE_INFO",
            "message": "Please provide at least your name and phone number."
        })

    # 3️⃣ Run multi-agent debate
    category, dialogue = run_debate(text)

    # 4️⃣ Legal reasoning (safe, category-based)
    legal = legal_reasoning(category)

    # 5️⃣ Decide status
    status = "SUBMITTED"
    if category == "General":
        status = "DRAFT"

    # 6️⃣ Persist to DB
    insert_complaint({
        "raw_input": text,
        "name": extracted.get("name"),
        "email": extracted.get("email"),
        "phone": extracted.get("phone"),
        "category": category,
        "urgency": "High",
        "legal": legal,
        "dialogue": dialogue,
        "status": status
    })

    # 7️⃣ Return response to frontend
    return jsonify({
        "status": status,
        "category": category,
        "dialogue": dialogue,
        "legal": legal
    })


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
