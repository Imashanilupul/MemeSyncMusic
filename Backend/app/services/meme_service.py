import requests

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util

from transformers import pipeline


class MemeService:

    def __init__(self):

        # Keyword extraction
        self.keyword_model = KeyBERT()

        # Semantic embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Emotion classifier
        self.emotion_model = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
        )

        # Meme embeddings cache
        self.meme_cache = None

    def analyze_lyrics(self, text):

        # Keywords

        keywords = self.keyword_model.extract_keywords(
            text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=5
        )

        keywords = [item[0] for item in keywords]

        # Emotion

        emotions = self.emotion_model(text)

        emotions = sorted(emotions[0], key=lambda x: x["score"], reverse=True)

        return {
            "keywords": keywords,
            "emotion": emotions[0]["label"],
            "emotion_score": round(emotions[0]["score"], 3),
        }

    def get_imgflip_memes(self):

        url = "https://api.imgflip.com/get_memes"

        response = requests.get(url)

        data = response.json()

        return data["data"]["memes"]

    def rank_memes(self, lyrics):

        memes = self.get_imgflip_memes()

        lyric_embedding = self.embedding_model.encode(lyrics, convert_to_tensor=True)

        results = []

        for meme in memes:

            meme_text = meme["name"]

            meme_embedding = self.embedding_model.encode(
                meme_text, convert_to_tensor=True
            )

            similarity = float(util.cos_sim(lyric_embedding, meme_embedding)[0][0])

            results.append(
                {
                    "name": meme["name"],
                    "url": meme["url"],
                    "similarity": round(similarity, 3),
                }
            )

        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:10]

    def search(self, lyrics):

        analysis = self.analyze_lyrics(lyrics)

        memes = self.rank_memes(lyrics)

        return {"lyrics": lyrics, "analysis": analysis, "memes": memes}
