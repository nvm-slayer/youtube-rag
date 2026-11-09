# PlaylistIQ 🎯

### YouTube Playlist Summarizer & RAG-Based Learning Assistant

PlaylistIQ transforms YouTube videos and playlists into structured learning resources. It automatically extracts transcripts, generates AI-powered summaries, and lets users ask questions across their processed content using Retrieval-Augmented Generation (RAG).

Instead of revisiting hours of video content, users can quickly review key concepts, understand the bigger picture, and retrieve relevant information with source timestamps.

## ✨ Features

- **Single Video Processing:** Process an individual YouTube video.
- **Playlist Processing:** Process an entire playlist with a configurable limit of 1–20 videos (default: 5).
- **Automatic Transcript Extraction:** Retrieve available YouTube transcripts.
- **Video-wise Summarization:** Generate structured summaries for individual videos.
- **Playlist Summarization:** Combine individual video summaries into an overall playlist summary.
- **Timestamp-Based Retrieval:** Retrieve relevant transcript chunks with video titles and timestamps.
- **RAG-Based Question Answering:** Ask questions about processed videos and receive context-aware answers.
- **Modular Architecture:** Separate modules for transcript extraction, chunking, embeddings, vector storage, summarization, and retrieval.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | User interface |
| yt-dlp | YouTube video and playlist metadata extraction |
| youtube-transcript-api | Transcript extraction |
| Sentence Transformers | Text embeddings |
| all-MiniLM-L6-v2 | Embedding model (384 dimensions) |
| Qdrant | Local vector database |
| Groq API | LLM-powered summarization and answer generation |

## 🏗️ Architecture

PlaylistIQ follows a modular ingestion and retrieval pipeline.

### 1. Ingestion Pipeline

1. Accept a YouTube video or playlist URL.
2. Extract video metadata.
3. Retrieve available transcripts.
4. Save transcripts locally.
5. Divide transcripts into overlapping chunks.
6. Generate video-wise summaries using hierarchical summarization.
7. Generate embeddings for transcript chunks.
8. Store embeddings and associated metadata in Qdrant.
9. Generate an overall playlist summary when processing a playlist.

### 2. RAG Pipeline

1. Accept a user's question.
2. Convert the question into an embedding using Sentence Transformers.
3. Retrieve the most relevant transcript chunks from Qdrant.
4. Pass the retrieved context to the Groq LLM.
5. Generate a context-aware answer with relevant video sources and timestamps.

## 📁 Project Structure

```text
youtube-rag/
│
├── app.py
├── main.py
├── ingest.py
├── test_summarizer.py
│
├── youtube_rag/
│   ├── __init__.py
│   ├── config.py
│   ├── transcript.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── ingestion.py
│   ├── rag.py
│   └── summarizer.py
│
├── data/
│   ├── transcripts/
│   └── summaries/
│
├── qdrant_data/
│
├── .env
└── pyproject.toml
```

## ⚙️ Getting Started

### Prerequisites

- Python
- [uv](https://docs.astral.sh/uv/)
- A Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/nvm-slayer/youtube-rag.git

cd youtube-rag
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

### 4. Run the application

```bash
uv run streamlit run app.py
```

Open the local URL provided by Streamlit in your browser.
##Screenshots 
<img width="1917" height="977" alt="image" src="https://github.com/user-attachments/assets/0c0a94ea-65de-4c59-9f30-34a8ef0b37c4" /> <img width="1917" height="980" alt="image" src="https://github.com/user-attachments/assets/c6de8929-9fdf-49c2-b7af-fe9853618202" />
## 🚀 How to Use

1. Launch PlaylistIQ.
2. Select **Single Video** or **Playlist**.
3. Paste the corresponding YouTube URL.
4. For playlists, select the maximum number of videos to process.
5. Start processing and wait for transcript extraction, summarization, and indexing.
6. Explore the generated summaries.
7. Open the Ask Questions section to query your processed content.

## 📌 Current Limitations

- Transcript extraction depends on transcript availability and accessibility.
- Videos without accessible transcripts cannot be processed through the current transcript-based pipeline.
- YouTube may restrict transcript requests or temporarily block requests based on IP or usage patterns.
- Processing multiple videos can take time due to transcript extraction, LLM calls, and embedding generation.
- Groq API rate limits can affect processing speed.
- The current implementation uses local Qdrant storage.

## 🔮 Future Improvements

- RAG evaluation using retrieval and generation metrics.
- Improved retrieval strategies and chunking evaluation.
- Better handling of transcript extraction failures.
- Conversation memory for follow-up questions.
- Agentic workflows for more advanced learning assistance.

## 👨‍💻 Author

**Ishu**

- GitHub: [@nvm-slayer](https://github.com/nvm-slayer)

---

*PlaylistIQ — Know the course. Own the knowledge.*
