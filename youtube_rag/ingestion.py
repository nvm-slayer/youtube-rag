
import json
from pathlib import Path
from itertools import islice

import yt_dlp

from youtube_rag.transcript import get_transcript, save_transcript
from youtube_rag.chunking import create_chunks, add_metadata
from youtube_rag.embeddings import create_embeddings
from youtube_rag.vector_store import create_collection, store_chunks
from youtube_rag.summarizer import summarize_video, summarize_playlist


SUMMARY_DIR = Path("data/summaries")


def ingest_video(video_id, video_title):
    """Process one video through transcript, summarization and RAG indexing."""

    print(f"\nProcessing: {video_title}")

    transcript = get_transcript(video_id)

    if not transcript:
        print("Skipping: transcript unavailable")
        return None

    save_transcript(video_id, video_title, transcript)

    chunks = create_chunks(transcript)
    chunks = add_metadata(chunks, video_id, video_title)

    if not chunks:
        print("Skipping: no chunks created")
        return None

    video_summary = None

    # Generate video summary
    try:
        video_summary = summarize_video(video_title, chunks)

        summary_data = {
            "video_id": video_id,
            "title": video_title,
            "summary": video_summary,
        }

        summary_file = SUMMARY_DIR / f"{video_id}.json"

        with open(summary_file, "w", encoding="utf-8") as file:
            json.dump(
                summary_data,
                file,
                ensure_ascii=False,
                indent=4,
            )

        print("Video summary saved.")

    except Exception as e:
        print(f"Summary generation failed: {e}")

    # Generate embeddings and store in Qdrant
    embeddings = create_embeddings(chunks)
    store_chunks(chunks, embeddings)

    print(f"Stored {len(chunks)} chunks")

    return {
        "video_id": video_id,
        "title": video_title,
        "summary": video_summary,
    }


def ingest_playlist(playlist_url, max_videos=5):
    """
    Process either a single YouTube video or a playlist.

    Single videos are processed once.
    Playlists are limited to max_videos.
    """

    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    if not info:
        raise ValueError("Could not extract YouTube information.")

    # Detect single video or playlist
    entries = info.get("entries")

    if entries is not None:
        input_type = "playlist"
        videos = list(islice(entries, max(1, int(max_videos))))
        collection_title = info.get("title", "YouTube Playlist")

        print(f"\nPlaylist detected: {collection_title}")
        print(f"Processing up to {len(videos)} videos.")

    else:
        input_type = "video"
        videos = [info]
        collection_title = info.get("title", "YouTube Video")

        print(f"\nSingle video detected: {collection_title}")

    create_collection()
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    video_summaries = []
    processed_videos = 0
    failed_videos = 0

    for video in videos:
        if not video:
            continue

        video_id = video.get("id")
        video_title = video.get("title", "Unknown title")

        if not video_id:
            failed_videos += 1
            print("Skipping: video ID unavailable")
            continue

        try:
            result = ingest_video(video_id, video_title)

            if result is None:
                failed_videos += 1
                continue

            processed_videos += 1

            if result.get("summary"):
                video_summaries.append(result)

        except Exception as e:
            failed_videos += 1
            print(f"Video processing failed: {e}")

    # Generate collection summary
    if video_summaries:
        try:
            if input_type == "playlist":
                final_summary = summarize_playlist(video_summaries)
            else:
                # Reuse the video summary; no extra LLM call.
                final_summary = video_summaries[0]["summary"]

            summary_data = {
                "playlist_title": collection_title,
                "videos_summarized": len(video_summaries),
                "summary": final_summary,
            }

            summary_file = SUMMARY_DIR / "playlist_summary.json"

            with open(summary_file, "w", encoding="utf-8") as file:
                json.dump(
                    summary_data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            print("\nCollection summary saved.")

        except Exception as e:
            print(f"Collection summary generation failed: {e}")

    else:
        print("\nNo video summaries generated.")

    print(f"\n{input_type.capitalize()} ingestion finished!")

    return {
        "processed_videos": processed_videos,
        "failed_videos": failed_videos,
        "summaries_generated": len(video_summaries),
        "input_type": input_type,
        "collection_title": collection_title,
    }
