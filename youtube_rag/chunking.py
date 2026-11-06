def create_chunks(segments, chunk_size=500, chunk_overlap=100):
    chunks = []
    current_chunk = []
    current_length = 0

    for segment in segments:
        text = segment["text"]
        current_chunk.append(segment)
        current_length += len(text)

        if current_length >= chunk_size:
            chunk_text = " ".join(item["text"] for item in current_chunk)

            chunks.append({
                "text": chunk_text,
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["start"] + current_chunk[-1]["duration"],
            })

            overlap = []
            overlap_length = 0

            for item in reversed(current_chunk):
                if overlap_length + len(item["text"]) > chunk_overlap:
                    break
                overlap.insert(0, item)
                overlap_length += len(item["text"])

            current_chunk = overlap
            current_length = overlap_length

    if current_chunk:
        chunks.append({
            "text": " ".join(item["text"] for item in current_chunk),
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["start"] + current_chunk[-1]["duration"],
        })

    return chunks


def add_metadata(chunks, video_id, video_title):
    for chunk in chunks:
        chunk["video_id"] = video_id
        chunk["video_title"] = video_title
        chunk["url"] = f"https://www.youtube.com/watch?v={video_id}&t={int(chunk['start'])}s"

    return chunks