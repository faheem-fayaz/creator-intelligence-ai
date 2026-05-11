import os

from groq import Groq
from dotenv import load_dotenv

from app.services.search_service import semantic_search
from app.services.transcript_service import extract_video_id
from app.services.query_rewriter import rewrite_query
from app.services.context_service import generate_video_context

from app.services.memory_service import (
    set_session_context,
    get_session_context
)
from app.services.memory_service import (
    save_message,
    get_conversation,
    set_session_video,
    get_session_video
)

load_dotenv(dotenv_path=".env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def memory_chat(session_id, question, video_url=None):

    # Set session video if provided
    if video_url:

        video_id = extract_video_id(video_url)

        context_summary = generate_video_context(video_url)

        set_session_context(
            session_id,
            context_summary
        )

    # Retrieve stored session video
    active_video = get_session_video(session_id)

    history = get_conversation(session_id)
    session_context = get_session_context(session_id)

    # Rewrite vague follow-up questions
    rewritten_query = rewrite_query(
        history,
        question
    )

    # Save user message
    save_message(session_id, "user", question)

    # Better semantic retrieval
    results = semantic_search(
        rewritten_query,
        video_id=active_video
    )

    documents = results["documents"][0]

    context = "\n".join(documents)

    history = get_conversation(session_id)

    messages = [
        {
            "role": "system",
            "content": f"""
You are an expert creator strategist.

Use the transcript context and conversation history
to answer intelligently.

VIDEO CONTEXT SUMMARY:
{session_context}

TRANSCRIPT CONTEXT:
{context}
"""
        }
    ]

    messages.extend(history)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3
    )

    answer = completion.choices[0].message.content

    save_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "active_video": active_video,
        "rewritten_query": rewritten_query,
"answer": answer,
        "history_length": len(history)
    }
