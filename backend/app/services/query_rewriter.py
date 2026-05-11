import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def rewrite_query(history, latest_question):

    history_text = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in history[-6:]
    ])

    prompt = f"""
Rewrite the user's latest question into a fully standalone query.

Conversation History:
{history_text}

Latest Question:
{latest_question}

Return ONLY the rewritten standalone query.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    rewritten = completion.choices[0].message.content

    return rewritten.strip()