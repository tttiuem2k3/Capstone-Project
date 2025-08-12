import sounddevice as sd
import scipy.io.wavfile as wav
import azure.cognitiveservices.speech as speechsdk

def record_audio(filename, duration=1.6, fs=16000):
    print(f"Đang ghi âm trong {duration} giây...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, fs, recording)
    print("Đã ghi âm xong.")

# Cấu hình Azure
speech_key = "5hY1DjrBaoePB2V00TLr74Fzcr8sS3i8RE3wPToDRA8t1U12WtplJQQJ99BFACqBBLyXJ3w3AAAYACOGXhch"
service_region = "southeastasia"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = "vi-VN"

while True:
    user_input = input("Nhấn '1' rồi Enter để bắt đầu ghi âm 1.6s (hoặc phím khác để thoát): ").strip()
    if user_input != "1":
        print("Thoát chương trình.")
        break

    filename = "audio_test_azureazure.wav"
    record_audio(filename, duration=2, fs=16000)

    # Nhận diện giọng nói từ file vừa ghi
    audio_config = speechsdk.audio.AudioConfig(filename=filename)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Đang nhận diện...")
    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Văn bản nhận diện được:", result.text)
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("Không nhận diện được giọng nói.")
    else:
        print("Lỗi:", result.reason)
# import azure.cognitiveservices.speech as speechsdk

# speech_key = "5hY1DjrBaoePB2V00TLr74Fzcr8sS3i8RE3wPToDRA8t1U12WtplJQQJ99BFACqBBLyXJ3w3AAAYACOGXhch"
# service_region = "southeastasia"

# speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# speech_config.speech_recognition_language = "vi-VN"

# # Nhận diện từ micro
# speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

# print("Nói vào micro để nhận diện...")
# result = speech_recognizer.recognize_once_async().get()

# if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#     print("Kết quả nhận diện:", result.text)
# else:
#     print("Không nhận diện được, lý do:", result.reason)
