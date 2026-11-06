import json
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

from youtube_rag.config import TRANSCRIPT_DIR

ytt_api = YouTubeTranscriptApi()


def get_transcript(video_id):
    try:
        transcript = ytt_api.fetch(video_id, languages=["en","hi"])
        return transcript.to_raw_data()

    except Exception as e:
        print(f"Could not fetch transcript for {video_id}: {e}")
        return None


def save_transcript(video_id, title, segments):
    transcript_dir = Path(TRANSCRIPT_DIR)
    transcript_dir.mkdir(parents=True, exist_ok=True)

    file_path = transcript_dir / f"{video_id}.json"

    data = {
        "video_id": video_id,
        "title": title,
        "segments": segments,
    }

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Transcript saved: {file_path}")