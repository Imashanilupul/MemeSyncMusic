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


import requests
from rapidfuzz import fuzz
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy


class MemeService:

    def __init__(self):

        self.analyzer = SentimentIntensityAnalyzer()

        self.nlp = spacy.load("en_core_web_sm")

    # ---------------------------
    # Emotion Detection
    # ---------------------------

    def detect_emotion(self, text):

        score = self.analyzer.polarity_scores(text)

        compound = score["compound"]

        if compound >= 0.5:
            return "happy"

        if compound <= -0.5:
            return "sad"

        if compound <= -0.2:
            return "angry"

        return "neutral"

    # ---------------------------
    # Keyword Extraction
    # ---------------------------

    def extract_keywords(self, text):

        doc = self.nlp(text)

        keywords = []

        for token in doc:

            if token.pos_ in [
                "NOUN",
                "PROPN",
                "ADJ",
                "VERB",
            ]:

                word = token.lemma_.lower()

                if len(word) > 2:

                    keywords.append(word)

        return list(dict.fromkeys(keywords))

    # ---------------------------
    # Reddit Search
    # ---------------------------

    def reddit_search(self, keyword):

        headers = {"User-Agent": "Mozilla/5.0"}

        url = f"https://www.reddit.com/search.json?" f"limit=25&q={keyword}"

        try:

            r = requests.get(
                url,
                headers=headers,
                timeout=20,
            )

            posts = r.json()["data"]["children"]

            memes = []

            for post in posts:

                data = post["data"]

                image = data.get("url_overridden_by_dest")

                if image and image.endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".gif",
                        ".webp",
                    )
                ):

                    memes.append(
                        {
                            "title": data["title"],
                            "image": image,
                            "score": data["score"],
                            "source": "reddit",
                        }
                    )

            return memes

        except Exception:

            return []

    # ---------------------------
    # Imgflip Search
    # ---------------------------

    def imgflip_search(self):

        try:

            response = requests.get(
                "https://api.imgflip.com/get_memes",
                timeout=20,
            )

            memes = response.json()["data"]["memes"]

            return [
                {
                    "title": meme["name"],
                    "image": meme["url"],
                    "score": 0,
                    "source": "imgflip",
                }
                for meme in memes
            ]

        except Exception:

            return []

    # ---------------------------
    # Ranking
    # ---------------------------

    def rank_memes(
        self,
        lyric,
        memes,
    ):

        ranked = []

        for meme in memes:

            similarity = fuzz.token_sort_ratio(
                lyric.lower(),
                meme["title"].lower(),
            )

            meme["similarity"] = similarity

            ranked.append(meme)

        ranked.sort(
            key=lambda x: x["similarity"],
            reverse=True,
        )

        return ranked

    # ---------------------------
    # Main Function
    # ---------------------------

    def find_memes(self, lyric):

        emotion = self.detect_emotion(lyric)

        keywords = self.extract_keywords(lyric)

        memes = []

        for keyword in keywords:

            memes.extend(self.reddit_search(keyword))

        memes.extend(self.imgflip_search())

        ranked = self.rank_memes(
            lyric,
            memes,
        )

        return {
            "lyric": lyric,
            "emotion": emotion,
            "keywords": keywords,
            "memes": ranked[:10],
        }
