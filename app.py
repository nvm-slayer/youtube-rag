import json
from pathlib import Path

import streamlit as st

from youtube_rag.rag import search, generate_answer
from youtube_rag.ingestion import ingest_playlist


# ---------- CONFIGURATION ----------

st.set_page_config(
    page_title="PlaylistIQ | The Learning Arena",
    page_icon="🎓",
    layout="wide",
)

SUMMARY_DIR = Path("data/summaries")


# ---------- DATA HELPERS ----------
# These functions must be defined before the tabs call them.

def load_playlist_summary():
    summary_file = SUMMARY_DIR / "playlist_summary.json"

    if not summary_file.exists():
        return None

    with open(summary_file, "r", encoding="utf-8") as file:
        return json.load(file)


def load_video_summaries():
    if not SUMMARY_DIR.exists():
        return []

    summaries = []

    for file_path in SUMMARY_DIR.glob("*.json"):
        if file_path.name == "playlist_summary.json":
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            summaries.append(json.load(file))

    return summaries


# ---------- CUSTOM STYLING ----------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --red: #e32630;
        --black: #09090b;
        --panel: #151518;
        --muted: #a1a1aa;
    }

    .stApp {
        background: var(--black);
        color: #f4f4f5;
        font-family: 'Inter', sans-serif;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Barlow Condensed', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    p, label, input, textarea {
        font-family: 'Inter', sans-serif;
    }

    .brand {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: 1px;
    }

    .brand span {
        color: var(--red);
    }

    .hero {
        border-top: 4px solid var(--red);
        border-bottom: 1px solid #333;
        padding: 2.5rem 0 2rem 0;
        margin: 1rem 0 2rem 0;
    }

    .eyebrow {
        color: var(--red);
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .hero-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: clamp(3.5rem, 8vw, 6.5rem);
        font-weight: 900;
        line-height: 0.88;
        text-transform: uppercase;
        margin: 1rem 0;
        letter-spacing: -1px;
    }

    .hero-title span {
        color: var(--red);
    }

    .hero-subtitle {
        color: var(--muted);
        font-size: 0.95rem;
        max-width: 550px;
        line-height: 1.7;
    }

    .section-label {
        color: var(--red);
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }

    .feature-panel {
        background: var(--panel);
        border: 1px solid #333;
        border-left: 3px solid var(--red);
        padding: 1.5rem;
        min-height: 165px;
        margin-bottom: 1rem;
    }

    .feature-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        text-transform: uppercase;
        margin: 0.4rem 0;
    }

    .feature-description {
        color: var(--muted);
        font-size: 0.85rem;
        line-height: 1.6;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #383838;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #a1a1aa;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 1px;
        padding: 1rem 0.2rem;
    }

    .stTabs [aria-selected="true"] {
        color: white !important;
        border-bottom: 3px solid var(--red) !important;
    }

    .stTextInput input, .stTextArea textarea {
        background: #151518 !important;
        color: white !important;
        border: 1px solid #383838 !important;
        border-radius: 3px !important;
    }

    .stButton button {
        background: var(--red);
        color: white;
        border: none;
        border-radius: 2px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0.6rem 1.2rem;
    }

    .stButton button:hover {
        background: #b91520;
        color: white;
        border: none;
    }

    hr {
        border-color: #333;
    }

    .footer {
        border-top: 1px solid #333;
        margin-top: 3rem;
        padding-top: 1rem;
        color: #71717a;
        font-size: 0.7rem;
        letter-spacing: 1px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- HEADER ----------

st.markdown(
    """
    <div class="brand">PLAYLIST<span>IQ</span></div>

    <div class="hero">
        <div class="eyebrow">Your next main event starts here</div>
        <div class="hero-title">
            KNOW THE COURSE.<br>
            <span>OWN THE KNOWLEDGE.</span>
        </div>
        <div class="hero-subtitle">
            Turn YouTube playlists into structured learning.
            Get summaries, revisit important concepts and
            ask questions across your entire course.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- FEATURE OVERVIEW ----------

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="feature-panel">
            <div class="section-label">01 / THE BIG PICTURE</div>
            <div class="feature-title">Playlist Summary</div>
            <div class="feature-description">
                Get the complete breakdown of your course,
                its major topics and learning sequence.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-panel">
            <div class="section-label">02 / VIDEO BREAKDOWN</div>
            <div class="feature-title">Individual Summaries</div>
            <div class="feature-description">
                Review every video through structured summaries
                and important takeaways.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- PLAYLIST INGESTION ----------

st.markdown("## ENTER THE ARENA")
st.caption("Load a YouTube playlist to build your learning workspace.")

playlist_url = st.text_input(
    "YOUTUBE PLAYLIST URL",
    placeholder="https://www.youtube.com/playlist?list=...",
)

if st.button("PROCESS PLAYLIST", use_container_width=True):
    if not playlist_url.strip():
        st.warning("Please enter a playlist URL.")
    else:
        try:
            with st.spinner(
                "Building your learning workspace. This may take a while..."
            ):
                result = ingest_playlist(playlist_url)

            if result and result.get("processed_videos", 0) > 0:
                st.success(
                    f"Successfully indexed {result['processed_videos']} videos!"
                )
                st.info(
                    f"Summaries generated: {result.get('summaries_generated', 0)} | "
                    f"Videos skipped: {result.get('failed_videos', 0)}"
                )
                st.rerun()
            else:
                st.error(
                    "No videos were indexed. Check transcript availability "
                    "or YouTube access."
                )

        except Exception as e:
            st.error(f"Playlist processing failed: {e}")


# ---------- MAIN WORKSPACE ----------

st.markdown(
    """
    <div class="section-label">03 / ENTER THE LEARNING ARENA</div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(
    [
        "Playlist Summary",
        "Video Summaries",
        "Ask Questions",
    ]
)

with tab1:
    st.markdown("## The complete course breakdown")

    data = load_playlist_summary()

    if data:
        st.caption(data.get("playlist_title", "Your playlist"))
        st.markdown(data.get("summary", "No summary text found."))
        st.divider()
        st.caption(
            f"Videos summarized: {data.get('videos_summarized', 0)}"
        )
    else:
        st.warning(
            "No playlist summary found. Please ingest a playlist first."
        )


with tab2:
    st.markdown("## Inside the playlist")
    st.caption("Explore the key concepts from individual videos.")

    video_summaries = load_video_summaries()

    if video_summaries:
        for index, video in enumerate(video_summaries, start=1):
            with st.expander(f"{index}. {video.get('title', 'Untitled video')}"):
                st.markdown(video.get("summary", "No summary available."))

                video_id = video.get("video_id")
                if video_id:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    st.markdown(f"[Watch video]({video_url})")
    else:
        st.warning(
            "No video summaries found. Please ingest a playlist first."
        )


with tab3:
    st.markdown("## Step into the knowledge arena")
    st.caption("Ask questions and get answers grounded in course videos.")

    question = st.text_input(
        "YOUR QUESTION",
        placeholder="What are the key concepts covered in this course?",
    )

    if st.button("ASK PLAYLISTIQ", use_container_width=True):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner("Searching your playlist..."):
                    results = search(question)
                    answer = generate_answer(question, results)

                st.markdown("### THE ANSWER")
                st.markdown(answer)

                if results:
                    st.markdown("### SOURCES")

                    for result in results:
                        payload = result.payload
                        timestamp = int(payload["start"])
                        minutes = timestamp // 60
                        seconds = timestamp % 60

                        st.markdown(
                            f"- [{payload['video_title']} "
                            f"— {minutes}:{seconds:02d}]"
                            f"({payload['url']})"
                        )

            except Exception as e:
                st.error(f"Something went wrong: {e}")


# ---------- FOOTER ----------

st.markdown(
    """
    <div class="footer">
        PLAYLISTIQ &nbsp; • &nbsp; BUILT TO LEARN. BUILT TO LAST.
    </div>
    """,
    unsafe_allow_html=True,
)
