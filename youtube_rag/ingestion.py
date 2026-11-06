import yt_dlp

from youtube_rag.transcript import get_transcript, save_transcript
from youtube_rag.chunking import create_chunks, add_metadata
from youtube_rag.embeddings import create_embeddings
from youtube_rag.vector_store import create_collection, store_chunks


def ingest_playlist(playlist_url):
    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist = ydl.extract_info(playlist_url, download=False)

    entries = playlist.get("entries", [])
    create_collection()

    for video in entries:
        if not video:
            continue

        video_id = video.get("id")
        video_title = video.get("title", "Unknown title")

        print(f"\nProcessing: {video_title}")

        transcript = get_transcript(video_id)

        if not transcript:
            print("Skipping: transcript unavailable")
            continue

        save_transcript(video_id, video_title, transcript)

        chunks = create_chunks(transcript)
        chunks = add_metadata(chunks, video_id, video_title)

        if not chunks:
            continue

        embeddings = create_embeddings(chunks)
        store_chunks(chunks, embeddings)

        print(f"Stored {len(chunks)} chunks")

    print("\nPlaylist ingestion complete!")