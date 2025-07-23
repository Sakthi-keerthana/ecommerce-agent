import os
import requests

def translate_question_to_sql(question: str) -> dict:
    prompt = f"""..."""  # Use the prompt above

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyDBfdZiDhLkZm8rx8Sxi_cJwtXKeVNazeM"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        if "-- INVALID QUESTION" in text:
            return {"sql": None, "humanized": "Invalid question."}

        # Split into SQL and humanized response
        sql_part = ""
        human_part = ""
        if "SQL:" in text and "Humanized:" in text:
            parts = text.split("Humanized:")
            sql_part = parts[0].replace("SQL:", "").strip()
            human_part = parts[1].strip()
        else:
            sql_part = text.strip()
            human_part = ""

        return {
            "sql": sql_part.strip("```sql").strip("```").strip(),
            "humanized": human_part
        }
    except Exception as e:
        return {"sql": None, "humanized": f"Error: {e}"}
