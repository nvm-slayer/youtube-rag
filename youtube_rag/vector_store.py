import uuid

from qdrant_client import QdrantClient, models

from youtube_rag.config import QDRANT_PATH, COLLECTION_NAME, VECTOR_SIZE

client = QdrantClient(path=QDRANT_PATH)


def create_collection():
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )
print("Qdrant storage:", QDRANT_PATH)
print("Collections:", client.get_collections().collections)

def store_chunks(chunks, embeddings):
    points = []

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_DNS,
                f"{chunk['video_id']}_{index}",
            )
        )

        points.append(
            models.PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload=chunk,
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )


def search_vectors(query_vector, top_k=3):
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results