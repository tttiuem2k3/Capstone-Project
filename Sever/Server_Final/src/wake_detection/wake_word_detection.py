from src import config
import speech_recognition as sr
import pvporcupine
import scipy.io.wavfile as wav
import numpy as np
import noisereduce as nr
from src import config
# Từ khóa cần phát hiện (có thể tùy chỉnh)
WAKE_WORDS = {
    "lisa": 1,
    "david": 2
}
KEYWORD_CODE = {
    0: 2,   
    1: 1    
}
def detect_wake_word():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_adjustment_ratio = 1.5
    text = ""
    with sr.AudioFile(config.AUDIO_DIRS["esp32_wake_word_audio"]) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="vi-VN")
        except sr.UnknownValueError:
            text = ""
    text = text.lower()
    # print(f"\n ☑️  Kiểm tra ----------> Nhận diện giọng nói: {text}\n")

    words = text.split()
    for word in words:
        if word in WAKE_WORDS:
            print(f"\n ☑️  Kiểm tra ----------> ✅ Wake word detected: {word}!\n")
            return WAKE_WORDS[word]
        
    print("\n ☑️  Kiểm tra ----------> ❌ No wake word detected - Tiếp tục lắng nghe!\n")
    return 0

def detect_wake_word_pvporcupine():
    filename = config.AUDIO_DIRS["esp32_wake_word_audio"]
    access_key = config.PV_ACCESS_KEY  # Bạn thêm access key vào config hoặc truyền trực tiếp
    keyword_paths = config.PV_KEYWORD_PATHS  # List đường dẫn file .ppn theo đúng thứ tự code
    
    sensitivities = [0.8] * len(keyword_paths)
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=keyword_paths,
        sensitivities=sensitivities
    )
    fs, audio = wav.read(filename)
    if len(audio.shape) > 1:
        audio = audio[:, 0]
    # Giảm ồn
    audio_float = audio.astype(np.float32)
    audio_denoised = nr.reduce_noise(y=audio_float, sr=fs)
    audio_denoised = audio_denoised.astype(np.int16)
    assert fs == porcupine.sample_rate, f"Sample rate phải là {porcupine.sample_rate}, file là {fs}"
    num_frames = len(audio_denoised) // porcupine.frame_length
    for i in range(num_frames):
        start = i * porcupine.frame_length
        end = start + porcupine.frame_length
        pcm = audio_denoised[start:end]
        if len(pcm) < porcupine.frame_length:
            break
        result = porcupine.process(pcm)
        if result >= 0:
            print(f"\n ☑️  Kiểm tra ----------> ✅ Wake word (index {result}) detected!\n")
            porcupine.delete()
            return KEYWORD_CODE.get(result, 0)
    porcupine.delete()
    print("\n ☑️  Kiểm tra ----------> ❌ No wake word detected - Tiếp tục lắng nghe!\n")
    return 0