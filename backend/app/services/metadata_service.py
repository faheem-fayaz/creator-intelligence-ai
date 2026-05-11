import re
import json
import os

from groq import Groq
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# Simple metadata extraction
# (Later you can replace with YouTube API)
def extract_basic_metadata(video_url):

    video_id = None

    if "v=" in video_url:
        video_id = video_url.split("v=")[-1]

    return {
        "video_id": video_id,
        "platform": "youtube",
        "url": video_url
    }


# AI-powered creator scoring
# Uses transcript + creator psychology reasoning
def generate_video_score(transcript):

    prompt = f"""
You are an expert creator strategist.

Analyze this transcript like a high-level creator intelligence platform.

TRANSCRIPT:
{transcript}

Return ONLY valid JSON.

Required JSON structure:

{{
  "hook_score": 0,
  "clarity_score": 0,
  "emotion_score": 0,
  "retention_score": 0,
  "virality_score": 0,
  "storytelling_score": 0,
  "overall_score": 0,
  "content_style": "",
  "predicted_audience": [],
  "strengths": [],
  "weaknesses": [],
  "improvements": []
}}

Scoring rules:
- Scores should be from 1-10
- Be realistic
- Analyze emotional hooks
- Analyze pacing
- Analyze storytelling
- Analyze engagement psychology
- Analyze retention quality
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

    response = completion.choices[0].message.content

    # Remove markdown wrappers if model adds them
    response = re.sub(r"```json", "", response)
    response = re.sub(r"```", "", response)

    try:

        return json.loads(
            response.strip()
        )

    except Exception:

        return {
            "raw_response": response
        }