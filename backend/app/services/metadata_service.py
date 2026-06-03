import re
import json
import os
import yt_dlp

from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_basic_metadata(video_url):

    try:
        ydl_opts = {
            "quiet": True,
            "extract_flat": False,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        views = info.get("view_count") or 0
        likes = info.get("like_count") or 0
        comments = info.get("comment_count") or 0
        followers = info.get("channel_follower_count") or 0

        engagement_rate = 0
        if views:
            engagement_rate = round(
                ((likes + comments) / views) * 100, 2
            )

        return {
            "video_id": info.get("id"),
            "title": info.get("title"),
            "creator": info.get("channel"),
            "views": views,
            "likes": likes,
            "comments": comments,
            "followers": followers,
            "duration": info.get("duration"),
            "upload_date": info.get("upload_date"),
            "hashtags": info.get("tags", [])[:10],
            "engagement_rate": engagement_rate,
            "platform": "youtube",
            "url": video_url,
        }

    except Exception as e:
        print("Metadata extraction failed:", e)
        video_id = None
        if "v=" in video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]
        return {
            "video_id": video_id,
            "title": None,
            "creator": None,
            "views": 0,
            "likes": 0,
            "comments": 0,
            "followers": 0,
            "duration": 0,
            "upload_date": None,
            "hashtags": [],
            "engagement_rate": 0,
            "platform": "youtube",
            "url": video_url,
        }


def generate_video_score(transcript):

    prompt = f"""
You are an expert creator strategist.

Analyze this transcript like a high-level creator intelligence platform.

TRANSCRIPT:
{transcript}

Return ONLY valid JSON. No markdown, no backticks, nothing else.

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
- Scores from 1-10
- Be realistic
- Analyze emotional hooks, pacing, storytelling, engagement psychology
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    response = completion.choices[0].message.content
    response = re.sub(r"```json", "", response)
    response = re.sub(r"```", "", response)

    try:
        return json.loads(response.strip())
    except Exception:
        return {"raw_response": response}