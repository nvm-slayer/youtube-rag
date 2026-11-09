
import json
from pathlib import Path

import yt_dlp

from youtube_rag.transcript import get_transcript, save_transcript
from youtube_rag.chunking import create_chunks, add_metadata
from youtube_rag.embeddings import create_embeddings
from youtube_rag.vector_store import create_collection, store_chunks
from youtube_rag.summarizer import summarize_video, summarize_playlist


SUMMARY_DIR = Path("data/summaries")


def ingest_playlist(playlist_url):
    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist = ydl.extract_info(playlist_url, download=False)

    entries = playlist.get("entries", [])
    playlist_title = playlist.get("title", "YouTube Playlist")

    create_collection()

    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    video_summaries = []
    processed_videos = 0
    failed_videos = 0

    for video in entries:
        if not video:
            continue

        video_id = video.get("id")
        video_title = video.get("title", "Unknown title")

        print(f"\nProcessing: {video_title}")

        transcript = get_transcript(video_id)

        if not transcript:
            failed_videos += 1
            print("Skipping: transcript unavailable")
            continue

        save_transcript(video_id, video_title, transcript)

        chunks = create_chunks(transcript)
        chunks = add_metadata(chunks, video_id, video_title)

        if not chunks:
            failed_videos += 1
            print("Skipping: no chunks created")
            continue

        # Generate video summary
        try:
            summary = summarize_video(video_title, chunks)

            video_summaries.append({
                "video_id": video_id,
                "title": video_title,
                "summary": summary,
            })

            summary_file = SUMMARY_DIR / f"{video_id}.json"

            with open(summary_file, "w", encoding="utf-8") as file:
                json.dump(
                    video_summaries[-1],
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
        processed_videos += 1
        print(f"Stored {len(chunks)} chunks")

    # Generate overall playlist summary
    if video_summaries:
        try:
            playlist_summary = summarize_playlist(video_summaries)

            summary_data = {
                "playlist_title": playlist_title,
                "videos_summarized": len(video_summaries),
                "summary": playlist_summary,
            }

            summary_file = SUMMARY_DIR / "playlist_summary.json"

            with open(summary_file, "w", encoding="utf-8") as file:
                json.dump(
                    summary_data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            print("\nPlaylist summary saved.")

        except Exception as e:
            print(f"Playlist summary generation failed: {e}")
    else:
        print("\nNo video summaries generated.")

    print("\nPlaylist ingestion finished!")

    return {
    "processed_videos": processed_videos,
    "failed_videos": failed_videos,
    "summaries_generated": len(video_summaries),
}
