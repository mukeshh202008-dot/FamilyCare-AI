import re
from datetime import datetime, timedelta

from agent.tools import (
    add_family_member,
    get_family_members,
    add_appointment,
    get_appointments,
    add_reminder,
    get_reminders
)


def get_date(text):
    today = datetime.now().date()

    if "today" in text.lower():
        return today.strftime("%Y-%m-%d")

    if "tomorrow" in text.lower():
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", text)

    if match:
        day, month, year = match.groups()

        if len(year) == 2:
            year = "20" + year

        return f"{year}-{int(month):02d}-{int(day):02d}"

    return None


def get_time(text):
    match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text.lower())

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    period = match.group(3)

    if period == "pm" and hour != 12:
        hour += 12

    if period == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"


def process_request(message):
    text = message.lower().strip()

    # ---------------- FAMILY ----------------

    if any(x in text for x in [
        "show family",
        "show my family",
        "family members",
        "who are my family",
        "list family",
        "my family"
    ]):
        result = get_family_members()

        return {
            "response": result,
            "tool_used": "get_family_members"
        }

    if any(x in text for x in [
        "add family",
        "add member",
        "add my mother",
        "add my father",
        "add my brother",
        "add my sister",
        "register my",
        "new family member",
        "add a family member"
    ]):

        age_match = re.search(r"\b(?:age|aged)\s*(\d+)\b", text)
        if not age_match:
            age_match = re.search(r"\b(\d{1,3})\s*years?\b", text)

        if not age_match:
            return {
                "response": "Please provide the person's age. Example: Add my mother, age 45.",
                "tool_used": "waiting_for_information"
            }

        age = int(age_match.group(1))

        relation = None
        relations = [
            "mother", "father", "brother",
            "sister", "son", "daughter",
            "wife", "husband", "grandfather",
            "grandmother", "grandma", "grandpa",
            "uncle", "aunt", "cousin"
        ]

        for r in relations:
            if r in text:
                relation = r
                break

        if not relation:
            return {
                "response": "Please provide the family relation. Example: mother, father, brother or sister.",
                "tool_used": "waiting_for_information"
            }

        names = {
            "mother": "Mother",
            "father": "Father",
            "brother": "Brother",
            "sister": "Sister",
            "son": "Son",
            "daughter": "Daughter",
            "wife": "Wife",
            "husband": "Husband",
            "grandfather": "Grandfather",
            "grandmother": "Grandmother",
            "grandma": "Grandmother",
            "grandpa": "Grandfather",
            "uncle": "Uncle",
            "aunt": "Aunt",
            "cousin": "Cousin"
        }

        name = names[relation]

        blood_group = ""
        allergies = ""
        conditions = ""
        emergency_contact = ""
        notes = ""

        for label, value in [
            ("blood group", re.search(r"blood\s*group\s*([a-z0-9+-]+)", text)),
            ("allergies", re.search(r"allerg(?:y|ies)\s*[:\-]?\s*([a-z ,]+)", text)),
            ("conditions", re.search(r"condit(?:ion|ions)\s*[:\-]?\s*([a-z ,]+)", text)),
            ("emergency contact", re.search(r"emergency\s*contact\s*[:\-]?\s*([a-z ]+)", text)),
        ]:
            if value:
                if label == "blood group":
                    blood_group = value.group(1).strip()
                elif label == "allergies":
                    allergies = value.group(1).strip()
                elif label == "conditions":
                    conditions = value.group(1).strip()
                elif label == "emergency contact":
                    emergency_contact = value.group(1).strip()

        if "needs" in text or "requires" in text or "note" in text:
            note_match = re.search(r"(?:note|notes|needs|requires)\s*[:\-]?\s*([a-z0-9 ,]+)", text)
            if note_match:
                notes = note_match.group(1).strip()

        result = add_family_member(
            name,
            age,
            relation,
            "",
            blood_group=blood_group,
            allergies=allergies,
            conditions=conditions,
            emergency_contact=emergency_contact,
            notes=notes
        )

        return {
            "response": result,
            "tool_used": "add_family_member"
        }

    # ---------------- APPOINTMENTS ----------------

    if any(x in text for x in [
        "show appointments",
        "my appointments",
        "list appointments",
        "appointments"
    ]) and not any(x in text for x in [
        "create",
        "add",
        "book",
        "schedule"
    ]):

        result = get_appointments()

        return {
            "response": result,
            "tool_used": "get_appointments"
        }

    if any(x in text for x in [
        "appointment",
        "book appointment",
        "schedule appointment",
        "create appointment",
        "add appointment",
        "book a",
        "schedule a",
        "appointment for"
    ]):

        date = get_date(text)
        time = get_time(text)

        if not date:
            return {
                "response": "Please provide the appointment date, for example tomorrow or 15/09/2026.",
                "tool_used": "waiting_for_information"
            }

        if not time:
            return {
                "response": "Please provide the appointment time, for example 10 AM.",
                "tool_used": "waiting_for_information"
            }

        member = "Family Member"
        for person in [
            "mother", "father", "brother",
            "sister", "son", "daughter",
            "wife", "husband", "grandmother",
            "grandfather"
        ]:
            if person in text:
                member = person.capitalize()
                break

        appointment_name = "Healthcare appointment"
        if "checkup" in text:
            appointment_name = "Checkup"
        elif "dental" in text:
            appointment_name = "Dental appointment"
        elif "doctor" in text:
            appointment_name = "Doctor consultation"
        elif "therapy" in text:
            appointment_name = "Therapy session"
        elif "vaccin" in text:
            appointment_name = "Vaccination"

        result = add_appointment(
            member,
            appointment_name,
            date,
            time
        )

        return {
            "response": result,
            "tool_used": "add_appointment"
        }

    # ---------------- REMINDERS ----------------

    if any(x in text for x in [
        "show reminders",
        "my reminders",
        "list reminders"
    ]):

        result = get_reminders()

        return {
            "response": result,
            "tool_used": "get_reminders"
        }

    if any(x in text for x in [
        "remind",
        "reminder",
        "set reminder"
    ]):

        date = get_date(text)
        time = get_time(text)

        if not date:
            return {
                "response": "Please provide the reminder date, for example tomorrow or 15/09/2026.",
                "tool_used": "waiting_for_information"
            }

        if not time:
            return {
                "response": "Please provide the reminder time, for example 10 AM.",
                "tool_used": "waiting_for_information"
            }

        member = "Family Member"

        for person in [
            "mother", "father", "brother",
            "sister", "son", "daughter"
        ]:
            if person in text:
                member = person.capitalize()
                break

        reminder = "Health reminder"

        if "checkup" in text:
            reminder = "Checkup reminder"
        elif "doctor" in text:
            reminder = "Doctor reminder"
        elif "appointment" in text:
            reminder = "Appointment reminder"

        result = add_reminder(
            member,
            reminder,
            date,
            time
        )

        return {
            "response": result,
            "tool_used": "add_reminder"
        }

    # ---------------- GENERAL ----------------

    if text in ["hello", "hi", "hey", "hello familycare", "hi familycare"]:
        return {
            "response": (
                "Hello! 👋 I am FamilyCare AI.\n\n"
                "I can help you manage:\n"
                "• Family members\n"
                "• Healthcare appointments\n"
                "• Health reminders\n\n"
                "Try: 'show my family members'"
            ),
            "tool_used": "none"
        }

    return {
        "response": (
            "I can help with family members, appointments and reminders.\n\n"
            "Try:\n"
            "• Show my family members\n"
            "• Add my mother, age 45\n"
            "• Show my appointments\n"
            "• Book an appointment for my father tomorrow at 10 AM\n"
            "• Show my reminders"
        ),
        "tool_used": "none"
    }