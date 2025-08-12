import speech_recognition as sr

def recognize_audio(file_path):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_adjustment_ratio = 1.5
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="vi-VN")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"Lỗi kết nối Google API: {e}"
