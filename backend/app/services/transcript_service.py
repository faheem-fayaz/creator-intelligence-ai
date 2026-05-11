from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs, unquote

from app.services.whisper_service import transcribe_audio


def extract_video_id(url: str):

    url = unquote(url)

    parsed_url = urlparse(url)

    # youtu.be links
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]

    # youtube.com/watch?v=
    if parsed_url.hostname in (
        "www.youtube.com",
        "youtube.com"
    ):
        return parse_qs(
            parsed_url.query
        ).get("v", [None])[0]

    return None


def get_transcript(video_url: str):

    video_id = extract_video_id(video_url)

    if not video_id:
        return {
            "error": "Invalid YouTube URL"
        }

    try:

        api = YouTubeTranscriptApi()

        transcript_data = api.fetch(video_id)

        segments = []

        for item in transcript_data:

            segments.append({
                "text": item.text,
                "start": item.start,
                "duration": item.duration
            })

        full_text = " ".join([
            item["text"]
            for item in segments
        ])

        return {
            "video_id": video_id,
            "transcript": full_text,
            "segments": segments,
            "source": "youtube_transcript_api"
        }

    except Exception as e:

        print("Transcript API failed.")
        print("Falling back to Whisper...")
        print(e)

        try:

            whisper_data = transcribe_audio(video_url)

            return {
                "video_id": video_id,
                "transcript": whisper_data["transcript"],
                "segments": whisper_data["segments"],
                "source": "whisper"
            }

        except Exception as whisper_error:

            return {
                "error": "Both transcript methods failed.",
                "details": str(whisper_error)
            }