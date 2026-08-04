import os
import shutil
import subprocess
import tempfile
import textwrap
from io import BytesIO
from pathlib import Path
from typing import Any
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image, ImageDraw, ImageFont


class VideoService:
    def __init__(self, upload_root: str = "uploads"):
        self.upload_root = upload_root
        os.makedirs(self.upload_root, exist_ok=True)
        self._font = ImageFont.load_default()

    def render(
        self,
        job_id: str,
        slides: list[dict[str, Any]],
        source: str = "youtube",
        audio_file: str | None = None,
    ) -> str:
        if not slides:
            raise ValueError("No slides were generated for the video.")

        output_dir = os.path.join(self.upload_root, job_id)
        os.makedirs(output_dir, exist_ok=True)

        audio_path = self.resolve_audio_path(job_id, source, audio_file)
        if not audio_path or not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Audio file not found for job {job_id}")

        temp_dir = tempfile.mkdtemp(prefix=f"{job_id}_frames_", dir=output_dir)
        output_path = os.path.join(output_dir, "combined.mp4")

        try:
            # Pre-fetch all slide images concurrently instead of
            # sequentially blocking inside the render loop.
            images = self._prefetch_images(slides)

            concat_lines: list[str] = []
            last_abs_path: str | None = None

            for i, (slide, image) in enumerate(zip(slides, images)):
                duration = max(float(slide.get("duration") or 2), 0.2)
                frame_path = os.path.join(temp_dir, f"slide_{i:04d}.png")
                self._write_slide_frame(slide, image, frame_path)

                # ffmpeg's concat demuxer resolves relative paths in the
                # list relative to the concat.txt file's own directory,
                # which double-prefixes an already-relative frame_path.
                # Use absolute, forward-slashed paths to avoid that
                # (also needed for correct parsing on Windows).
                abs_path = os.path.abspath(frame_path).replace("\\", "/")
                concat_lines.append(f"file '{abs_path}'")
                concat_lines.append(f"duration {duration}")
                last_abs_path = abs_path

            # The concat demuxer ignores duration on the final entry
            # unless the file is repeated once more without a duration.
            if last_abs_path:
                concat_lines.append(f"file '{last_abs_path}'")

            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, "w") as f:
                f.write("\n".join(concat_lines))

            ffmpeg_command = [
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
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-threads",
                "0",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                output_path,
            ]

            completed = subprocess.run(
                ffmpeg_command,
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                stderr = (
                    completed.stderr.strip()
                    or completed.stdout.strip()
                    or "ffmpeg failed"
                )
                raise RuntimeError(stderr)

            return output_path
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def resolve_audio_path(
        self, job_id: str, source: str, audio_file: str | None
    ) -> str | None:
        if source == "youtube":
            youtube_path = os.path.join(self.upload_root, job_id, "audio.mp3")
            if os.path.isfile(youtube_path):
                return youtube_path
            return None

        if audio_file:
            uploaded_path = os.path.join(self.upload_root, audio_file)
            if os.path.isfile(uploaded_path):
                return uploaded_path

        direct_path = os.path.join(self.upload_root, f"{job_id}.mp3")
        if os.path.isfile(direct_path):
            return direct_path

        return None

    def _prefetch_images(
        self, slides: list[dict[str, Any]]
    ) -> list[Image.Image | None]:
        urls = [slide.get("image_url") for slide in slides]
        with ThreadPoolExecutor(max_workers=8) as pool:
            return list(pool.map(self._load_image, urls))

    def _write_slide_frame(
        self,
        slide: dict[str, Any],
        image: Image.Image | None,
        output_path: str,
    ) -> None:
        width, height = 1280, 720
        base = Image.new("RGB", (width, height), (12, 12, 12))

        if image is not None:
            source_width, source_height = image.size
            source_ratio = source_width / source_height if source_height else 1
            target_ratio = width / height

            if source_ratio > target_ratio:
                draw_width = int(width * 0.82)
                draw_height = int(draw_width / source_ratio)
            else:
                draw_height = int(height * 0.82)
                draw_width = int(draw_height * source_ratio)

            resized = image.resize((draw_width, draw_height), Image.LANCZOS)
            x = (width - draw_width) // 2
            y = (height - draw_height) // 2
            base.paste(resized, (x, y))

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 155))
        base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")

        draw = ImageDraw.Draw(base)
        text = str(slide.get("text") or "").strip()
        lines = textwrap.wrap(text, width=28) if text else ["No lyrics available"]
        draw.multiline_text(
            (width // 2, height - 140),
            "\n".join(lines),
            fill="white",
            font=self._font,
            anchor="mm",
            align="center",
        )

        base.save(output_path)

    def _load_image(self, image_url: str | None) -> Image.Image | None:
        if not image_url:
            return None

        try:
            response = requests.get(
                image_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception:
            return None
