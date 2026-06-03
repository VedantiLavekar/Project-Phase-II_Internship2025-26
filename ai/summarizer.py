import requests
import re

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"


def summarize_text(text):

    if not text or len(text.strip()) == 0:

        return "No content available."

    try:

        # =========================
        # CLEAN EMAIL TEXT
        # =========================

        text = re.sub(
            r'\s+',
            ' ',
            text
        )

        text = text.strip()

        # LIMIT LONG EMAILS
        text = text[:3000]

        # =========================
        # AI SUMMARY REQUEST
        # =========================

        response = requests.post(

    "https://openrouter.ai/api/v1/chat/completions",

    headers={

        "Authorization": f"Bearer {API_KEY}",

        "Content-Type": "application/json"

    },

            json={

                "model": "openai/gpt-3.5-turbo",

                "messages": [

                    {

                        "role": "system",

                        "content": """

You are an intelligent email assistant.

Generate short professional summaries of emails.

Rules:
- Keep summary concise
- Maximum 3 short sentences
- Focus only on important information
- Mention action required if present
- Ignore greetings, signatures, HTML, CSS, footer text
- Make summary human readable

"""

                    },

                    {

                        "role": "user",

                        "content": f"""

Read this email carefully and explain its actual meaning in 2 short sentences.

EMAIL:
{text}

"""

                    }

                ],

                "temperature": 0.3,

                "max_tokens": 120

            }

        )
        print("\n====================")
        print("EMAIL SENT TO AI:")
        print(text)
        print("====================\n")

        data = response.json()
        
        print("\n====================")
        print("OPENROUTER RESPONSE:")
        print(data)
        print("====================\n")

        # =========================
        # SAFE RESPONSE
        # =========================
        if "choices" not in data:

            print("\nOPENROUTER ERROR RESPONSE:\n")
            print(data)
            print("\n========================\n")

            return "Unable to generate summary."

        summary = data["choices"][0]["message"]["content"]

        summary = summary.strip()

        # LIMIT OUTPUT SIZE
        summary = summary[:400]

        print("\nFINAL SUMMARY:\n")
        print(summary)
        print("\n====================\n")

        return summary

    except Exception as e:

        print("Summary Error:", e)

        return "Unable to generate summary."
