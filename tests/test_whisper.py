from faster_whisper import WhisperModel
import time

print("Loading model...")

model = WhisperModel("base", device="cuda", device_index=1, compute_type="float16")
print(model.model.device)

print("Model loaded")


segments, info = model.transcribe(
    "C:/Users/User/OneDrive/Documents/GitHub/MemeSyncMusic/Backend/uploads/4d734996-7f2d-459e-9a47-93a504824b89.mp3",
    beam_size=5,
)


for segment in segments:
    print(segment.text)


print("Keeping process alive...")
time.sleep(120)
