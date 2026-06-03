import requests

API_KEY = "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"


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