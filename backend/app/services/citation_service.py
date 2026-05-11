def format_timestamp(seconds):

    minutes = int(seconds // 60)

    remaining_seconds = int(seconds % 60)

    return f"{minutes:02}:{remaining_seconds:02}"


def build_citations(results):

    citations = []

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    for text, metadata in zip(
        documents,
        metadatas
    ):

        start = metadata.get("start", 0)

        end = metadata.get("end", 0)

        citation = (
            f"[{format_timestamp(start)}"
            f"-"
            f"{format_timestamp(end)}]"
        )

        citations.append({
            "citation": citation,
            "text": text,
            "video_id": metadata.get("video_id")
        })

    return citations