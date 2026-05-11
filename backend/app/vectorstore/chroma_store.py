import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="video_transcripts"
)


def store_chunk(chunk_id, text, embedding, metadata):

    collection.add(
        ids=[chunk_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )


def search_similar(query_embedding, top_k=5, video_id=None):

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k
    }

    if video_id:
        query_params["where"] = {
            "video_id": video_id
        }

    results = collection.query(**query_params)

    return results