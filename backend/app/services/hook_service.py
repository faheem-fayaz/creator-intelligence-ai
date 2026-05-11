from app.services.transcript_service import get_transcript

from groq import Groq
from dotenv import load_dotenv

import os

load_dotenv(dotenv_path=".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_hook(video_url):

    data = get_transcript(video_url)

    # Handle transcript errors safely
    if "segments" not in data:
        return {
            "error": "Transcript not available for this video."
        }

    segments = data["segments"]

    # Extract meaningful hook content
    hook_segments = []

    for segment in segments:

        text = segment["text"].strip()

        # Skip music/noise-only captions
        if "♪" in text:
            continue

        # Skip tiny meaningless chunks
        if len(text) < 10:
            continue

        # Use first 30 seconds
        if segment["start"] <= 30:
            hook_segments.append(text)

    hook_text = " ".join(hook_segments)

    # Handle empty hook text
    if not hook_text:
        return {
            "error": "No meaningful hook transcript found."
        }

    prompt = f"""
You are an expert creator strategist.

Analyze this video hook.

HOOK TRANSCRIPT:
{hook_text}

Analyze:
1. Emotional trigger
2. Curiosity gap
3. Attention retention
4. Pacing
5. Clarity
6. Audience psychology
7. Virality potential

Give actionable creator advice.
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
        "hook_transcript": hook_text,
        "analysis": answer
    }