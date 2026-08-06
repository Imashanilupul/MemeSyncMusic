import librosa
import numpy as np


class AudioService:

    def __init__(self):
        pass

    # -----------------------
    # Analyze Audio
    # -----------------------

    def analyze(self, audio_path):

        y, sr = librosa.load(audio_path, sr=None)

        duration = librosa.get_duration(y=y, sr=sr)

        tempo, beat_frames = librosa.beat.beat_track(
            y=y,
            sr=sr,
        )

        # librosa.beat.beat_track's return type for `tempo` has changed
        # across versions — sometimes a plain float, sometimes a size-1
        # numpy array. float() only accepts a true 0-d array/scalar, so
        # normalize explicitly instead of assuming either shape.
        tempo = np.asarray(tempo).reshape(-1)[0]

        beat_times = librosa.frames_to_time(
            beat_frames,
            sr=sr,
        )

        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr,
        )

        onset_times = librosa.frames_to_time(
            onset_frames,
            sr=sr,
        )

        rms = librosa.feature.rms(y=y)[0]

        spectral_centroid = librosa.feature.spectral_centroid(
            y=y,
            sr=sr,
        )[0]

        chroma = librosa.feature.chroma_stft(
            y=y,
            sr=sr,
        )

        return {
            "duration": float(duration),
            "sample_rate": sr,
            "tempo": float(tempo),
            "beats": beat_times.tolist(),
            "onsets": onset_times.tolist(),
            "rms_mean": float(np.mean(rms)),
            "rms_max": float(np.max(rms)),
            "spectral_centroid": float(np.mean(spectral_centroid)),
            "chroma_mean": chroma.mean(axis=1).tolist(),
        }

    # -----------------------
    # Match Lyrics to Beats
    # -----------------------

    def align_lyrics(self, lyrics, beats):

        aligned = []

        for lyric in lyrics:

            start = lyric["start"]

            nearest = min(
                beats,
                key=lambda b: abs(b - start),
            )

            aligned.append(
                {
                    **lyric,
                    "beat": nearest,
                }
            )

        return aligned

    # -----------------------
    # Detect Energy
    # -----------------------

    def energy_level(self, rms):

        if rms > 0.25:
            return "high"

        elif rms > 0.10:
            return "medium"

        return "low"

    # -----------------------
    # Complete Pipeline
    # -----------------------

    def process(
        self,
        audio_path,
        lyrics,
    ):

        analysis = self.analyze(audio_path)

        aligned = self.align_lyrics(
            lyrics,
            analysis["beats"],
        )

        analysis["lyrics"] = aligned

        analysis["energy"] = self.energy_level(analysis["rms_mean"])

        return analysis
