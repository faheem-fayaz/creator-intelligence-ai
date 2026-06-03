import os
import yt_dlp

from faster_whisper import WhisperModel


# Load Whisper model once
model = None


def download_audio(video_url):

    os.makedirs("temp_audio", exist_ok=True)

    output_path = "temp_audio/audio"

    ydl_opts = {
        "format": "worstaudio",
        "outtmpl": output_path,
        "quiet": False,
        "noplaylist": True,
        "extractaudio": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "64",
            }
        ],
    }

    # Use local FFmpeg if available, otherwise let yt-dlp find it on PATH
    ffmpeg_local = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"
    if os.path.exists(ffmpeg_local):
        ydl_opts["ffmpeg_location"] = ffmpeg_local

    print(f"Downloading audio from: {video_url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    audio_file = output_path + ".mp3"

    print(f"Audio saved at: {audio_file}")

    return audio_file


def transcribe_audio(video_url):
    global model

    if model is None:
        model = WhisperModel("tiny", compute_type="int8")

    audio_path = download_audio(video_url)

    print("Starting Whisper transcription...")

    segments, info = model.transcribe(audio_path, beam_size=5)

    transcript_segments = []
    full_text = ""

    for segment in segments:

        text = segment.text.strip()

        if len(text) < 3 or text == "." or text.count(".") > 3:
            continue

        transcript_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": text,
        })

        full_text += text + " "

    print("Transcription complete.")

    return {
        "transcript": full_text.strip(),
        "segments": transcript_segments,
    }