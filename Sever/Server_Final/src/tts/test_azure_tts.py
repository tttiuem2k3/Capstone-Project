import azure.cognitiveservices.speech as speechsdk
import time
# Đo thời gian bắt đầu
start_time = time.time()

# Thay bằng key và region của bạn
speech_key = "5hY1DjrBaoePB2V00TLr74Fzcr8sS3i8RE3wPToDRA8t1U12WtplJQQJ99BFACqBBLyXJ3w3AAAYACOGXhch"
service_region = "southeastasia"  # vd: "southeastasia"

# Khởi tạo Speech Config
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Chọn giọng nói tiếng Việt (ví dụ: 'vi-VN-HoaiMyNeural' hoặc 'vi-VN-NamMinhNeural')
# speech_config.speech_synthesis_voice_name = 'vi-VN-HoaiMyNeural'
speech_config.speech_synthesis_voice_name = 'vi-VN-NamMinhNeural'
# Nội dung cần chuyển
text = "vâng"

# Khởi tạo synthesizer
audio_config = speechsdk.audio.AudioOutputConfig(filename="male_response.wav")
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# Chuyển văn bản thành giọng nói
result = synthesizer.speak_text_async(text).get()


if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    # Đo thời gian kết thúc
    end_time = time.time()
    print(f"Thời gian thực thi: {end_time - start_time:.3f} giây")

else:
    print(f"Lỗi: {result.reason}")
