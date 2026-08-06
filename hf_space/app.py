import os
import gradio as gr

from services.youtube import YouTubeService
from services.lyrics import LyricsService
from services.meme import MemeService
from services.video import VideoService
from services.audio import AudioService

os.makedirs("outputs", exist_ok=True)

youtube = YouTubeService()
lyrics_service = LyricsService()
meme_service = MemeService()
video_service = VideoService()
audio_service = AudioService()

# Generic "One Does Not Simply" template — used whenever a lyric line has no
# text (instrumental/gap filler) or no meme match was found, so we never
# drop a slide (and its duration) just because matching failed.
DEFAULT_FALLBACK_IMAGE = "https://i.imgflip.com/1bij.jpg"


def fill_gaps(lyrics, total_duration, max_gap=1.5):
    """
    Insert filler slides for any stretch of audio that isn't covered by a
    caption line (intros, instrumental breaks, missing auto-captions, the
    outro, etc.), and pad the end if captions finish before the audio does.

    Without this, total slide duration only ever reflects what YouTube's
    transcript happened to cover — which is very often less than the real
    track length — and that shortfall is what caused the video to render
    shorter than the audio and drift out of sync.
    """
    filled = []
    cursor = 0.0

    for line in lyrics:
        gap = line["start"] - cursor
        if gap > max_gap:
            filled.append({"start": cursor, "duration": gap, "text": ""})
        filled.append(line)
        cursor = line["start"] + line["duration"]

    trailing_gap = total_duration - cursor
    if trailing_gap > max_gap:
        filled.append({"start": cursor, "duration": trailing_gap, "text": ""})

    return filled


def process_music(youtube_url):
    try:
        data = youtube.process(youtube_url)

        audio_path = data["audio_path"]
        raw_lyrics = data["lyrics"]

        if not raw_lyrics:
            raise gr.Error(
                "No captions/transcript were found for this video, so lyrics "
                "can't be synced to memes. Try a different video with "
                "captions enabled."
            )

        # Audio duration is now the single source of truth for how long the
        # final video should be — everything else is built to match it,
        # instead of ffmpeg's -shortest silently deciding it for us.
        true_duration = audio_service.analyze(audio_path)["duration"]

        lyrics = lyrics_service.process(raw_lyrics)
        lyrics = fill_gaps(lyrics, true_duration)

        slides = []
        for lyric in lyrics:
            text = lyric["text"]

            if text:
                meme = meme_service.best_meme(text)
                image_url = meme["image_url"] if meme else DEFAULT_FALLBACK_IMAGE
            else:
                image_url = DEFAULT_FALLBACK_IMAGE

            # Every lyric-derived slide is kept regardless of match success,
            # so its duration is never silently dropped from the timeline.
            slides.append(
                {
                    "image_url": image_url,
                    "text": text,
                    "duration": lyric["duration"],
                }
            )

        total_slide_duration = sum(s["duration"] for s in slides)
        if abs(total_slide_duration - true_duration) > 1.0:
            print(
                f"WARNING: slide duration ({total_slide_duration:.2f}s) "
                f"still diverges from audio duration ({true_duration:.2f}s)"
            )

        video_path = video_service.render(
            job_id=data["job_id"],
            slides=slides,
            audio_path=audio_path,
            total_duration=true_duration,
        )

        return video_path

    except gr.Error:
        raise
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
