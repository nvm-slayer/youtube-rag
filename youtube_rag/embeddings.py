from sentence_transformers import SentenceTransformer

from youtube_rag.config import EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)


def create_embeddings(chunks):
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(texts)

    return embeddings


def create_query_embedding(query):
    return model.encode(query).tolist()