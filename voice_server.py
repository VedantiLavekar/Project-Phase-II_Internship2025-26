# =========================
# VOICE SERVER
# =========================

from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
import requests
import pyttsx3
import webbrowser
import subprocess
import time
import threading
import os
import sys
import re


# =========================
# AI CONFIG
# =========================

OPENROUTER_API_KEY = "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"

# =========================
# TELEGRAM CONFIG
# =========================
BOT_TOKEN = "8386672558:AAEePUYseuV7SftQkw50VYhtQY2gsH_f5Ks"
CHAT_ID = "2044709883"

# =========================
# GLOBAL SPEECH ENGINE
# =========================

# =========================
# SPEAK FUNCTION
# =========================
def speak(text):

    print(
        "ASSISTANT:",
        text
    )

    try:

        temp_engine = pyttsx3.init()

        temp_engine.setProperty(
            'rate',
            185
        )

        temp_engine.setProperty(
            'volume',
            1.0
        )

        voices = temp_engine.getProperty(
            'voices'
        )

        temp_engine.setProperty(
            'voice',
            voices[0].id
        )

        temp_engine.say(text)

        temp_engine.runAndWait()

        temp_engine.stop()

    except Exception as e:

        print(
            "Speech Error:",
            e
        )
# =========================
# TELEGRAM
# =========================

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {

        "chat_id": CHAT_ID,
        "text": message

    }

    try:

        requests.post(url, json=payload)
        return True

    except Exception as e:

        print("TELEGRAM ERROR:", e)
        return False

# =========================
# RESOURCE PATH
# =========================

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# =========================
# LOAD MODEL
# =========================

MODEL_PATH = resource_path(
    "vosk-model-en-us-0.22"
)

print("Loading Vosk model...")
print("MODEL PATH:", MODEL_PATH)

model = Model(MODEL_PATH)

recognizer = KaldiRecognizer(
    model,
    16000
)

# =========================
# AUDIO QUEUE
# =========================

q = queue.Queue()

# =========================
# STATES
# =========================

is_active = False
waiting_for_telegram = False
waiting_for_reply = False

reply_email_number = 1

last_command = ""
last_command_time = 0

# =========================
# TEST FLASK
# =========================

print("Testing Flask Connection...")

try:

    test = requests.get(
        "http://127.0.0.1:5000"
    )

    print(
        "Flask Connected:",
        test.status_code
    )

except Exception as e:

    print(
        "Flask NOT Running:",
        e
    )

# =========================
# READY
# =========================

print(sd.query_devices())

print("🎤 Voice Assistant Ready...")

speak(
    "Say hello to activate assistant"
)

# =========================
# AUDIO CALLBACK
# =========================

def callback(indata, frames, time_info, status):

    if status:
        print(status)

    q.put(bytes(indata))

# =========================
# SEND DASHBOARD COMMAND
# =========================

def send_dashboard_command(command):

    try:

        print(
            "Sending command to dashboard:",
            command
        )

        response = requests.post(

            "http://127.0.0.1:5000/update-command",

            json={
                "command": command
            },

            timeout=15

        )

        print(
            "Dashboard Response:",
            response.status_code
        )

    except Exception as e:

        print(
            "Dashboard Error:",
            e
        )
        return
        
        
        
# =========================
# AI EMAIL SUMMARY
# =========================

def generate_email_summary(email_text):

    try:

        prompt = f"""
        Read this email carefully and generate
        a professional summary in 3 to 4 sentences.

        Email:
        {email_text}
        """

        headers = {

            "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
            "application/json"

        }

        data = {

            "model":
            "openai/gpt-3.5-turbo",

            "messages": [

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        }

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers=headers,
            json=data

        )

        result = response.json()

        summary = result["choices"][0]["message"]["content"]

        return summary

    except Exception as e:

        print("SUMMARY ERROR:", e)

        return "Unable to generate summary."


# =========================
# AI SUGGESTED REPLIES
# =========================

