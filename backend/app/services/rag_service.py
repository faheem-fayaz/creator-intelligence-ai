import os

from groq import Groq
from dotenv import load_dotenv

from app.services.citation_service import build_citations
from app.services.search_service import semantic_search


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_question(question: str, video_id: str):

    # Retrieve relevant chunks from this specific video
    results = semantic_search(
        question,
        video_id=video_id
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        return {
            "question": question,
            "answer": "I couldn't find transcript content for this video. Please run the analysis again and try your question.",
            "citations": [],
            "sources": []
        }

    # Build citations
    citations = build_citations(results)

    # Build transcript context
    context = "\n".join(documents)

    prompt = f"""
You are an AI creator coach.

Answer the user's question using ONLY the transcript context below.

IMPORTANT:
- Be concise but insightful
- Reference emotional hooks
- Reference storytelling
- Reference creator psychology
- Use evidence from transcript context
- Do not invent information that is not present in the transcript

Transcript Context:
{context}

Question:
{question}
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    answer = completion.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "sources": results.get("metadatas", [[]])[0]
    }