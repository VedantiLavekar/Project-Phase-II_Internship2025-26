import requests

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"


def generate_reply(text):

    if not text:
        return "No content available."

    try:
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
                        "role": "user",
                        "content": f"Generate 3 short professional email replies:\n{text[:2000]}"
                    }
                ]
            }
        )

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("Reply Error:", e)
        return "Unable to generate replies."
