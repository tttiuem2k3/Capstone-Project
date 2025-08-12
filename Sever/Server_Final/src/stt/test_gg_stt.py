import speech_recognition as sr
import sounddevice as sd
import scipy.io.wavfile as wav

def record_audio(filename, duration=1.6, fs=16000):
    print(f"Đang ghi âm trong {duration} giây...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, fs, recording)
    print("Đã ghi âm xong.")

def recognize_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="vi-VN")
        print("Nội dung nhận diện:", text)
    except sr.UnknownValueError:

        print("Không nhận diện được nội dung.")
    except sr.RequestError as e:
        print(f"Lỗi kết nối Google API: {e}")

if __name__ == "__main__":
    filename = "audio_test_gg.wav"
    while True:
        user_input = input("Nhấn '1' rồi Enter để bắt đầu ghi âm 1.8s (hoặc phím khác để thoát): ").strip()
        if user_input != "1":
            print("Thoát chương trình.")
            break
        record_audio(filename, duration=2)
        recognize_audio(filename)

