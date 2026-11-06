from youtube_rag.ingestion import ingest_playlist
from youtube_rag.rag import search, generate_answer
from youtube_rag.vector_store import client


def main():
    print("YouTube RAG Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask a question: ")

        if query.lower() == "exit":
            break

        results = search(query)
        answer = generate_answer(query, results)

        print("\nAnswer:", answer)

        for result in results:
            payload = result.payload
            print(f"\nSource: {payload['video_title']}")
            print(f"Timestamp: {payload['url']}")

        print("\n" + "-" * 50)


if __name__ == "__main__":
    try:
        main()
    finally:
        client.close()