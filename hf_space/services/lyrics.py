import re


class LyricsService:
    def __init__(self):
        pass

    def clean(self, lyrics: list[dict]) -> list[dict]:
        """
        Clean transcript text.
        """

        cleaned = []

        for line in lyrics:

            text = line["text"]

            # Remove [Music], [Applause], etc.
            text = re.sub(r"\[.*?\]", "", text)

            # Remove extra spaces
            text = re.sub(r"\s+", " ", text).strip()

            if text:

                cleaned.append(
                    {
                        "start": line["start"],
                        "duration": line["duration"],
                        "text": text,
                    }
                )

        return cleaned

    def merge_short_lines(
        self,
        lyrics: list[dict],
        max_gap: float = 1.0,
    ):
        """
        Merge consecutive short lyric lines.
        """

        if not lyrics:
            return []

        merged = []

        current = lyrics[0].copy()

        for nxt in lyrics[1:]:

            current_end = current["start"] + current["duration"]

            gap = nxt["start"] - current_end

            if gap <= max_gap:

                current["text"] += " " + nxt["text"]

                current["duration"] = nxt["start"] + nxt["duration"] - current["start"]

            else:

                merged.append(current)

                current = nxt.copy()

        merged.append(current)

        return merged

    def split_long_lines(
        self,
        lyrics: list[dict],
        max_words: int = 8,
    ):
        """
        Split long lyric sentences into multiple captions.
        """

        output = []

        for line in lyrics:

            words = line["text"].split()

            if len(words) <= max_words:

                output.append(line)

                continue

            chunk_count = (len(words) + max_words - 1) // max_words

            duration_per_chunk = line["duration"] / chunk_count

            for i in range(chunk_count):

                chunk = words[i * max_words : (i + 1) * max_words]

                output.append(
                    {
                        "start": line["start"] + i * duration_per_chunk,
                        "duration": duration_per_chunk,
                        "text": " ".join(chunk),
                    }
                )

        return output

    def process(self, lyrics):

        lyrics = self.clean(lyrics)

        lyrics = self.merge_short_lines(lyrics)

        lyrics = self.split_long_lines(lyrics)

        return lyrics
