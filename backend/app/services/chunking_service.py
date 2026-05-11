def chunk_transcript(segments, chunk_size=5):
    chunks = []

    current_chunk = []

    for i, segment in enumerate(segments):
        current_chunk.append(segment)

        if len(current_chunk) >= chunk_size:
            text = " ".join([s["text"] for s in current_chunk])

            chunks.append({
                "text": text,
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["start"]
            })

            current_chunk = []

    if current_chunk:
        text = " ".join([s["text"] for s in current_chunk])

        chunks.append({
            "text": text,
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["start"]
        })

    return chunks