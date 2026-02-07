import sqlite3
import json

def init_db():
    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_input TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        category TEXT,
        urgency TEXT,
        legal TEXT,
        dialogue TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_complaint(data):
    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO complaints
    (raw_input, name, email, phone, category, urgency, legal, dialogue, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["raw_input"],
        data["name"],
        data["email"],
        data["phone"],
        data["category"],
        data["urgency"],
        data["legal"],
        json.dumps(data["dialogue"]),
        "SUBMITTED"
    ))
    conn.commit()
    conn.close()
    

def save_complaint(name, phone, email, complaint, category, status):
    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO complaints (name, phone, email, complaint, category, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, email, complaint, category, status))

    conn.commit()
    conn.close()

