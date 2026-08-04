from faster_whisper import WhisperModel
import ctranslate2

print("CUDA types:")
print(ctranslate2.get_supported_compute_types("cuda"))


model = WhisperModel("base", device="cuda", compute_type="float16")


print(model)
