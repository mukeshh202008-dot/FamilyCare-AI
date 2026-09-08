from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3

from agent.agent import process_request

app = Flask(__name__)

DB = "database.db"


def get_db():
    return sqlite3.connect(DB)


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS family (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            relation TEXT,
            phone TEXT,
            blood_group TEXT DEFAULT '',
            allergies TEXT DEFAULT '',
            conditions TEXT DEFAULT '',
            emergency_contact TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member TEXT NOT NULL,
            appointment TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT DEFAULT ''
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member TEXT NOT NULL,
            reminder TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            notes TEXT DEFAULT ''
        )
    """)

    for table, columns in {
        "family": [
            "blood_group",
            "allergies",
            "conditions",
            "emergency_contact",
            "notes",
            "created_at",
        ],
        "appointments": [
            "status",
            "notes",
        ],
        "reminders": [
            "status",
            "notes",
        ],
    }.items():
        existing = conn.execute(f"PRAGMA table_info({table})").fetchall()
        existing_columns = {row[1] for row in existing}

        for column in columns:
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT DEFAULT ''")

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    conn = get_db()
    conn.row_factory = sqlite3.Row

    family = conn.execute(
        "SELECT * FROM family ORDER BY id DESC"
    ).fetchall()

    appointments = conn.execute(
        "SELECT * FROM appointments ORDER BY date, time"
    ).fetchall()

    reminders = conn.execute(
        "SELECT * FROM reminders ORDER BY date, time"
    ).fetchall()

    total_members = len(family)
    upcoming_appointments = len([
        item for item in appointments
        if item["date"] >= __import__('datetime').date.today().isoformat()
    ])
    active_reminders = len([
        item for item in reminders
        if item["date"] >= __import__('datetime').date.today().isoformat()
    ])

    conn.close()

    return render_template(
        "dashboard.html",
        family=family,
        appointments=appointments,
        reminders=reminders,
        total_members=total_members,
        upcoming_appointments=upcoming_appointments,
        active_reminders=active_reminders
    )


@app.route("/family", methods=["GET", "POST"])
def family_page():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age")
        relation = request.form.get("relation", "").strip()
        phone = request.form.get("phone", "").strip()
        blood_group = request.form.get("blood_group", "").strip()
        allergies = request.form.get("allergies", "").strip()
        conditions = request.form.get("conditions", "").strip()
        emergency_contact = request.form.get("emergency_contact", "").strip()
        notes = request.form.get("notes", "").strip()

        if name and age and relation:
            conn = get_db()
            conn.execute(
                """
                INSERT INTO family
                (name, age, relation, phone, blood_group, allergies, conditions, emergency_contact, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    int(age),
                    relation,
                    phone,
                    blood_group,
                    allergies,
                    conditions,
                    emergency_contact,
                    notes,
                )
            )
            conn.commit()
            conn.close()

        return redirect(url_for("family_page"))

    conn = get_db()
    conn.row_factory = sqlite3.Row

    members = conn.execute(
        "SELECT * FROM family ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "family.html",
        members=members
    )


@app.route("/appointments", methods=["GET", "POST"])
def appointments_page():

    if request.method == "POST":
        member = request.form.get("member", "").strip()
        appointment = request.form.get("appointment", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        status = request.form.get("status", "Scheduled").strip()
        notes = request.form.get("notes", "").strip()

        if member and appointment and date and time:
            conn = get_db()
            conn.execute(
                """
                INSERT INTO appointments
                (member, appointment, date, time, status, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (member, appointment, date, time, status, notes)
            )
            conn.commit()
            conn.close()

        return redirect(url_for("appointments_page"))

    conn = get_db()
    conn.row_factory = sqlite3.Row

    members = conn.execute(
        "SELECT id, name FROM family ORDER BY name"
    ).fetchall()
    appointments = conn.execute(
        "SELECT * FROM appointments ORDER BY date, time"
    ).fetchall()

    conn.close()

    return render_template(
        "appointments.html",
        appointments=appointments,
        members=members
    )


@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route("/api/assistant", methods=["POST"])
def assistant_api():

    data = request.json
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "response": "Please enter a message.",
            "tool_used": "none"
        })

    try:
        result = process_request(message)
        return jsonify(result)

    except Exception as e:
        print("Agent Error:", e)

        return jsonify({
            "response": "Sorry, something went wrong.",
            "tool_used": "error"
        }), 500


if __name__ == "__main__":
    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )