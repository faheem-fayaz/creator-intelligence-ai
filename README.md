\# Creator Intelligence AI



AI-powered creator analysis platform for:



\* Hook analysis

\* Emotional storytelling analysis

\* Virality prediction

\* Retention analysis

\* Transcript intelligence

\* AI creator chat (RAG)

\* Video comparison



Built using:



\* Next.js

\* FastAPI

\* Groq LLMs

\* ChromaDB

\* Faster Whisper

\* yt-dlp

\* TailwindCSS



\---



\# Features



\## AI Creator Scoring



Analyze videos for:



\* Hook quality

\* Emotional engagement

\* Retention potential

\* Virality

\* Storytelling



\---



\## Hook Analysis



AI-powered breakdown of:



\* Emotional triggers

\* Curiosity gaps

\* Attention retention

\* Audience psychology

\* Creator strategy



\---



\## AI Creator Chat



RAG-powered creator assistant with:



\* Transcript citations

\* Semantic retrieval

\* Context-aware answers

\* Creator psychology analysis



\---



\## Video Comparison



Compare two videos for:



\* Emotional storytelling

\* Hook effectiveness

\* Retention strength

\* Virality potential



\---



\## Transcript Intelligence



\* Automatic transcript extraction

\* Whisper fallback support

\* Timestamped transcript viewer



\---



\# Architecture



```txt

Frontend (Next.js)

&#x20;   ↓

FastAPI Backend

&#x20;   ↓

Transcript + Whisper Layer

&#x20;   ↓

ChromaDB Vector Search

&#x20;   ↓

Groq LLM Analysis Engine

```



\---



\# Tech Stack



| Layer              | Technology            |

| ------------------ | --------------------- |

| Frontend           | Next.js + TailwindCSS |

| Backend            | FastAPI               |

| AI Models          | Groq Llama 3          |

| Vector DB          | ChromaDB              |

| Speech Recognition | Faster Whisper        |

| Video Processing   | yt-dlp + ffmpeg       |

| Embeddings         | sentence-transformers |



\---



\# Local Setup



\## Backend Setup



```bash

cd backend



python -m venv venv



venv\\Scripts\\activate



pip install -r requirements.txt

```



Create `.env`



```env

GROQ\_API\_KEY=your\_api\_key\_here

```



Run backend:



```bash

uvicorn app.main:app --reload

```



\---



\## Frontend Setup



```bash

cd frontend



npm install

```



Create `.env.local`



```env

NEXT\_PUBLIC\_API\_URL=http://localhost:8000

```



Run frontend:



```bash

npm run dev

```



\---



\# API Endpoints



| Endpoint         | Description           |

| ---------------- | --------------------- |

| `/video-score`   | AI creator scoring    |

| `/hook-analysis` | Hook analysis         |

| `/ask`           | RAG creator chat      |

| `/compare`       | Compare videos        |

| `/transcript`    | Transcript extraction |



\---



\# Future Improvements



\* Creator trend analysis

\* Thumbnail analysis

\* AI title generation

\* Multi-platform creator analytics

\* YouTube metadata intelligence

\* Audience sentiment analysis



\---

\# Screenshots



\## Dashboard



!\[Dashboard](./screenshots/dashboard.png)



\---



\## Video Score



!\[Video Score](./screenshots/video-score.png)



\---



\## Hook Analysis



!\[Hook Analysis](./screenshots/hook-analysis.png)



\---



\## AI Creator Chat



!\[Chat](./screenshots/chat.png)



\---



\## Transcript Viewer



!\[Transcript](./screenshots/transcript.png)



\---



\## Compare Videos



!\[Compare](./screenshots/compare.png)



\# Author



Faheem Fayaz



