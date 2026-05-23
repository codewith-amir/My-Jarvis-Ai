# ============================================
# JARVIS - Local AI Assistant
# Main Flask backend file
# ============================================

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import ollama
import json
import os
from datetime import datetime
from modules.weather import get_weather
from modules.reminders import add_reminder, get_reminders, delete_reminder
from modules.news import get_news

load_dotenv()

app = Flask(__name__)

# Store conversation history (in memory - resets on restart)
conversation_history = []

# ============================================
# Helper: Decide which tool/module to use
# based on user's message
# ============================================
def detect_intent(message):
    msg = message.lower()
    if any(word in msg for word in ["weather", "mausam", "temperature", "garmi", "sardi"]):
        return "weather"
    if any(word in msg for word in ["reminder", "remind", "yaad", "alarm", "set reminder"]):
        return "reminder"
    if any(word in msg for word in ["show reminders", "my reminders", "meri reminders", "list reminders"]):
        return "list_reminders"
    if any(word in msg for word in ["news", "khabar", "headlines", "today news"]):
        return "news"
    if any(word in msg for word in ["time", "waqt", "date", "aaj", "today"]):
        return "datetime"
    return "chat"

# ============================================
# Main chat route - handles all messages
# ============================================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    intent = detect_intent(user_message)
    response_text = ""

    # --- Weather ---
    if intent == "weather":
        city = "Lahore"  # Default city - you can change this
        # Try to extract city from message
        words = user_message.split()
        for i, word in enumerate(words):
            if word.lower() in ["in", "of", "mein"] and i + 1 < len(words):
                city = words[i + 1].capitalize()
                break
        weather_data = get_weather(city)
        response_text = weather_data

    # --- Add Reminder ---
    elif intent == "reminder":
        result = add_reminder(user_message)
        response_text = result

    # --- List Reminders ---
    elif intent == "list_reminders":
        reminders = get_reminders()
        response_text = reminders

    # --- News ---
    elif intent == "news":
        response_text = get_news()

    # --- Date/Time ---
    elif intent == "datetime":
        now = datetime.now()
        response_text = f"Abhi ka time: {now.strftime('%I:%M %p')} aur date: {now.strftime('%A, %d %B %Y')} hai."

    # --- Normal AI Chat ---
    else:
        try:
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Keep last 10 messages only (memory limit for your RAM)
            recent_history = conversation_history[-10:]

            # System prompt - makes Jarvis behave like a personal assistant
            system_prompt = """You are Jarvis, a helpful personal AI assistant. 
You are friendly, smart, and concise. 
You can speak in both English and Urdu/Roman Urdu mixed style.
Keep responses short and helpful - not too long.
You are running locally on the user's laptop."""

            # Call Ollama (local AI)
            response = ollama.chat(
                model="mistral",
                messages=[{"role": "system", "content": system_prompt}] + recent_history
            )

            response_text = response["message"]["content"]

            # Save assistant reply to history
            conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

        except Exception as e:
            response_text = f"AI se baat karne mein error aya: {str(e)}. Kya Ollama chal raha hai?"

    return jsonify({"reply": response_text})

# ============================================
# Clear conversation history
# ============================================
@app.route("/clear", methods=["POST"])
def clear_chat():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "cleared"})

# ============================================
# Delete a reminder
# ============================================
@app.route("/delete_reminder", methods=["POST"])
def remove_reminder():
    data = request.get_json()
    index = data.get("index")
    result = delete_reminder(index)
    return jsonify({"status": result})

# ============================================
# Main page
# ============================================
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    print("=" * 40)
    print("  JARVIS is starting up...")
    print("  Open: http://localhost:5000")
    print("=" * 40)
    app.run(debug=True, port=5000)
