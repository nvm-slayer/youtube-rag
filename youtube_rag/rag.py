from groq import Groq

from youtube_rag.config import GROQ_API_KEY, GROQ_MODEL
from youtube_rag.embeddings import create_query_embedding
from youtube_rag.vector_store import search_vectors

groq_client = Groq(api_key=GROQ_API_KEY)


def search(query, top_k=3):
    query_vector = create_query_embedding(query)
    return search_vectors(query_vector, top_k)


def generate_answer(query, results):
    if not results:
        return "I couldn't find relevant information in the course videos."

    context = ""

    for result in results:
        payload = result.payload

        context += f"""
Video: {payload['video_title']}
Timestamp: {payload['start']}
URL: {payload['url']}
Content: {payload['text']}

"""

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI Engineering course assistant. "
                    "Answer using only the provided video context. "
                    "If the answer is not present, say so. "
                    "Be clear and beginner-friendly."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\nContext:\n{context}",
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content