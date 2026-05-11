import os

from groq import Groq
from dotenv import load_dotenv

from app.services.transcript_service import get_transcript

load_dotenv(dotenv_path=".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_video_context(video_url):

    data = get_transcript(video_url)

    if "transcript" not in data:
        return None

    transcript = data["transcript"][:5000]

    prompt = f"""
Analyze this video transcript.

Return:
1. Short summary
2. Main themes
3. Emotional tone
4. Key topics

Transcript:
{transcript}
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

    return completion.choices[0].message.content