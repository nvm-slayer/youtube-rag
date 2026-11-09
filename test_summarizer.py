
import json
from pathlib import Path

from youtube_rag.chunking import create_chunks
from youtube_rag.summarizer import summarize_video


transcript_dir = Path("data/transcripts")

transcript_files = list(transcript_dir.glob("*.json"))

if not transcript_files:
    print("No saved transcripts found.")
    raise SystemExit

# Pick an existing transcript
file_path = transcript_files[0]

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

video_title = data["title"]
segments = data["segments"]

# Create chunks from the saved transcript
chunks = create_chunks(segments)

print(f"Testing summarizer: {video_title}")
print("Generating summary...\n")

summary = summarize_video(video_title, chunks)

print("VIDEO SUMMARY")
print("=" * 50)
print(summary)
