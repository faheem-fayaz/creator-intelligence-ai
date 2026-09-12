from app.services.transcript_service import get_transcript

from groq import Groq

import os
import json


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def score_video(video_url: str):

    data = get_transcript(video_url)

    if "segments" not in data:
        return {
            "error": data.get(
                "error",
                "Transcript not available."
            )
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

Scoring rules:

- Scores must be numbers from 0 to 100.
- hook_score evaluates the strength of the opening/message hook
  based only on the provided transcript.
- clarity_score evaluates how clearly the content communicates
  its main idea.
- emotion_score evaluates emotional engagement present in the
  transcript.
- retention_score estimates the transcript's ability to maintain
  viewer interest based only on the provided text.
- virality_score estimates shareability based only on the
  provided transcript.
- Do not invent information that is not present in the transcript.
"""

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        answer = completion.choices[0].message.content

        cleaned = (
            answer
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed = json.loads(cleaned)

        return parsed

    except json.JSONDecodeError:
        return {
            "error": "AI returned an invalid JSON response."
        }

    except Exception as e:
        print("Video scoring failed.")
        print(e)

        return {
            "error": "Failed to generate video score."
        }