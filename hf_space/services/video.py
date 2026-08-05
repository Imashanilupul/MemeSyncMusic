import os
import textwrap
import subprocess
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont


class VideoService:

    def __init__(self, output_dir="outputs"):

        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    # ---------------------------------
    # Download Meme Image
    # ---------------------------------

    def download_image(self, url, output_path):

        response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})

        response.raise_for_status()

        image = Image.open(BytesIO(response.content)).convert("RGB")

        image.save(output_path, quality=95)

    # ---------------------------------
    # Create Image Frame With Lyrics
    # ---------------------------------

    def create_frame(self, image_path, lyric, output_path):

        width = 1280
        height = 720

        image = Image.open(image_path).convert("RGB")

        image.thumbnail((width, height))

        canvas = Image.new("RGB", (width, height), "black")

        x = (width - image.width) // 2
        y = (height - image.height) // 2

        canvas.paste(image, (x, y))

        draw = ImageDraw.Draw(canvas)

        # lyric background

        draw.rectangle((0, 550, width, height), fill=(0, 0, 0))

        font = ImageFont.load_default()

        wrapped_text = "\n".join(textwrap.wrap(lyric, width=45))

        draw.multiline_text(
            (width // 2, 635),
            wrapped_text,
            fill="white",
            font=font,
            anchor="mm",
            align="center",
        )

        canvas.save(output_path)

    # ---------------------------------
    # Generate Video Using FFmpeg
    # ---------------------------------

    def render(self, job_id, slides, audio_path):

        job_dir = os.path.join(self.output_dir, job_id)

        frame_dir = os.path.join(job_dir, "frames")

        os.makedirs(frame_dir, exist_ok=True)

        print("Creating frames...")

        frame_paths = []

        # Create frames

        for index, slide in enumerate(slides):

            image_path = os.path.join(frame_dir, f"image_{index}.jpg")

            frame_path = os.path.join(frame_dir, f"frame_{index}.jpg")

            self.download_image(slide["image_url"], image_path)

            self.create_frame(image_path, slide.get("text", ""), frame_path)

            frame_paths.append(frame_path)

        # ---------------------------------
        # Create FFmpeg concat file
        # ---------------------------------

        concat_file = os.path.join(job_dir, "files.txt")

        with open(concat_file, "w", encoding="utf-8") as file:

            for index, slide in enumerate(slides):

                absolute_path = os.path.abspath(frame_paths[index])

                # Windows path fix

                absolute_path = absolute_path.replace("\\", "/")

                file.write(f"file '{absolute_path}'\n")

                duration = slide.get("duration", 3)

                file.write(f"duration {duration}\n")

            # repeat final frame

            last = os.path.abspath(frame_paths[-1]).replace("\\", "/")

            file.write(f"file '{last}'\n")

        # ---------------------------------
        # FFmpeg Rendering
        # ---------------------------------

        output_video = os.path.join(job_dir, "meme_music_video.mp4")

        print("Running FFmpeg...")

        command = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,
            "-i",
            audio_path,
            "-vf",
            "format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            output_video,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:

            print(result.stderr)

            raise Exception("FFmpeg rendering failed")

        print("Video created:", output_video)

        return output_video
