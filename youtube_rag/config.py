
import os
from dotenv import load_dotenv

load_dotenv()

# Groq configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"

# Embedding configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

# Qdrant configuration
QDRANT_PATH = "./qdrant_data"
COLLECTION_NAME = "youtube_transcripts"

# Transcript storage
TRANSCRIPT_DIR = "data/transcripts"
