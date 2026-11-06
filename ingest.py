from youtube_rag.ingestion import ingest_playlist
from youtube_rag.vector_store import client


def main():
    playlist_url = input("Enter YouTube playlist URL: ")
    ingest_playlist(playlist_url)


if __name__ == "__main__":
    try:
        main()
    finally:
        client.close()