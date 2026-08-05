import os
import uuid

from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeService:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def download_audio(self, url: str):
        job_id = str(uuid.uuid4())

        job_folder = os.path.join(self.output_dir, job_id)
        os.makedirs(job_folder, exist_ok=True)

        output_template = os.path.join(job_folder, "audio.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        audio_path = os.path.join(job_folder, "audio.mp3")

        return {
            "job_id": job_id,
            "title": info.get("title"),
            "channel": info.get("uploader"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "audio_path": audio_path,
            "video_id": info.get("id"),
        }

    def get_transcript(self, video_id: str):
        try:
            transcript = YouTubeTranscriptApi().fetch(video_id)

            lyrics = []

            for line in transcript:
                lyrics.append(
                    {
                        "start": float(line.start),
                        "duration": float(line.duration),
                        "text": line.text.strip(),
                    }
                )

            return lyrics

        except Exception as e:
            # Still return [] for the common "no captions" case, but log
            # *why* — otherwise a real network/API error looks identical to
            # "this video just has no captions" and main.py can't tell them
            # apart when deciding how to warn the user.
            print(f"No transcript available for video {video_id}: {e}")
            return []

    def process(self, url: str):
        data = self.download_audio(url)

        lyrics = self.get_transcript(data["video_id"])

        data["lyrics"] = lyrics

        return data