def generate_ai_replies(email_text):

    try:

        prompt = f"""
        Read this email carefully and generate
        3 professional short reply suggestions.

        Keep replies natural and meaningful.

        Email:
        {email_text}
        """

        headers = {

            "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
            "application/json"

        }

        data = {

            "model":
            "openai/gpt-3.5-turbo",

            "messages": [

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        }

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers=headers,
            json=data

        )

        result = response.json()

        replies = result["choices"][0]["message"]["content"]

        return replies

    except Exception as e:

        print("REPLY ERROR:", e)

        return "Unable to generate replies."

# =========================
# OPEN GOOGLE LOGIN
# =========================

def open_google_login():

    try:

        url = "http://127.0.0.1:5000/login/google"

        subprocess.Popen([

            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

            "--profile-directory=Default",

            "--start-maximized",

            url

        ])

    except Exception as e:

        print("EDGE ERROR:", e)

        webbrowser.open(url)

# =========================
# DUPLICATE FILTER
# =========================

def is_duplicate(command):

    global last_command
    global last_command_time

    current_time = time.time()

    if (

        command == last_command

        and

        current_time - last_command_time < 2

    ):

        return True

    last_command = command
    last_command_time = current_time

    return False









def normalize_command(text):

    text = text.lower()

    replacements = {

        # SUMMARY
        "smary": "summary",
        "summery": "summary",
        "samary": "summary",
        "samadi": "summary",
        "somebody": "summary",

        # READ
        "raid": "read",
        "reed": "read",

        # LOGIN
        "login which google": "login with google",

        # TELEGRAM
        "daily gram": "telegram",
        "jimmy gram": "telegram",
        "barely gram": "telegram",
        
        # SENT FIXES
        "open sent": "sent",
        "on open sent": "sent",
        "one sent": "sent",
        "sand": "sent",
        "saint": "sent",
        "film bad guys": "sent",
        
        
         # DELETE FIXES
        "email lead": "delete",
        "email delete": "delete",
        "deletee": "delete",
        "deleet": "delete",
        "believe email": "delete",
        "email": "delete",
        "emails": "delete",
        "email email": "delete",
        "man email": "delete",
        "dim he may know": "delete",

        # EMAIL
        "he made": "email",
        
        # TRASH FIXES
        "rash": "trash",
        "crash": "trash",
        "brash": "trash",
        "open brash": "trash",
        "blush": "trash",
        "mash": "trash",
        "mush": "trash",
        "trashh": "trash",
        
        
        # SUMMARY COMMON FIXES

        "summary 1": "summary one",
        "summary 2": "summary two",
        "summary 3": "summary three",
        "summary 4": "summary four",
        "summary 5": "summary five",
        "summary 6": "summary six",
        "summary 7": "summary seven",
        "summary 8": "summary eight",
        "summary 9": "summary nine",
        "summary 10": "summary ten",

        "some mighty one": "summary one",
        "some mighty two": "summary two",
        "some mighty three": "summary three",
        "some mighty four": "summary four",
        "some mighty five": "summary five",

        "so mighty one": "summary one",
        "so mighty two": "summary two",
        "so mighty three": "summary three",
        "so mighty four": "summary four",
        "so mighty five": "summary five",

        "summery one": "summary one",
        "summery two": "summary two",
        "summery three": "summary three",
        "summery four": "summary four",
        "summery five": "summary five",
        
        
        
        # SUMMARY
        "smary": "summary",
        "summery": "summary",
        
        
        # AI REPLY
        "suggested reply": "suggest reply",
        "ai replies": "suggest reply",
        "reply suggestion": "suggest reply",
        
        
        
        # NUMBER FIXES

        "won": "one",
        "to": "two",
        "tree": "three",
        "for": "four",
        "fife": "five",
        "sicks": "six",
        "heaven": "seven",
        "ate": "eight",
        "mine": "nine",
    
    }
    
    
    
    
        # SEARCH FIXES

    text = text.replace(
        "sarge",
        "search"
    )

    text = text.replace(
        "serge",
        "search"
    )

    text = text.replace(
        "site",
        "search"
    )

    text = text.replace(
        "searching",
        "search"
    )

    text = text.replace(
        "accent",
        "analyst"
    )

    text = text.replace(
        "and at least",
        "analyst"
    )

    for wrong, correct in replacements.items():

        text = text.replace(
            wrong,
            correct
        )

    return text
