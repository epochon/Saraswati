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
    complaint_text = data["complaint"]
    category = categorize_complaint(complaint_text)

    db.collection("complaints").add({
        "text": complaint_text,
        "category": category,
        "status": "OPEN"
    })

    return jsonify({"category": category})


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
    complaints_ref = db.collection("complaints").stream()

    complaints = []
    for doc in complaints_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        complaints.append(data)

    return render_template("dashboard.html", complaints=complaints)


if __name__ == "__main__":
    print("🔥 Firestore connected successfully")
    app.run(debug=True)

