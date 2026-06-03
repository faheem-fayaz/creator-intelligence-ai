import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.services.search_service import semantic_search
from app.services.transcript_service import extract_video_id
from app.services.query_rewriter import rewrite_query
from app.services.context_service import generate_video_context
from app.services.memory_service import (
    set_session_context,
    get_session_context,
    save_message,
    get_conversation,
    set_session_video,
    get_session_video,
)

load_dotenv(dotenv_path=".env")


# LangChain LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.3,
)

# LangChain prompt template with memory placeholder
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert creator strategist.

Use the transcript context and conversation history to answer intelligently.

VIDEO CONTEXT SUMMARY:
{session_context}

TRANSCRIPT CONTEXT:
{context}
""",
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

# LangChain chain: prompt | llm | parser
chain = prompt | llm | StrOutputParser()


def memory_chat(session_id: str, question: str, video_url: str = None):

    # Set session video if provided
    if video_url:
        video_id = extract_video_id(video_url)
        context_summary = generate_video_context(video_url)
        set_session_context(session_id, context_summary)
        set_session_video(session_id, video_id)

    # Retrieve stored session video
    active_video = get_session_video(session_id)
    session_context = get_session_context(session_id)

    # Get conversation history
    raw_history = get_conversation(session_id)

    # Rewrite vague follow-up questions using history
    rewritten_query = rewrite_query(raw_history, question)

    # Save user message
    save_message(session_id, "user", question)

    # Semantic retrieval with video filter
    results = semantic_search(rewritten_query, video_id=active_video)
    documents = results["documents"][0]
    context = "\n".join(documents)

    # Convert history to LangChain message objects
    lc_history = []
    for msg in raw_history:
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    # Run LangChain chain
    answer = chain.invoke({
        "session_context": session_context or "",
        "context": context,
        "history": lc_history,
        "question": question,
    })

    # Save assistant response
    save_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "active_video": active_video,
        "rewritten_query": rewritten_query,
        "answer": answer,
        "history_length": len(raw_history),
    }