# =========================
# EXTRACT EMAIL NUMBER
# =========================

def extract_email_number(text):

    text = text.lower()

    number_map = {

        "one": 1,
        "first": 1,

        "two": 2,
        "second": 2,

        "three": 3,
        "third": 3,

        "four": 4,
        "fourth": 4,

        "five": 5,
        "fifth": 5,

        "six": 6,
        "sixth": 6,

        "seven": 7,
        "seventh": 7,

        "eight": 8,
        "eighth": 8,

        "nine": 9,
        "ninth": 9,

        "ten": 10,
        "tenth": 10,

        "eleven": 11,
        "eleventh": 11,

        "twelve": 12,
        "twelfth": 12,

        "thirteen": 13,
        "thirteenth": 13,

        "fourteen": 14,
        "fourteenth": 14,

        "fifteen": 15,
        "fifteenth": 15,

        "sixteen": 16,
        "sixteenth": 16,

        "seventeen": 17,
        "seventeenth": 17,

        "eighteen": 18,
        "eighteenth": 18,

        "nineteen": 19,
        "nineteenth": 19,

        "twenty": 20,
        "twentieth": 20

    }

    for word, num in number_map.items():

        if word in text:
            return num

    match = re.search(r"\d+", text)

    if match:

        number = int(match.group())

        if 1 <= number <= 20:
            return number

    return None
# =========================
# MICROPHONE STREAM
# =========================

