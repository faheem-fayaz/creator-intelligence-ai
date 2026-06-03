from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.services.transcript_service import get_transcript, extract_video_id
from app.services.chunking_service import chunk_transcript
from app.services.embedding_service import generate_embedding
from app.services.search_service import semantic_search
from app.services.rag_service import ask_question
from app.services.comparison_service import compare_videos
from app.services.hook_service import analyze_hook
from app.services.scoring_service import score_video
from app.services.stream_service import stream_answer
from app.services.memory_rag_service import memory_chat
from app.services.metadata_service import extract_basic_metadata, generate_video_score
from app.vectorstore.chroma_store import store_chunk, collection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ingest_if_needed(url: str):
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "Invalid URL"}

    existing = collection.get(where={"video_id": video_id})
    if existing and len(existing["ids"]) > 0:
        return {"message": "Already ingested", "chunks_stored": len(existing["ids"])}

    data = get_transcript(url)
    if "error" in data:
        return data

    chunks = chunk_transcript(data["segments"])

    for i, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk["text"])
        store_chunk(
            chunk_id=f"{data['video_id']}_{i}",
            text=chunk["text"],
            embedding=embedding,
            metadata={
                "video_id": data["video_id"],
                "start": chunk["start"],
                "end": chunk["end"],
            },
        )

    return {"message": "Ingested", "chunks_stored": len(chunks)}


@app.get("/")
def home():
    return {"message": "Creator Intelligence API Running"}


@app.get("/transcript")
def transcript(url: str):
    return get_transcript(url)


@app.get("/ingest")
def ingest_video(url: str):
    return ingest_if_needed(url)


@app.get("/search")
def search(query: str):
    return semantic_search(query)


@app.get("/ask")
def ask(query: str):
    return ask_question(query)


@app.get("/compare")
def compare(video1: str, video2: str, query: str):
    ingest_if_needed(video1)
    ingest_if_needed(video2)
    return compare_videos(video1, video2, query)


@app.get("/hook-analysis")
def hook_analysis(url: str):
    return analyze_hook(url)


@app.get("/score")
def score(url: str):
    return score_video(url)


@app.get("/stream-ask")
def stream_ask(query: str):
    return StreamingResponse(stream_answer(query), media_type="text/plain")


@app.get("/memory-chat")
def memory_chat_endpoint(session_id: str, query: str, video_url: str = None):
    return memory_chat(session_id, query, video_url)


@app.get("/video-score")
def video_score(url: str):
    transcript_data = get_transcript(url)
    if "error" in transcript_data:
        return transcript_data
    score_data = generate_video_score(transcript_data["transcript"])
    metadata = extract_basic_metadata(url)
    return {
        "metadata": metadata,
        "analysis": score_data,
        "transcript_source": transcript_data.get("source"),
    }