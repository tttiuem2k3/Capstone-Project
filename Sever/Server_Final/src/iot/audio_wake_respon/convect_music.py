import os
import subprocess

INPUT_FOLDER = "./"   # Thư mục chứa nhạc gốc (MP3, WAV, v.v.)
OUTPUT_FOLDER = "susscess"      # Thư mục xuất file WAV đã convert

# Tạo thư mục nếu chưa có
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_to_esp32_wav(input_path, output_path):
    # command = [
    # r"D:\App\ffmpeg\ffmpeg-2025-04-17-git-7684243fbe-full_build\bin\ffmpeg.exe",
    # "-y",
    # "-i", input_path,
    # "-ac", "1",
    # "-ar", "16000",
    # "-c:a", "pcm_u8",
    # output_path
    # ]
    command = [
    r"D:\App\ffmpeg\ffmpeg-2025-04-17-git-7684243fbe-full_build\bin\ffmpeg.exe",
    "-y",
    "-i", input_path,
    "-ac", "1",
    "-ar", "16000",
    "-filter:a", "volume=2",
    "-c:a", "pcm_u8",
    output_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Đã convert: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi convert {input_path}: {e.stderr.decode()}")

def batch_convert():
    for filename in os.listdir(INPUT_FOLDER):
        input_path = os.path.join(INPUT_FOLDER, filename)
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext in [".mp3", ".wav", ".m4a", ".flac", ".ogg"]:
            output_path = os.path.join(OUTPUT_FOLDER, f"{name}.wav")
            convert_to_esp32_wav(input_path, output_path)
        else:
            print(f"⚠️ Bỏ qua file không hỗ trợ: {filename}")

if __name__ == "__main__":
    batch_convert()
