import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.environ.get("DATABASE_PATH", "/data/students.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_db():
    with get_db() as db:
        db.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, course TEXT NOT NULL, year INTEGER NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS marks (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, subject TEXT NOT NULL, marks REAL NOT NULL, max_marks REAL NOT NULL, FOREIGN KEY(student_id) REFERENCES students(id))")
        count = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            db.execute("INSERT INTO students (id, name, course, year) VALUES (?, ?, ?, ?)", (1, "Demo Student", "Computer Engineering", 2))

initialize_db()

@app.get("/")
def index():
    return jsonify(service="Student Record & Academic Management API", endpoints=["/api/health", "/api/students", "/api/marks"])

@app.get("/api/health")
def health():
    try:
        with get_db() as db:
            db.execute("SELECT 1").fetchone()
        return jsonify(status="UP", service="student-record-api"), 200
    except sqlite3.Error:
        return jsonify(status="DOWN", service="student-record-api"), 503

@app.get("/api/students")
def list_students():
    with get_db() as db:
        rows = db.execute("SELECT id, name, course, year FROM students ORDER BY id").fetchall()
    return jsonify(students=[dict(row) for row in rows]), 200

@app.post("/api/marks")
def add_marks():
    payload = request.get_json(silent=True) or {}
    required = ("student_id", "subject", "marks", "max_marks")
    missing = [key for key in required if key not in payload]
    if missing:
        return jsonify(error="Missing required fields", fields=missing), 400
    try:
        student_id = int(payload["student_id"])
        subject = str(payload["subject"]).strip()
        marks = float(payload["marks"])
        max_marks = float(payload["max_marks"])
    except (TypeError, ValueError):
        return jsonify(error="student_id must be an integer; marks values must be numeric"), 400
    if not subject or max_marks <= 0 or marks < 0 or marks > max_marks:
        return jsonify(error="Provide a subject and marks between 0 and max_marks"), 400
    with get_db() as db:
        student = db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
        if student is None:
            return jsonify(error="Student not found", student_id=student_id), 404
        cursor = db.execute("INSERT INTO marks (student_id, subject, marks, max_marks) VALUES (?, ?, ?, ?)", (student_id, subject, marks, max_marks))
        record_id = cursor.lastrowid
    return jsonify(message="Marks recorded", id=record_id, student_id=student_id, subject=subject, marks=marks, max_marks=max_marks), 201

@app.get("/api/marks")
def list_marks():
    with get_db() as db:
        rows = db.execute("SELECT m.id, m.student_id, s.name AS student_name, m.subject, m.marks, m.max_marks FROM marks m JOIN students s ON s.id = m.student_id ORDER BY m.id DESC").fetchall()
    return jsonify(marks=[dict(row) for row in rows]), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
