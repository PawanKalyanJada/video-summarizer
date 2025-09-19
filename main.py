import streamlit as st
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from streamlit_player import st_player


# Cache the model once (efficient loading)
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


summarizer = load_summarizer()


def summarize_text(text, chunk_size=1000):
    """Split text into chunks and summarize each part with a progress bar."""
    words = text.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    summaries = []
    progress = st.progress(0)
    status = st.empty()

    for idx, chunk in enumerate(chunks, 1):
        status.text(f"Summarizing chunk {idx}/{len(chunks)} ...")
        summary = summarizer(
            chunk,
            max_length=150,
            min_length=40,
            do_sample=False
        )[0]["summary_text"]
        summaries.append(summary.strip())
        progress.progress(int((idx / len(chunks)) * 100))

    progress.empty()
    status.text("✅ Summarization completed!")
    return " ".join(summaries)


def get_transcript(video_id):
    """Fetch transcript text from YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([i["text"] for i in transcript]).strip()
    except Exception:
        return None


# Streamlit UI
st.set_page_config(page_title="YouTube Summarizer", layout="centered")
st.title("📺 YouTube Video Summarization")
st.write("Enter a YouTube video link and get an AI-generated summary of the video.")

selection = st.selectbox(
    "Choose an option:",
    ("-- Select --", "Try sample videos", "Enter your own link")
)

if selection == "Try sample videos":
    youtube_video = st.selectbox(
        "Examples:",
        (
            "-- Select --",
            "https://www.youtube.com/watch?v=Cu3R5it4cQs",
            "https://www.youtube.com/watch?v=PZEQnCaGxgw",
            "https://www.youtube.com/watch?v=TKXldNsmRaw"
        )
    )

    if youtube_video != "-- Select --":
        video_id = youtube_video.split("v=")[-1]
        state = st.empty()
        state.text("⏳ Fetching transcript...")
        text = get_transcript(video_id)

        if not text:
            state.text("❌ Transcript not available for this video.")
        else:
            state.text("⏳ Starting summarization...")
            summary = summarize_text(text)

            st.subheader("▶️ Submitted Video")
            st_player(youtube_video)

            st.subheader("📝 Summary")
            st.write(summary)


elif selection == "Enter your own link":
    youtube_video = st.text_input("Enter the YouTube link:")

    if youtube_video:
        if "youtube.com/watch" in youtube_video:
            video_id = youtube_video.split("v=")[-1].split("&")[0]
        elif "youtu.be" in youtube_video:
            video_id = youtube_video.split("/")[-1]
        else:
            video_id = None

        if video_id:
            state = st.empty()
            state.text("⏳ Fetching transcript...")
            text = get_transcript(video_id)

            if not text:
                state.text("❌ Transcript not available for this video.")
            else:
                state.text("⏳ Starting summarization...")
                summary = summarize_text(text)

                st.subheader("▶️ Submitted Video")
                st_player(youtube_video)

                st.subheader("📝 Summary")
                st.write(summary)
        else:
            st.warning("⚠️ Please enter a valid YouTube link!")


# Footer
st.markdown(
    """
    <div style="text-align:center; margin-top:40px; font-size:14px; color:gray;">
        Developed by <a href="https://www.linkedin.com/in/pawan-kalyan-9704991aa/" target="_blank">Pawan Kalyan Jada</a><br>
        📧 pawankalyanjada@gmail.com
    </div>
    """,
    unsafe_allow_html=True
)
