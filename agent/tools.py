import sqlite3

DB = "database.db"


def ensure_schema():
    conn = sqlite3.connect(DB)

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
        "family": ["blood_group", "allergies", "conditions", "emergency_contact", "notes", "created_at"],
        "appointments": ["status", "notes"],
        "reminders": ["status", "notes"],
    }.items():
        existing_columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for column in columns:
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT DEFAULT ''")

    conn.commit()
    conn.close()


def add_family_member(
    name,
    age,
    relation,
    phone="",
    blood_group="",
    allergies="",
    conditions="",
    emergency_contact="",
    notes=""
):
    ensure_schema()
    conn = sqlite3.connect(DB)

    conn.execute("""
        INSERT INTO family(
            name, age, relation, phone, blood_group,
            allergies, conditions, emergency_contact, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        relation,
        phone,
        blood_group,
        allergies,
        conditions,
        emergency_contact,
        notes,
    ))

    conn.commit()
    conn.close()

    return f"{name} was successfully added as a family member."


def get_family_members():
    ensure_schema()
    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT name, age, relation, phone, blood_group, allergies, conditions, emergency_contact, notes
        FROM family
    """).fetchall()

    conn.close()

    if not rows:
        return "There are no family members yet."

    result = []

    for row in rows:
        name, age, relation, phone, blood_group, allergies, conditions, emergency_contact, notes = row
        extra = []
        if blood_group:
            extra.append(f"blood group {blood_group}")
        if allergies:
            extra.append(f"allergies: {allergies}")
        if conditions:
            extra.append(f"conditions: {conditions}")
        if emergency_contact:
            extra.append(f"emergency: {emergency_contact}")
        summary = ", ".join(extra) if extra else "No additional details"
        result.append(f"{name}, age {age}, {relation}. {summary}")

    return "\n".join(result)


def add_appointment(member, appointment, date, time, status="Scheduled", notes=""):
    ensure_schema()
    conn = sqlite3.connect(DB)

    conn.execute("""
        INSERT INTO appointments
        (member, appointment, date, time, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (member, appointment, date, time, status, notes))

    conn.commit()
    conn.close()

    return (
        f"Appointment successfully created for {member} "
        f"on {date} at {time}."
    )


def get_appointments():
    ensure_schema()
    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT member, appointment, date, time, status, notes
        FROM appointments
        ORDER BY date, time
    """).fetchall()

    conn.close()

    if not rows:
        return "There are no appointments."

    result = []

    for member, appointment, date, time, status, notes in rows:
        note_text = f" - {notes}" if notes else ""
        result.append(
            f"{member}: {appointment} on {date} at {time} [{status}]{note_text}"
        )

    return "\n".join(result)


def add_reminder(member, reminder, date, time, status="Pending", notes=""):
    ensure_schema()
    conn = sqlite3.connect(DB)

    conn.execute("""
        INSERT INTO reminders
        (member, reminder, date, time, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (member, reminder, date, time, status, notes))

    conn.commit()
    conn.close()

    return (
        f"Reminder successfully created for {member} "
        f"on {date} at {time}."
    )


def get_reminders():
    ensure_schema()
    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT member, reminder, date, time, status, notes
        FROM reminders
        ORDER BY date, time
    """).fetchall()

    conn.close()

    if not rows:
        return "There are no reminders."

    result = []

    for member, reminder, date, time, status, notes in rows:
        note_text = f" - {notes}" if notes else ""
        result.append(
            f"{member}: {reminder} on {date} at {time} [{status}]{note_text}"
        )

    return "\n".join(result)
