import requests
import spacy
from rapidfuzz import fuzz
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class MemeService:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment = SentimentIntensityAnalyzer()
        self.memes = self._load_imgflip_memes()

    # -----------------------------
    # Load Imgflip Memes
    # -----------------------------
    def _load_imgflip_memes(self):

        try:
            response = requests.get(
                "https://api.imgflip.com/get_memes",
                timeout=20,
            )

            response.raise_for_status()

            data = response.json()

            if not data["success"]:
                return []

            memes = []

            for meme in data["data"]["memes"]:

                memes.append(
                    {
                        "id": meme["id"],
                        "title": meme["name"],
                        "image_url": meme["url"],
                        "width": meme["width"],
                        "height": meme["height"],
                        "box_count": meme["box_count"],
                    }
                )

            return memes

        except Exception as e:
            print("Imgflip Error:", e)
            return []

    # -----------------------------
    # Emotion Detection
    # -----------------------------
    def detect_emotion(self, text):

        score = self.sentiment.polarity_scores(text)

        compound = score["compound"]

        if compound >= 0.6:
            return "happy"

        elif compound >= 0.2:
            return "positive"

        elif compound <= -0.6:
            return "sad"

        elif compound <= -0.2:
            return "angry"

        return "neutral"

    # -----------------------------
    # Keyword Extraction
    # -----------------------------
    def extract_keywords(self, text):

        doc = self.nlp(text)

        keywords = []

        for token in doc:

            if token.is_stop:
                continue

            if token.is_punct:
                continue

            if token.pos_ in [
                "NOUN",
                "PROPN",
                "VERB",
                "ADJ",
            ]:

                keywords.append(token.lemma_.lower())

        return list(dict.fromkeys(keywords))

    # -----------------------------
    # Score Meme
    # -----------------------------
    def score_meme(
        self,
        lyric,
        meme_name,
        keywords,
    ):

        score = fuzz.token_set_ratio(
            lyric.lower(),
            meme_name.lower(),
        )

        for keyword in keywords:

            score += (
                fuzz.partial_ratio(
                    keyword,
                    meme_name.lower(),
                )
                * 0.5
            )

        return score

    # -----------------------------
    # Find Best Memes
    # -----------------------------
    def find_memes(
        self,
        lyric,
        top_k=10,
    ):

        emotion = self.detect_emotion(lyric)

        keywords = self.extract_keywords(lyric)

        ranked = []

        for meme in self.memes:

            similarity = self.score_meme(
                lyric,
                meme["title"],
                keywords,
            )

            ranked.append(
                {
                    **meme,
                    "emotion": emotion,
                    "score": similarity,
                }
            )

        ranked.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return {
            "lyric": lyric,
            "emotion": emotion,
            "keywords": keywords,
            "results": ranked[:top_k],
        }

    # -----------------------------
    # Return Single Best Meme
    # -----------------------------
    def best_meme(self, lyric):

        result = self.find_memes(
            lyric,
            top_k=1,
        )

        if result["results"]:
            return result["results"][0]

        return None
