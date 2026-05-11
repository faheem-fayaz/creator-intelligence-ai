from fastapi import FastAPI

from app.services.transcript_service import get_transcript
from app.services.chunking_service import chunk_transcript
from app.services.embedding_service import generate_embedding
from app.services.search_service import semantic_search
from app.services.rag_service import ask_question
from app.services.comparison_service import compare_videos
from app.services.hook_service import analyze_hook
from app.services.scoring_service import score_video
from fastapi.responses import StreamingResponse
from app.services.stream_service import stream_answer
from app.services.memory_rag_service import memory_chat
from app.services.metadata_service import (
    extract_basic_metadata,
    generate_video_score
)
from fastapi.middleware.cors import CORSMiddleware



from app.vectorstore.chroma_store import store_chunk

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Creator Intelligence API Running"}


@app.get("/transcript")
def transcript(url: str):
    return get_transcript(url)


@app.get("/ingest")
def ingest_video(url: str):

    # Step 1: Get transcript data
    data = get_transcript(url)

    # Step 2: Chunk transcript
    chunks = chunk_transcript(data["segments"])

    # Step 3: Generate embeddings + store in ChromaDB
    for i, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk["text"])

        store_chunk(
            chunk_id=f"{data['video_id']}_{i}",
            text=chunk["text"],
            embedding=embedding,
            metadata={
                "video_id": data["video_id"],
                "start": chunk["start"],
                "end": chunk["end"]
            }
        )

    return {
        "message": "Video ingested successfully",
        "chunks_stored": len(chunks)
    }
@app.get("/search")
def search(query: str):

    results = semantic_search(query)

    return results
@app.get("/ask")
def ask(query: str):

    response = ask_question(query)

    return response
@app.get("/compare")
def compare(video1: str, video2: str, query: str):

    response = compare_videos(
        video1,
        video2,
        query
    )

    return response
@app.get("/hook-analysis")
def hook_analysis(url: str):

    response = analyze_hook(url)

    return response

@app.get("/score")
def score(url: str):

    response = score_video(url)

    return response
@app.get("/stream-ask")
def stream_ask(query: str):

    return StreamingResponse(
        stream_answer(query),
        media_type="text/plain"
    )
@app.get("/memory-chat")
def memory_chat_endpoint(
    session_id: str,
    query: str,
    video_url: str = None
):

    response = memory_chat(
        session_id,
        query,
        video_url
    )

    return response
@app.get("/video-score")
def video_score(url: str):

    # Get transcript
    transcript_data = get_transcript(url)

    # Handle transcript errors
    if "error" in transcript_data:
        return transcript_data

    # Generate AI scoring
    score_data = generate_video_score(
        transcript_data["transcript"]
    )

    metadata = extract_basic_metadata(url)

    return {
        "metadata": metadata,
        "analysis": score_data,
        "transcript_source": transcript_data.get("source")
    }