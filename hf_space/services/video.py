import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips


class VideoService:

    def __init__(self, output_dir="outputs"):

        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------------
    # Create Meme Frame
    # -----------------------------

    def create_frame(self, meme_url, lyric, output_path):

        width = 1280
        height = 720

        img = Image.open(meme_url).convert("RGB")

        img.thumbnail((width, height))

        canvas = Image.new("RGB", (width, height), "black")

        x = (width - img.width) // 2

        y = (height - img.height) // 2

        canvas.paste(img, (x, y))

        draw = ImageDraw.Draw(canvas)

        # dark subtitle background

        draw.rectangle((0, height - 170, width, height), fill=(0, 0, 0))

        font = ImageFont.load_default()

        lines = textwrap.wrap(lyric, width=45)

        draw.multiline_text(
            (width // 2, height - 120),
            "\n".join(lines),
            font=font,
            fill="white",
            anchor="mm",
            align="center",
        )

        canvas.save(output_path)

    # -----------------------------
    # Generate Video
    # -----------------------------

    def render(self, job_id, slides, audio_path):

        job_dir = os.path.join(self.output_dir, job_id)

        os.makedirs(job_dir, exist_ok=True)

        clips = []

        for index, slide in enumerate(slides):

            frame_path = os.path.join(job_dir, f"frame_{index}.jpg")

            self.create_frame(slide["image_url"], slide["text"], frame_path)

            duration = slide.get("duration", 3)

            clip = ImageClip(frame_path).with_duration(duration)

            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")

        audio = AudioFileClip(audio_path)

        video = video.with_audio(audio)

        output = os.path.join(job_dir, "meme_music_video.mp4")

        video.write_videofile(output, fps=30, codec="libx264", audio_codec="aac")

        return output
