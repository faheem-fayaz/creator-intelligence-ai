from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs, unquote
import re

from app.services.whisper_service import transcribe_audio


def extract_video_id(url: str):

    url = unquote(url)
    parsed_url = urlparse(url)

    # youtu.be links
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]

    # youtube.com/watch?v=
    if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed_url.query).get("v", [None])[0]

    # Instagram Reels — return a unique ID from the URL
    if parsed_url.hostname in ("www.instagram.com", "instagram.com"):
        match = re.search(r"/reel/([^/]+)/", parsed_url.path)
        if match:
            return f"ig_{match.group(1)}"
        match = re.search(r"/p/([^/]+)/", parsed_url.path)
        if match:
            return f"ig_{match.group(1)}"

    return None


def is_instagram_url(url: str) -> bool:
    parsed = urlparse(unquote(url))
    return parsed.hostname in ("www.instagram.com", "instagram.com")


def is_youtube_url(url: str) -> bool:
    parsed = urlparse(unquote(url))
    return parsed.hostname in (
        "www.youtube.com",
        "youtube.com",
        "youtu.be",
    )


def get_transcript(video_url: str):

    video_id = extract_video_id(video_url)

    if not video_id:
        return {"error": "Invalid URL — must be YouTube or Instagram Reel"}

    # --- INSTAGRAM REELS ---
    if is_instagram_url(video_url):
        return _get_instagram_transcript(video_url, video_id)

    # --- YOUTUBE ---
    return _get_youtube_transcript(video_url, video_id)


def _get_youtube_transcript(video_url: str, video_id: str):

    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)

        segments = []
        for item in transcript_data:
            segments.append({
                "text": item.text,
                "start": item.start,
                "duration": item.duration,
            })

        full_text = " ".join([s["text"] for s in segments])

        return {
            "video_id": video_id,
            "transcript": full_text,
            "segments": segments,
            "source": "youtube_transcript_api",
        }

    except Exception as e:
        print("YouTube Transcript API failed, falling back to Whisper...")
        print(e)

        try:
            whisper_data = transcribe_audio(video_url)
            return {
                "video_id": video_id,
                "transcript": whisper_data["transcript"],
                "segments": whisper_data["segments"],
                "source": "whisper",
            }
        except Exception as whisper_error:
            return {
                "error": "Both transcript methods failed.",
                "details": str(whisper_error),
            }


def _get_instagram_transcript(video_url: str, video_id: str):
    """
    Instagram Reels have no caption API.
    We use yt-dlp to download audio, then Whisper to transcribe.
    yt-dlp supports Instagram Reels natively.
    """
    print(f"Instagram Reel detected: {video_url}")
    print("Using yt-dlp + Whisper for transcription...")

    try:
        whisper_data = transcribe_audio(video_url)

        return {
            "video_id": video_id,
            "transcript": whisper_data["transcript"],
            "segments": whisper_data["segments"],
            "source": "whisper_instagram",
        }

    except Exception as e:
        return {
            "error": "Instagram transcript failed.",
            "details": str(e),
        }