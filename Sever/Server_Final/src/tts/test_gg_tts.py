import time
from gtts import gTTS

# Đo thời gian bắt đầu
start_time = time.time()

# Nội dung văn bản cần chuyển
text = "Xin chào! Đây là ví dụ sử dụng chuyển văn bản thành giọng nói"

# Chọn ngôn ngữ tiếng Việt ('vi')
tts = gTTS(text=text, lang='vi')

# Lưu file âm thanh (mặc định là mp3)
tts.save("audio_gTTS.wav")

# Đo thời gian kết thúc
end_time = time.time()
print(f"Thời gian thực thi: {end_time - start_time:.3f} giây")

