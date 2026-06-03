import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="video_transcripts"
)

print(
    "COLLECTION COUNT:",
    collection.count()
)


def store_chunk(
    chunk_id,
    text,
    embedding,
    metadata
):

    collection.add(
        ids=[chunk_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )

    print(
        "Stored chunk:",
        chunk_id
    )


def search_similar(
    query_embedding,
    top_k=5,
    video_id=None
):

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k
    }

    if video_id:

        query_params["where"] = {
            "video_id": video_id
        }

    print(
        "SEARCH VIDEO ID:",
        video_id
    )

    results = collection.query(
        **query_params
    )

    print(
        "RESULT COUNT:",
        len(results.get("documents", [[]])[0])
    )

    return results