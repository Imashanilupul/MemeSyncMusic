import gradio as gr
import os

from services.youtube import YouTubeService
from services.lyrics import LyricsService
from services.meme import MemeService
from services.video import VideoService

os.makedirs("outputs", exist_ok=True)

youtube = YouTubeService()
lyrics_service = LyricsService()
meme_service = MemeService()
video_service = VideoService()


def process_music(youtube_url):
    try:

        # Download audio + lyrics
        data = youtube.process(youtube_url)

        audio_path = data["audio_path"]
        lyrics = data["lyrics"]

        # Clean/process lyrics
        lyrics = lyrics_service.process(lyrics)

        # Get memes
        slides = []

        for lyric in lyrics:
            meme = meme_service.best_meme(lyric["text"])

            if meme:
                slides.append(
                    {
                        "image_url": meme["image_url"],
                        "text": lyric["text"],
                        "duration": lyric["duration"],
                    }
                )

        # Create video
        video_path = video_service.render(
            job_id=data["job_id"], slides=slides, audio_path=audio_path
        )

        return video_path

    except Exception as e:
        raise gr.Error(str(e))


demo = gr.Interface(
    fn=process_music,
    inputs=gr.Textbox(
        label="YouTube Music Link",
        placeholder="Paste YouTube song URL",
    ),
    outputs=gr.Video(label="Generated Meme Music Video"),
    title="🎵 MemeSyncMusic",
    description="""
Turn any English YouTube song into a meme-style music video.

✔ Downloads the audio
✔ Extracts lyrics
✔ Matches memes
✔ Generates a synchronized video

Currently supports English songs only.
More languages coming soon!
""",
)

demo.launch()
