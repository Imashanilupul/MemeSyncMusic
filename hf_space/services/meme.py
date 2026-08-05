import requests
import spacy
from rapidfuzz import fuzz
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class MemeService:
    """
    Single consolidated meme-matching implementation.

    Note: this intentionally drops the Reddit-search variant that was
    duplicated across files — reddit.com/search.json is an unauthenticated,
    unsupported endpoint that rate-limits aggressively, and it returns
    unmoderated images with no NSFW filtering, which isn't safe for an
    auto-generated video pipeline. Imgflip's curated template set is the
    only source used here.
    """

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

            if not data.get("success"):
                print("Imgflip API returned success=false")
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
        base_score = fuzz.token_set_ratio(
            lyric.lower(),
            meme_name.lower(),
        )

        if not keywords:
            return base_score

        # Average (not sum) across keywords, so lines that happen to yield
        # more keywords don't automatically outrank shorter lines just from
        # accumulating more additive bonus points.
        keyword_score = sum(
            fuzz.partial_ratio(keyword, meme_name.lower()) for keyword in keywords
        ) / len(keywords)

        return (base_score * 0.6) + (keyword_score * 0.4)

    # -----------------------------
    # Find Best Memes
    # -----------------------------
    def find_memes(
        self,
        lyric,
        top_k=10,
    ):
        if not self.memes:
            # Template pool failed to load at startup — surface an empty,
            # clearly-labeled result instead of pretending nothing matched.
            return {
                "lyric": lyric,
                "emotion": "neutral",
                "keywords": [],
                "results": [],
            }

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
