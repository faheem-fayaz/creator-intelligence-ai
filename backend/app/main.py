from fastapi import Depends, FastAPI
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
from app.auth.dependencies import get_current_user
from app.auth.router import router as auth_router
from app.database import Base, engine
from app.models import User

app = FastAPI(title="Creator Intelligence API")

Base.metadata.create_all(bind=engine)
app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://creator-intelligence-ai.vercel.app",
    ],
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
def transcript(url: str, current_user: User = Depends(get_current_user)):
    return get_transcript(url)


@app.get("/ingest")
def ingest_video(url: str, current_user: User = Depends(get_current_user)):
    return ingest_if_needed(url)


@app.get("/search")
def search(query: str, current_user: User = Depends(get_current_user)):
    return semantic_search(query)


@app.get("/ask")
def ask(
    query: str,
    video_url: str,
    current_user: User = Depends(get_current_user)
):
    ingest_result = ingest_if_needed(video_url)

    if "error" in ingest_result:
        return ingest_result

    video_id = extract_video_id(video_url)

    return ask_question(
        question=query,
        video_id=video_id
    )


@app.get("/compare")
def compare(video1: str, video2: str, query: str, current_user: User = Depends(get_current_user)):
    ingest_if_needed(video1)
    ingest_if_needed(video2)
    return compare_videos(video1, video2, query)


@app.get("/hook-analysis")
def hook_analysis(url: str, current_user: User = Depends(get_current_user)):
    return analyze_hook(url)


@app.get("/score")
def score(url: str, current_user: User = Depends(get_current_user)):
    return score_video(url)


@app.get("/stream-ask")
def stream_ask(query: str, current_user: User = Depends(get_current_user)):
    return StreamingResponse(stream_answer(query), media_type="text/plain")


@app.get("/memory-chat")
def memory_chat_endpoint(session_id: str, query: str, video_url: str = None, current_user: User = Depends(get_current_user)):
    return memory_chat(session_id, query, video_url)


@app.get("/video-score")
def video_score(
    url: str,
    current_user: User = Depends(get_current_user)
):
    # Make sure transcript is available in Chroma
    ingest_result = ingest_if_needed(url)

    if "error" in ingest_result:
        return ingest_result

    # Get transcript for scoring
    transcript_data = get_transcript(url)

    if "error" in transcript_data:
        return transcript_data

    score_data = generate_video_score(
        transcript_data["transcript"]
    )

    metadata = extract_basic_metadata(url)

    return {
        "metadata": metadata,
        "analysis": score_data,
        "transcript_source": transcript_data.get("source"),
    }