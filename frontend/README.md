# Creator Intelligence Platform

A full-stack RAG-powered platform for analyzing, comparing, and improving social media video content. Built with Next.js, FastAPI, LangChain, ChromaDB, and Groq.

---

## What It Does

- Paste any YouTube or Instagram Reel URL
- Pulls transcript + metadata (views, likes, comments, followers, engagement rate)
- Chunks and embeds the transcript into ChromaDB
- Chat with an AI that answers questions grounded in the actual video content
- Compare two videos side by side with real engagement data
- Memory across conversation turns — follow-up questions work naturally
- Streamed responses with timestamped citations

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js + Tailwind | Fast, server-side rendering, easy deployment |
| Backend | FastAPI | Async Python, automatic docs, lightweight |
| Orchestration | LangChain | ChatPromptTemplate + MessagesPlaceholder for memory-aware chains |
| Embeddings | sentence-transformers (MiniLM-L6) | Free, runs locally, 384-dim vectors, fast inference |
| Vector DB | ChromaDB | Zero-config, persistent, runs locally, no external service needed |
| LLM | Groq + Llama 3.3 70B | Fastest inference available, free tier, near GPT-4 quality |
| Transcripts | youtube-transcript-api + yt-dlp + Whisper | Caption API first (fast), Whisper fallback for Instagram/no-captions |
| Metadata | yt-dlp | Pulls views, likes, comments, followers, upload date in one call |

---

## Architecture

```
User
  │
  ▼
Next.js Frontend
  │  (GET /compare, /video-score, /memory-chat, /stream-ask)
  ▼
FastAPI Backend
  ├── transcript_service     → YouTube Transcript API → yt-dlp+Whisper fallback
  ├── metadata_service       → yt-dlp (views, likes, comments, followers, engagement)
  ├── chunking_service       → splits transcript into 5-segment chunks with timestamps
  ├── embedding_service      → MiniLM-L6 sentence-transformers
  ├── chroma_store           → PersistentClient, tagged by video_id
  ├── search_service         → semantic_search with video_id filter
  ├── memory_rag_service     → LangChain chain (prompt | llm | parser) + session memory
  ├── comparison_service     → dual retrieval, metadata injection, Groq LLM
  ├── stream_service         → Groq streaming via StreamingResponse
  └── scoring_service        → AI scoring: hook, emotion, retention, virality, storytelling
```

---

## Running at Scale — 1000 Creators/Day

### Current setup (dev)
- ChromaDB local, Whisper tiny model, Groq free tier
- Cost: ~$0/day
- Limit: single machine, no parallelism

### Production path (1000 creators/day)

**Transcripts**
- YouTube Transcript API is free and instant for captioned videos (~80% of videos)
- Whisper tiny on CPU handles the rest — ~30s per video
- At 1000/day: ~200 Whisper jobs → run on 2x EC2 t3.medium instances with a job queue (Redis + Celery)

**Embeddings**
- MiniLM-L6 runs locally, no API cost
- 1000 videos × ~20 chunks × ~1ms per embed = ~20 seconds total
- Cost: $0

**Vector DB**
- ChromaDB works up to ~1M vectors without issue
- At 1000 creators/day × 20 chunks = 20K vectors/day
- Switch to Qdrant Cloud or Pinecone at 10M+ vectors for horizontal scaling

**LLM**
- Groq free tier: 14,400 requests/day, 500K tokens/minute
- At 1000 creators: depends on query volume, not ingestion
- Groq is 10x cheaper than OpenAI GPT-4o at same quality for Llama 3.3 70B
- If budget allows: GPT-4o-mini at $0.15/1M tokens for highest accuracy

**Estimated cost at 1000 creators/day**
| Component | Cost |
|---|---|
| Embeddings (MiniLM local) | $0 |
| Transcripts (YT API) | $0 |
| Whisper (self-hosted) | ~$2/day EC2 |
| Groq LLM | $0 (free tier) or ~$1-2/day paid |
| ChromaDB (local/self-hosted) | $0 |
| **Total** | **~$2-4/day** |

### What breaks at 10,000 users
- ChromaDB local → migrate to Qdrant Cloud (horizontal sharding)
- Single FastAPI process → add Gunicorn workers + load balancer
- Whisper on one machine → distributed queue with auto-scaling workers
- Session memory in-memory → move to Redis for multi-instance support

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Add your GROQ_API_KEY to .env

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install

cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

---

## Environment Variables

**backend/.env**
```
GROQ_API_KEY=your_groq_api_key
```

**frontend/.env.local**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Key Design Decisions

**Why ChromaDB over Pinecone?**
Zero setup, persistent, free, runs locally. Pinecone adds latency and cost for no benefit at this scale. Easy to swap — just replace `chroma_store.py`.

**Why MiniLM over OpenAI embeddings?**
OpenAI ada-002 costs $0.0001/1K tokens. At 1000 creators × 20 chunks × 100 tokens = 2M tokens/day = $0.20/day. MiniLM is free and within 5% accuracy for semantic search on conversational content.

**Why Groq over OpenAI?**
Groq inference is 10-25x faster than OpenAI. For a real-time chat interface, latency matters more than marginal quality difference. Llama 3.3 70B on Groq matches GPT-4o on most creator analysis tasks.

**Why chunk size 5 segments?**
Each segment is ~5-10 seconds of speech. 5 segments = ~30 seconds of content per chunk. Small enough for precise retrieval, large enough to have context. Tested against 3 and 10 — 5 gave the most relevant citations.

**Why auto-ingest on compare?**
Eliminates a manual step. The `/compare` endpoint checks ChromaDB first — if the video is already indexed it skips ingestion entirely. First-time ingestion adds ~3-5 seconds, subsequent calls are instant.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/ingest?url=` | Ingest video transcript into ChromaDB |
| GET | `/transcript?url=` | Get raw transcript + segments |
| GET | `/video-score?url=` | AI scoring (hook, emotion, virality, etc.) |
| GET | `/hook-analysis?url=` | Detailed hook analysis |
| GET | `/compare?video1=&video2=&query=` | Compare two videos with metadata |
| GET | `/ask?query=` | RAG question answering |
| GET | `/stream-ask?query=` | Streaming RAG response |
| GET | `/memory-chat?session_id=&query=&video_url=` | Memory-aware LangChain chat |

---

## Project Structure

```
creator-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── services/
│   │   │   ├── transcript_service.py     # YouTube + Instagram
│   │   │   ├── metadata_service.py       # yt-dlp metadata + engagement rate
│   │   │   ├── chunking_service.py       # Segment chunking
│   │   │   ├── embedding_service.py      # MiniLM embeddings
│   │   │   ├── search_service.py         # Semantic search
│   │   │   ├── memory_rag_service.py     # LangChain chain + session memory
│   │   │   ├── comparison_service.py     # Dual-video RAG comparison
│   │   │   ├── stream_service.py         # Streaming responses
│   │   │   ├── scoring_service.py        # AI video scoring
│   │   │   ├── hook_service.py           # Hook analysis
│   │   │   ├── citation_service.py       # Timestamped citations
│   │   │   ├── query_rewriter.py         # Follow-up query rewriting
│   │   │   ├── context_service.py        # Video context summary
│   │   │   ├── memory_service.py         # Session state management
│   │   │   └── whisper_service.py        # yt-dlp + Whisper transcription
│   │   └── vectorstore/
│   │       └── chroma_store.py           # ChromaDB store/search
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── app/
    │   ├── page.tsx                      # Main UI
    │   └── layout.tsx
    ├── package.json
    └── .env.example
```