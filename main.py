import yt_dlp
import json
from pathlib import Path
from qdrant_client import QdrantClient, models
import uuid
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from groq import Groq

client = QdrantClient(path="./qdrant_data")

COLLECTION_NAME = "youtube_transcripts"
model = SentenceTransformer("all-MiniLM-L6-v2")


load_dotenv()

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# playlist_url = input("Enter YouTube playlist URL: ")

# ydl_opts = {
#     "extract_flat": "in_playlist",
#     "playlist_items": "1:20",
#     "quiet": True,
#     "ignoreerrors": True
# }

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:

#     playlist_info = ydl.extract_info(
#         playlist_url,
#         download=False
#     )

#     videos = playlist_info.get("entries", [])

#     for video in videos:

#         if video is None:
#             continue

#         print({
#             "id": video.get("id"),
#             "title": video.get("title")
#         })
from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()


def get_transcript(video_id):

    try:
        transcript = ytt_api.fetch(
            video_id,
            languages=["en"]
        )

        segments = transcript.to_raw_data()

        return segments

    except Exception as e:
        print(f"Transcript extraction failed: {e}")
        return None

def save_transcript(video_id, title, segments):

    transcript_data = {
        "video_id": video_id,
        "title": title,
        "segments": segments
    }

    file_path = Path("data/transcripts") / f"{video_id}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(transcript_data, file, indent=4, ensure_ascii=False)

    print(f"Transcript saved: {file_path}")

def create_chunks(segments, chunk_size=500, chunk_overlap=100):

    chunks = []
    current_segments = []
    current_length = 0

    for segment in segments:

        text = segment["text"].strip()

        if not text:
            continue

        # Add the segment to the current chunk
        current_segments.append(segment)
        current_length += len(text)

        # Check whether chunk size has been reached
        if current_length >= chunk_size:

            chunk_text = " ".join(
                s["text"].strip() for s in current_segments
            )

            chunk = {
                "text": chunk_text,
                "start": current_segments[0]["start"],
                "end": current_segments[-1]["start"] + current_segments[-1]["duration"]
            }

            chunks.append(chunk)

            # Keep overlapping segments for the next chunk
            overlap_segments = []
            overlap_length = 0

            for s in reversed(current_segments):
                if overlap_length + len(s["text"]) > chunk_overlap:
                    break

                overlap_segments.insert(0, s)
                overlap_length += len(s["text"])

            current_segments = overlap_segments
            current_length = overlap_length

    # Save remaining segments as the final chunk
    if current_segments:

        chunk_text = " ".join(
            s["text"].strip() for s in current_segments
        )

        chunk = {
            "text": chunk_text,
            "start": current_segments[0]["start"],
            "end": current_segments[-1]["start"] + current_segments[-1]["duration"]
        }

        chunks.append(chunk)

    return chunks
def add_metadata(chunks, video_id, video_title):

    for chunk in chunks:

        chunk["video_id"] = video_id
        chunk["video_title"] = video_title

        chunk["url"] = (
            f"https://www.youtube.com/watch?v={video_id}"
            f"&t={int(chunk['start'])}s"
        )

    return chunks
def create_embeddings(chunks):
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts)
    return embeddings
def create_collection():

    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )

        print("Collection created successfully!")

    else:
        print("Collection already exists!")


def store_chunks(chunks, embeddings):

    points = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        point = models.PointStruct(
            id=str(uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"{chunk['video_id']}_{i}"
            )),
            vector=embedding.tolist(),
            payload=chunk
        )

        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"Successfully stored {len(points)} chunks!")
def generate_answer(query, results):

    context = ""

    for i, result in enumerate(results):

        context += f"""
        Source {i+1}:
        Video: {result.payload["video_title"]}
        Timestamp: {result.payload["start"]}
        Content: {result.payload["text"]}
        URL: {result.payload["url"]}
        """

    prompt = f"""
    You are a helpful assistant answering questions
    using YouTube video transcripts.

    Answer the user's question using ONLY the provided context.

    If the answer is not available in the context,
    say that you could not find the answer in the videos.

    Always include relevant video titles and timestamps
    as sources.

    Context:
    {context}

    User Question:
    {query}
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content
def search(query, top_k=3):

    # Convert the question into an embedding
    query_vector = model.encode(query).tolist()

    # Search Qdrant for similar vectors
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results
def ingest_playlist(playlist_url):

    ydl_opts = {
        "extract_flat": "in_playlist",
        "quiet": True,
        "ignoreerrors": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(
            playlist_url,
            download=False
        )

    videos = playlist_info.get("entries", [])

    print(f"\nFound {len(videos)} videos.")

    create_collection()

    total_chunks = 0

    for index, video in enumerate(videos, start=1):

        if video is None:
            continue

        video_id = video.get("id")
        video_title = video.get("title")

        print(f"\n[{index}/{len(videos)}] Processing: {video_title}")

        # 1. Extract transcript
        transcript = get_transcript(video_id)

        if not transcript:
            print("Skipping: Transcript unavailable.")
            continue
        save_transcript(video_id, video_title, transcript)

        # 2. Create chunks
        chunks = create_chunks(transcript)

        # 3. Attach video metadata
        chunks = add_metadata(
            chunks,
            video_id,
            video_title
        )

        # 4. Generate embeddings
        embeddings = create_embeddings(chunks)

        # 5. Store in Qdrant
        store_chunks(chunks, embeddings)

        total_chunks += len(chunks)

        print(f"Processed {len(chunks)} chunks.")

    print("\n===== INGESTION COMPLETE =====")
    print(f"Total videos: {len(videos)}")
    print(f"Total chunks stored: {total_chunks}")
if __name__ == "__main__":

    try:
        playlist_url = input("Enter YouTube playlist URL: ")

        ingest_playlist(playlist_url)

        print("\nYou can now ask questions about the playlist.")
        print("Type 'exit' to quit.\n")

        while True:

            user_query = input("Ask a question: ")

            if user_query.lower().strip() == "exit":
                break

            if not user_query.strip():
                continue

            results = search(user_query)

            if not results:
                print("No relevant results found.")
                continue

            answer = generate_answer(user_query, results)

            print("\n===== ANSWER =====\n")
            print(answer)

    finally:
        client.close()