import os
import yt_dlp

from faster_whisper import WhisperModel


# Load Whisper model once
model =None


def download_audio(video_url):

    # Create temp directory if missing
    os.makedirs(
        "temp_audio",
        exist_ok=True
    )

    output_path = "temp_audio/audio"

    ydl_opts = {

        # Best audio
        "format": "worstaudio",

        # Save path
        "outtmpl": output_path,

        # Logging
        "quiet": False,

        # Avoid playlists
        "noplaylist": True,

        # Explicit FFmpeg path
        "ffmpeg_location": r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin",

        # Extract audio
        "extractaudio": True,

        # Convert to mp3
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "64",
            }
        ],
    }

    print("Downloading audio...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    audio_file = output_path + ".mp3"

    print(f"Audio saved at: {audio_file}")

    return audio_file


def transcribe_audio(video_url):
    global model

    if model is None:
        model = WhisperModel(
            "tiny",
            compute_type="int8"
        )   

    audio_path = download_audio(video_url)

    print("Starting Whisper transcription...")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5
    )

    transcript_segments = []

    full_text = ""

    for segment in segments:

        text = segment.text.strip()

        # Skip useless chunks
        if (
            len(text) < 3
            or text == "."
            or text.count(".") > 3
        ):
            continue

        transcript_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": text
        })

        full_text += text + " "

    print("Transcription complete.")

    return {
        "transcript": full_text.strip(),
        "segments": transcript_segments
    }