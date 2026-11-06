from qdrant_client import QdrantClient
from youtube_rag.config import QDRANT_PATH, COLLECTION_NAME

client = QdrantClient(path=QDRANT_PATH)

try:
    print("Database path:", QDRANT_PATH)

    collections = client.get_collections().collections
    print("Before deletion:", [c.name for c in collections])

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)
        print("Delete request completed.")
    else:
        print("Collection does not exist.")

    collections = client.get_collections().collections
    print("After deletion:", [c.name for c in collections])

finally:
    client.close()