from faster_whisper import WhisperModel


class TranscriptionService:

    def __init__(self):
        self.model = None

    def load_model(self):

        if self.model is None:

            print("Loading Whisper model...")

            self.model = WhisperModel("small", device="cuda", compute_type="float16")

            print("Whisper model loaded")

        return self.model

    def transcribe(self, filepath: str):

        model = self.load_model()

        segments, info = model.transcribe(filepath, beam_size=5)

        transcript = []

        for segment in segments:

            transcript.append(
                {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                }
            )

        return {"language": info.language, "segments": transcript}
