import re
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

    def get_transcript(self, url: str):
        video_id = self.extract_video_id(url)

        if not video_id:
            raise Exception("Invalid YouTube URL")

        ytt_api = YouTubeTranscriptApi()

        fetched_transcript = ytt_api.fetch(video_id)

        lyrics = []

        for snippet in fetched_transcript:
            lyrics.append(
                {
                    "start": round(snippet.start, 2),
                    "duration": round(snippet.duration, 2),
                    "text": snippet.text,
                }
            )

        return {"video_id": video_id, "lyrics": lyrics}
