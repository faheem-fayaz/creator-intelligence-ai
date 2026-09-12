from app.services.embedding_service import generate_embedding
from app.vectorstore.chroma_store import search_similar


def semantic_search(query: str, video_id=None):

    query_embedding = generate_embedding(query)

    results = search_similar(
        query_embedding=query_embedding,
        video_id=video_id
    )

    return results