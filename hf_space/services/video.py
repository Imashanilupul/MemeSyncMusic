import os
import textwrap
import subprocess
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

# Cap on downloaded meme images to avoid unbounded memory use from a
# malicious or oversized URL before PIL ever validates it's an image.
MAX_IMAGE_BYTES = 15 * 1024 * 1024  # 15MB


class VideoService:

    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # ---------------------------------
    # Download Meme Image
    # ---------------------------------

    def download_image(self, url, output_path):

        response = requests.get(
            url, timeout=30, headers={"User-Agent": "Mozilla/5.0"}, stream=True
        )
        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_IMAGE_BYTES:
            raise ValueError(f"Image at {url} exceeds {MAX_IMAGE_BYTES} byte limit")

        buffer = BytesIO()
        downloaded = 0

        for chunk in response.iter_content(chunk_size=8192):
            downloaded += len(chunk)
            if downloaded > MAX_IMAGE_BYTES:
                raise ValueError(
                    f"Image at {url} exceeded {MAX_IMAGE_BYTES} byte limit while streaming"
                )
            buffer.write(chunk)

        buffer.seek(0)
        image = Image.open(buffer).convert("RGB")
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

        # Skip the caption bar entirely for filler slides (empty text) —
        # instrumental sections shouldn't show a blank black caption strip.
        if lyric:
            draw = ImageDraw.Draw(canvas)

            draw.rectangle((0, 550, width, height), fill=(0, 0, 0))

            try:
                # A real TTF renders far more legibly at this size than the
                # tiny bitmap default font.
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32
                )
            except OSError:
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

    def render(self, job_id, slides, audio_path, total_duration=None):

        if not slides:
            raise ValueError(
                "No slides were generated for this video — check that the "
                "transcript and meme matching produced at least one slide."
            )

        job_dir = os.path.join(self.output_dir, job_id)

        frame_dir = os.path.join(job_dir, "frames")

        os.makedirs(frame_dir, exist_ok=True)

        print("Creating frames...")

        frame_paths = []

        # Create frames — slides whose image fails to download are skipped
        # (with a logged reason) rather than crashing the whole render.
        for index, slide in enumerate(slides):

            image_path = os.path.join(frame_dir, f"image_{index}.jpg")
            frame_path = os.path.join(frame_dir, f"frame_{index}.jpg")

            try:
                self.download_image(slide["image_url"], image_path)
            except Exception as e:
                print(f"Skipping slide {index}: failed to download image ({e})")
                continue

            self.create_frame(image_path, slide.get("text", ""), frame_path)

            frame_paths.append((frame_path, slide.get("duration", 3)))

        if not frame_paths:
            raise ValueError("All slide images failed to download — nothing to render.")

        # ---------------------------------
        # Create FFmpeg concat file
        # ---------------------------------

        concat_file = os.path.join(job_dir, "files.txt")

        with open(concat_file, "w", encoding="utf-8") as file:

            for frame_path, duration in frame_paths:

                absolute_path = os.path.abspath(frame_path)

                # Windows path fix
                absolute_path = absolute_path.replace("\\", "/")

                file.write(f"file '{absolute_path}'\n")
                file.write(f"duration {duration}\n")

            # repeat final frame (required by the ffmpeg concat demuxer,
            # which otherwise drops the last entry's duration)
            last = os.path.abspath(frame_paths[-1][0]).replace("\\", "/")
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
        ]

        # Slide durations are now built (in main.py's fill_gaps) to sum to
        # the true audio duration, so -shortest is a safety net for rounding
        # drift rather than the thing deciding the video's length. Pinning
        # -t explicitly makes that intent obvious instead of implicit.
        if total_duration:
            command += ["-t", str(total_duration)]

        command += ["-shortest", output_video]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:

            print(result.stderr)

            raise Exception("FFmpeg rendering failed")

        print("Video created:", output_video)

        return output_video
