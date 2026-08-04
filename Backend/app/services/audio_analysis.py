import librosa
import numpy as np


class AudioAnalyzer:

    def analyze(self, filepath: str):

        y, sr = librosa.load(filepath, sr=None)

        duration = librosa.get_duration(y=y, sr=sr)

        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        tempo = np.asarray(tempo).item()

        beat_times = librosa.frames_to_time(beats, sr=sr)

        rms = librosa.feature.rms(y=y)[0]

        return {
            "duration": round(duration, 2),
            "sample_rate": sr,
            "bpm": round(tempo, 2),
            "total_beats": len(beat_times),
            "beat_times": beat_times.tolist(),
            "average_energy": round(float(np.mean(rms)), 4),
        }
