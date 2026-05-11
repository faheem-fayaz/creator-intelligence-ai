import os

from groq import Groq
from dotenv import load_dotenv

from app.services.citation_service import build_citations
from app.services.search_service import semantic_search


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_question(question: str):

    # Retrieve relevant chunks
    results = semantic_search(question)

    # Build citations
    citations = build_citations(results)

    # Extract documents
    documents = results["documents"][0]

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

Transcript Context:
{context}

Question:
{question}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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
        "sources": results["metadatas"][0]
    }