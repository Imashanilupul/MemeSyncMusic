import json
import os
import re
import shutil
import uuid

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeService:

    def extract_video_id(self, url: str):

        patterns = [
            r"v=([a-zA-Z0-9_-]{11})",
            r"youtu\.be/([a-zA-Z0-9_-]{11})",
            r"shorts/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)

            if match:
                return match.group(1)

        return None

    def process(self, url: str):

        job_id = str(uuid.uuid4())

        output_dir = os.path.join("uploads", job_id)
        os.makedirs(output_dir, exist_ok=True)

        ##################################################
        # Download MP3
        ##################################################

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            downloaded = ydl.prepare_filename(info)

        audio_path = os.path.splitext(downloaded)[0] + ".mp3"

        shutil.move(audio_path, os.path.join(output_dir, "audio.mp3"))

        audio_path = os.path.join(output_dir, "audio.mp3")

        ##################################################
        # Download Transcript
        ##################################################

        transcript = []

        try:

            video_id = self.extract_video_id(url)

            api = YouTubeTranscriptApi()

            fetched = api.fetch(video_id)

            for item in fetched:

                transcript.append(
                    {
                        "start": round(item.start, 2),
                        "duration": round(item.duration, 2),
                        "text": item.text,
                    }
                )

        except Exception as e:

            print("Transcript not available:", e)

        ##################################################
        # Save transcript
        ##################################################

        transcript_path = os.path.join(
            output_dir,
            "transcript.json",
        )

        with open(
            transcript_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                transcript,
                f,
                ensure_ascii=False,
                indent=4,
            )

        ##################################################
        # Save metadata
        ##################################################

        metadata = {
            "title": info.get("title"),
            "channel": info.get("uploader"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
        }

        with open(
            os.path.join(output_dir, "metadata.json"),
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                metadata,
                f,
                indent=4,
            )

        ##################################################

        return {
            "job_id": job_id,
            "title": metadata["title"],
            "channel": metadata["channel"],
            "duration": metadata["duration"],
            "thumbnail": metadata["thumbnail"],
            "audio_path": audio_path,
            "transcript_path": transcript_path,
            "transcript_found": len(transcript) > 0,
        }