with sd.RawInputStream(

    samplerate=16000,
    blocksize=2000,
    dtype="int16",
    channels=1,
    callback=callback

):

    print("🎤 Listening continuously...")

    while True:

        data = q.get()

        if recognizer.AcceptWaveform(data):

            result = json.loads(
                recognizer.Result()
            )

            text = result.get(
                "text",
                ""
            ).lower().strip()

            if not text:
                continue

            # =========================
            # REMOVE NOISE
            # =========================

            noise_words = [

                "uh",
                "um",
                "please",
                "assistant",
                "hmm",
                "ah",
                "the"

            ]

            for w in noise_words:
                text = text.replace(w, "")

            text = " ".join(text.split())
            text = normalize_command(text)

            if len(text) < 2:
                continue

            if len(text.split()) > 10:
                continue

            # =========================
            # FIX COMMON WORDS
            # =========================

            text = text.replace(
                "log in",
                "login"
            )

            text = text.replace(
                "goggle",
                "google"
            )

            text = text.replace(
                "google log in",
                "login with google"
            )

            # =========================
            # DUPLICATE FILTER
            # =========================

            if is_duplicate(text):
                continue

            print("\n===================")
            print("FINAL COMMAND:", text)
            print("===================\n")

            # =========================
            # WAKE WORD
            # =========================

            if (

                text.strip() == "hello"

                or

                text.strip() == "hi"

                or

                text.strip() == "hey"

                or

                text.strip() == "wake up"

            ):

                is_active = True

                speak(
                    "I am listening. "
                    "You can say commands like login, "
                    "register or login with google"
                )
                time.sleep(4)

                continue

            # =========================
            # IGNORE IF NOT ACTIVE
            # =========================

            if not is_active:
                continue

            # =========================
            # STOP ASSISTANT
            # =========================

            if "stop" in text:

                speak(
                    "Assistant stopped"
                )

                is_active = False

                continue

            # =========================
            # LOGIN GOOGLE
            # =========================

            if text.strip() == "login with google":

                speak(
                    "Opening Google login and dashboard"
                )
                time.sleep(3)
                threading.Thread(

                    target=open_google_login,

                    daemon=True

                ).start()

                

                speak(
                    "Dashboard opened. "
                    "You can now say commands like inbox, sent, "
                    "read email, send email or telegram"
                )
                time.sleep(5)

                continue

            # =========================
            # EMAIL NUMBER
            # =========================

            email_number = extract_email_number(text)

            # =========================
            # INBOX
            # =========================

            if "inbox" in text:

                speak(
                    "Opening inbox"
                )
                time.sleep(2)

                send_dashboard_command(
                    "inbox"
                )

                continue

            # =========================
            # SENT
            # =========================

            if "sent" in text:

                speak(
                    "Opening sent mails"
                )
                time.sleep(2)

                send_dashboard_command(
                    "sent"
                )

                continue

            # =========================
            # TRASH
            # =========================

            if "trash" in text:

                speak(
                    "Opening trash"
                )
                time.sleep(2)

                send_dashboard_command(
                    "trash"
                )

                continue
            
            
            
            
            
            # =========================
            # COMPOSE EMAIL
            # =========================

            if (

                "send email" in text

                or

                "compose email" in text

                or

                "compose" in text

                or

                "combo" in text

                or

                "combos" in text

                or

                "come boards" in text

            ):

                speak(
                    "Opening voice compose page"
                )
                time.sleep(2)

                webbrowser.open(
                    "http://127.0.0.1:5000/voice-mail"
                )

                continue
            # =========================
            # DELETE EMAIL
            # =========================

            if "delete" in text:

                if "latest" in text:

                    speak(
                        "Deleting latest email"
                    )

                    send_dashboard_command(
                        "delete latest email"
                    )

                    continue

                if email_number is None:

                    speak(
                        "Please say email number clearly"
                    )

                    continue

                speak(
                    f"Deleting email {email_number}"
                )

                send_dashboard_command(
                    f"delete {email_number}"
                )

                continue
            
            
            
            # =========================
            # READ EMAIL
            # =========================

            if (
                "read" in text
                or
                "reed" in text
                or
                "raid" in text
            ):

                if email_number is None:

                    speak(
                        "Please say email number clearly"
                    )

                    continue

                speak(
                    f"Reading email {email_number}"
                )

                send_dashboard_command(
                    f"read {email_number}"
                )

                continue
            
            
            
            # =========================
            # EMAIL SUMMARY
            # =========================

            if "summary" in text:

                if email_number is None:

                    speak(
                        "Please say email number clearly"
                    )

                    continue

                speak(
                    f"Generating summary for email {email_number}"
                )

                send_dashboard_command(
                    f"summary {email_number}"
                )

                continue
            
            
        
        
            # =========================
            # AI REPLY SUGGESTIONS
            # =========================

            if "suggest reply" in text:

                if email_number is None:

                    speak(
                        "Please say email number clearly"
                    )

                    continue

                speak(
                    f"Generating AI replies for email {email_number}"
                )

                send_dashboard_command(
                    f"ai reply {email_number}"
                )

                continue

            # =========================
            # REPLY EMAIL
            # =========================

            if "reply" in text:

                if email_number is None:

                    speak(
                        "Please say email number clearly"
                    )

                    continue

                waiting_for_reply = True
                reply_email_number = email_number

                speak(
                    f"What should I reply to email {email_number}"
                )

                continue

            # =========================
            # WAITING FOR REPLY
            # =========================

            if waiting_for_reply:

                waiting_for_reply = False

                send_dashboard_command(
                    f"send reply {reply_email_number} {text}"
                )

                speak(
                    "Reply sent successfully"
                )

                continue
            
            
            
            
            
            
            
            # =========================
            # SEARCH EMAILS
            # =========================

            if "search" in text:

                query = text.replace(
                    "search",
                    ""
                ).strip()

                if not query:

                    speak(
                        "Please say what to search"
                    )

                    continue

                speak(
                    f"Searching emails for {query}"
                )
                time.sleep(2)

                send_dashboard_command(
                    f"search {query}"
                )

                continue        
          

            # =========================
            # TELEGRAM
            # =========================

            if "telegram" in text:

                speak(
                    "Opening telegram message page"
                )
                time.sleep(2)

                webbrowser.open(
                    "http://127.0.0.1:5000/telegram"
                )

                continue

            # =========================
            # LOGOUT
            # =========================

            if "logout" in text:

                speak(
                    "Logging out"
                )

                send_dashboard_command(
                    "logout"
                )

                continue
            
            
            
            
    

            # =========================
            # UNKNOWN COMMAND
            # =========================

            print(
                "IGNORED UNKNOWN COMMAND:",
                text
            )