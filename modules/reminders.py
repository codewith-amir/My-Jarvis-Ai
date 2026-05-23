# ============================================
# Reminders Module
# Simple file-based reminders (no database needed)
# Reminders save to reminders.json file
# ============================================

import json
import os
from datetime import datetime

REMINDERS_FILE = "reminders.json"

def load_reminders():
    """Load reminders from JSON file"""
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_reminders(reminders):
    """Save reminders to JSON file"""
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

def add_reminder(message):
    """Extract reminder text and save it"""
    # Remove common trigger words to get the actual reminder
    cleaned = message.lower()
    for word in ["remind me to", "reminder", "set reminder", "yaad dilao", "remind me", "add reminder"]:
        cleaned = cleaned.replace(word, "").strip()

    if not cleaned:
        return "Kya yaad dilana hai? Likho: 'Remind me to drink water at 5pm'"

    reminders = load_reminders()
    reminder = {
        "id": len(reminders),
        "text": cleaned.capitalize(),
        "created_at": datetime.now().strftime("%d/%m/%Y %I:%M %p")
    }
    reminders.append(reminder)
    save_reminders(reminders)

    return f"✅ Reminder save ho gaya: '{cleaned.capitalize()}'"

def get_reminders():
    """Return all reminders as formatted text"""
    reminders = load_reminders()

    if not reminders:
        return "Abhi koi reminders nahi hain. Kaho: 'Remind me to ...'"

    result = "📋 Tumhari reminders:\n"
    for i, r in enumerate(reminders):
        result += f"{i + 1}. {r['text']} (added: {r['created_at']})\n"
    result += "\nDelete karne ke liye number wala button dabao."
    return result

def delete_reminder(index):
    """Delete a reminder by index"""
    reminders = load_reminders()
    if index is not None and 0 <= index < len(reminders):
        removed = reminders.pop(index)
        save_reminders(reminders)
        return f"Reminder delete ho gaya: '{removed['text']}'"
    return "Reminder nahi mila."
