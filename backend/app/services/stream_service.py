import os

from groq import Groq
from dotenv import load_dotenv

from app.services.search_service import semantic_search

load_dotenv(dotenv_path=".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def stream_answer(question: str):

    results = semantic_search(question)

    documents = results["documents"][0]

    context = "\n".join(documents)

    prompt = f"""
You are an expert creator strategist.

Answer the user's question using the context below.

CONTEXT:
{context}

QUESTION:
{question}
"""

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        stream=True
    )

    for chunk in stream:

        content = chunk.choices[0].delta.content

        if content:
            yield content