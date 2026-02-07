from flask import Flask, render_template, request, jsonify
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# ---- Firebase init (safe path) ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "credentials.json")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()


# ---- Complaint Categorization Logic ----
def categorize_complaint(text):
    text = text.lower()

    if "fire" in text or "burn" in text:
        return "fire"
    elif "water" in text or "leak" in text or "pipe" in text:
        return "water"
    elif "electricity" in text or "power" in text or "current" in text:
        return "electricity"
    elif "police" in text or "court" in text or "legal" in text:
        return "legal"
    else:
        return "other"


# ---- Home (Complaint Form) ----
@app.route("/")
def home():
    return render_template("complaint_form.html")


# ---- Submit Complaint (NEW) ----
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    db.collection("complaints").add({
        "consensus_data": {
            "name": data.get("name", "").strip(),
            "complaint": data.get("complaint", ""),
            "category": categorize_complaint(data.get("complaint", "")),
            "location": "Unknown"
        },
        "phone": "9846960356",
        "metadata": {
            "protocol": "manual-ui"
        }
    })

    return jsonify({"status": "ok"})



# ---- Dashboard Stats (NEW) ----
@app.route("/stats")
def stats():
    counts = {
        "fire": 0,
        "water": 0,
        "electricity": 0,
        "legal": 0,
        "other": 0
    }

    complaints = db.collection("complaints").stream()

    for doc in complaints:
        data = doc.to_dict()
        category = data.get("category", "other")
        if category in counts:
            counts[category] += 1

    return jsonify(counts)


# ---- Dashboard Page ----
@app.route("/dashboard")
def dashboard():
    docs = db.collection("complaints").stream()
    complaints = []

    for doc in docs:
        data = doc.to_dict()

        # Case 1: Agent / Consensus data
        if "consensus_data" in data:
            cd = data.get("consensus_data", {})
            complaints.append({
                "name": cd.get("name", "—"),
                "complaint": cd.get("complaint", "—"),
                "category": cd.get("category", "—"),
                "location": cd.get("location", "—"),
                "phone": data.get("phone", "—"),
                "status": "OPEN"
            })

        # Case 2: Old / Simple UI submissions
        else:
            complaints.append({
                "name": "—",
                "complaint": data.get("text", "—"),
                "category": data.get("category", "—"),
                "location": "—",
                "phone": "—",
                "status": data.get("status", "OPEN")
            })

    return render_template("dashboard.html", complaints=complaints)


@app.route("/debug-all")
def debug_all():
    docs = db.collection("complaints").stream()
    out = []
    for doc in docs:
        out.append(doc.to_dict())
    return jsonify(out)


if __name__ == "__main__":
    print("🔥 Firestore connected successfully")
    app.run(debug=True)

