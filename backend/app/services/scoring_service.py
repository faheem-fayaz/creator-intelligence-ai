from app.services.transcript_service import get_transcript

from groq import Groq
from dotenv import load_dotenv

import os
import json

load_dotenv(dotenv_path=".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def score_video(video_url):

    data = get_transcript(video_url)

    if "segments" not in data:
        return {
            "error": "Transcript not available."
        }

    transcript = data["transcript"][:4000]

    prompt = f"""
You are an expert creator strategist.

Analyze this video transcript and score it.

Return ONLY valid JSON.

Transcript:
{transcript}

Return format:
{{
    "hook_score": number,
    "clarity_score": number,
    "emotion_score": number,
    "retention_score": number,
    "virality_score": number,
    "summary": "short explanation"
}}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )
        
    answer = completion.choices[0].message.content

    # Remove markdown code blocks
    cleaned = answer.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        return {
            "error": str(e),
            "raw_response": answer
        }