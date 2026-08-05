import gradio as gr
import os

from services.youtube import download_youtube_audio
from services.lyrics import extract_lyrics
from services.meme import generate_memes
from services.video import create_video

os.makedirs("outputs", exist_ok=True)


def process_music(youtube_url):

    try:

        # Step 1: Download music

        audio_path = download_youtube_audio(youtube_url)

        # Step 2: Get lyrics

        lyrics = extract_lyrics(youtube_url)

        # Step 3: Find memes

        memes = generate_memes(lyrics)

        # Step 4: Generate video

        video_path = create_video(audio_path, lyrics, memes)

        return video_path

    except Exception as e:

        return f"Error: {str(e)}"


demo = gr.Interface(
    fn=process_music,
    inputs=gr.Textbox(label="YouTube Music Link", placeholder="Paste YouTube song URL"),
    outputs=gr.Video(label="Generated Meme Music Video"),
    title="MemeSyncMusic 🎵😂",
    description="""
    Transform songs into meme-style music videos.

    Currently supports English songs only.

    More languages coming soon!
    """,
)


demo.launch()
