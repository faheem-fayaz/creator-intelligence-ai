from app.services.search_service import semantic_search
from app.services.transcript_service import extract_video_id

from groq import Groq
from dotenv import load_dotenv

import os

load_dotenv(dotenv_path=".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def compare_videos(video_url_1, video_url_2, question):

    video_id_1 = extract_video_id(video_url_1)
    video_id_2 = extract_video_id(video_url_2)

    results_1 = semantic_search(
        question,
        video_id=video_id_1
    )

    results_2 = semantic_search(
        question,
        video_id=video_id_2
    )

    context_1 = "\n".join(results_1["documents"][0])

    context_2 = "\n".join(results_2["documents"][0])

    prompt = f"""
You are an expert creator strategist.

Compare these two videos and answer the user's question.

VIDEO A:
{context_1}

VIDEO B:
{context_2}

QUESTION:
{question}

Give:
- strengths
- weaknesses
- hook analysis
- engagement reasoning
- pacing analysis
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    answer = completion.choices[0].message.content

    return {
        "question": question,
        "comparison": answer,
        "video_1_sources": results_1["metadatas"][0],
        "video_2_sources": results_2["metadatas"][0]
    }