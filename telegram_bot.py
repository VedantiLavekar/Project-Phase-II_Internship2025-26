from flask import Flask, request
import requests
import json
import os

from ai.summarizer import summarize_text
from ai.reply_generator import generate_reply

# ================= CONFIG =================

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

STORE_FILE = "telegram_messages.json"

USERS_FILE = "telegram_users.json"

# ==========================================

app = Flask(__name__)

# ---------- CREATE FILES ----------

if not os.path.exists(STORE_FILE):

    with open(STORE_FILE, "w") as f:

        json.dump([], f)

if not os.path.exists(USERS_FILE):

    with open(USERS_FILE, "w") as f:

        json.dump({}, f)

# ---------- SAVE MESSAGE ----------

def save_message(data):

    with open(STORE_FILE, "r") as f:

        messages = json.load(f)

    messages.append(data)

    with open(STORE_FILE, "w") as f:

        json.dump(messages, f, indent=2)

# ---------- SAVE USER ----------

def save_user(name, chat_id):

    with open(USERS_FILE, "r") as f:

        users = json.load(f)

    users[name.lower()] = chat_id

    with open(USERS_FILE, "w") as f:

        json.dump(users, f, indent=2)

# ---------- SEND TELEGRAM ----------

def send_telegram_message(chat_id, message):

    url = f"{BASE_URL}/sendMessage"

    payload = {

        "chat_id": chat_id,

        "text": message

    }

    requests.post(url, json=payload)

# ---------- WEBHOOK ----------

@app.route("/", methods=["POST"])
def webhook():

    data = request.json

    try:

        message = data["message"]

        text = message.get("text", "")

        user = message["from"].get(

            "first_name",

            "unknown"

        )

        chat_id = message["chat"]["id"]

        print("\n===================")

        print("NEW TELEGRAM MESSAGE")

        print("USER:", user)

        print("MESSAGE:", text)

        print("===================\n")

        # SAVE USER

        save_user(

            user,

            chat_id

        )

        # AI SUMMARY

        summary = summarize_text(text)

        # AI REPLY

        reply = generate_reply(text)

        # SAVE MESSAGE

        save_message({

            "user": user,

            "chat_id": chat_id,

            "message": text,

            "summary": summary,

            "reply": reply

        })

        response = (

            f"📌 Summary:\n{summary}\n\n"

            f"🤖 Suggested Reply:\n{reply}"

        )

        send_telegram_message(

            chat_id,

            response

        )

    except Exception as e:

        print("ERROR:", e)

    return "OK"

# ---------- RUN ----------

if __name__ == "__main__":

    print(
        "✅ Telegram Flask Bot Running"
    )

    app.run(port=6000)
