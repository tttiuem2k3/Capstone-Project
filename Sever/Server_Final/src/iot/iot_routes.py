import os
import wave
import subprocess
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.responses import Response
from threading import Thread

from src import config
from src.wake_detection.wake_word_detection import detect_wake_word,detect_wake_word_pvporcupine
from src.stt.speech_to_text import recognize_audio
from src.tts.text_to_speech import text_to_speech_azure
from src.base.llm_model import answer_question_viT5, answer_question_vinaLlama
from src.base.prompt_normalization import question_normalization
os.makedirs(config.AUDIO_DIRS["chunks"], exist_ok=True)

router = APIRouter()
chunk_counter = 0
chunk_wake_word_counter = 0
processing_status = {
    "is_processing": False,
    "done": False
}
history = []
AI = 1
@router.get("/list_music")
async def list_music():
    print("\n----------⭐⭐⭐⭐⭐ Thiết bị phần cứng đã được khởi động!⭐⭐⭐⭐⭐ ----------\n")
    print("\n----------> 🔵 Lấy danh sách bài hát!\n")
    try:
        files = [f for f in os.listdir(config.AUDIO_DIRS["music"]) if f.endswith(".wav")]
        return files
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/wake_word_record")
async def wake_word_record(request: Request):
    global chunk_wake_word_counter
    chunk_data = await request.body()
    chunk_filename = f"chunk_{chunk_wake_word_counter:05d}.wav"
    path = os.path.join(config.AUDIO_DIRS["wake_word_chunks"], chunk_filename)
    with open(path, 'wb') as f:
        f.write(chunk_data)
    chunk_wake_word_counter += 1
    return {"status": "ok", "file": chunk_filename}

@router.get("/check_wake_word")
async def check_wake_word():
    global AI
    global chunk_wake_word_counter
    combine_chunks(config.AUDIO_DIRS["wake_word_chunks"], config.AUDIO_DIRS["esp32_wake_word_audio"])
    try:
        has_wake_word = detect_wake_word()
        # has_wake_word = detect_wake_word_pvporcupine()
        if has_wake_word == 1:
            AI = 1
            remove_chunk(config.AUDIO_DIRS["wake_word_chunks"], "wake_word_chunks")
            return Response(status_code=200)
        elif has_wake_word == 2:
            AI = 2
            remove_chunk(config.AUDIO_DIRS["wake_word_chunks"], "wake_word_chunks")
            return Response(status_code=202)
        else:
            if chunk_wake_word_counter >= 40:
                remove_chunk(config.AUDIO_DIRS["wake_word_chunks"], "wake_word_chunks")
            return Response(status_code=204)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/stream_record")
async def stream_chunk(request: Request):
    global chunk_counter
    chunk_data = await request.body()
    chunk_filename = f"chunk_{chunk_counter:05d}.wav"
    path = os.path.join(config.AUDIO_DIRS["chunks"], chunk_filename)
    with open(path, 'wb') as f:
        f.write(chunk_data)
    chunk_counter += 1
    return {"status": "ok", "file": chunk_filename}

@router.post("/end_stream_record")
async def end_stream():
    combine_chunks(config.AUDIO_DIRS["chunks"], config.AUDIO_DIRS["input_audio_from_esp32"])
    remove_chunk(config.AUDIO_DIRS["chunks"], "chunks")
    return {"status": "done", "output": config.AUDIO_DIRS["input_audio_from_esp32"]}

@router.get("/start_ai_process")
async def start_ai_process():
    if not processing_status["is_processing"]:
        Thread(target=ai_processing_thread).start()
        return {"message": "Started processing"}
    else:
        return JSONResponse(content={"message": "Already processing"}, status_code=202)

@router.get("/check_status")
async def check_status():
    if processing_status["done"]:
        processing_status["done"] = False
        return {"status": "done"}
    return JSONResponse(content={"status": "false"}, status_code=202)

@router.get("/output_audio")
async def stream_output_audio():
    path = config.AUDIO_DIRS["output_audio_to_esp32"]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="audio/wav")

@router.get("/play_music/{filename:path}")
async def stream_music(filename: str):
    if filename.startswith("bao_thuc"):
        folder = config.AUDIO_DIRS["alarm"]
        print("\n----------> 🔔 Phát báo thức!\n")
    elif filename.endswith("response.wav"):
        folder = config.AUDIO_DIRS["audio_wake_respon"]
        if AI == 1:
            print("---> 🤖 LISA: Dạ có emmm!\n")
        elif AI == 2:
            print("---> 🤖 DAVID: vânggg!\n")
        print("---> 🎙️  Bắt đầu ghi âm câu hỏi của bạn!\n")
    else:
        folder = config.AUDIO_DIRS["music"]
        print(f"\n----------> 🎶 Phát bài hát {filename}!\n")
    safe_path = os.path.join(folder, os.path.basename(filename))
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(safe_path, media_type="audio/wav")


# ---------------- Xử lý AI -----------------

def ai_processing_thread():
    global processing_status
    global history
    global AI
    processing_status["is_processing"] = True
    processing_status["done"] = False
    try:
        config.AUDIO_DIRS["input_audio_from_esp32"]
        text = ""
        text= recognize_audio(config.AUDIO_DIRS["input_audio_from_esp32"])
        if AI == 1:
            if text == "":
                text = "..."
                print(f"---> 🗣  Bạn nói: {text}\n")
                print(f"🧠 LISA (Medical ViT5) đang suy nghĩ câu trả lời......")
                response ="Bạn muốn hỏi gì, tôi sẽ hỗ trợ bạn các câu hỏi về bệnh tật."
            else:   
                print(f"---> 🗣  Bạn nói: {text}\n")
                print(f"🧠 LISA (Medical ViT5) đang suy nghĩ câu trả lời......")
                question = question_normalization(text, history, 0)
                if question == "Vui lòng đặt câu hỏi liên quan đến bệnh tật.":
                    response = "Vui lòng đặt câu hỏi liên quan đến bệnh tật."
                else:
                    print(f"\n🧠 LISA: Ý bạn muốn hỏi ' {question.lower()} '......")
                    response = answer_question_viT5(question)

            
            print(f"\n---> 🤖 LISA: {response}\n")
            text_to_speech_azure(response, config.AUDIO_DIRS["ai_output_audio"], config.azure_speech_key, 
                                 config.azure_service_region, config.female_voice_name)

        elif AI == 2:
            if text == "":
                text = "..."
                print(f"---> 🗣  Bạn nói: {text}\n")
                print(f"🧠 DAVID (Medical VinaLlama2.7B) đang suy nghĩ câu trả lời......")
                response ="Bạn muốn hỏi gì, tôi sẽ hỗ trợ bạn các câu hỏi về bệnh tật."
            else:   
                print(f"---> 🗣  Bạn nói: {text}\n")
                print(f"🧠 DAVID (Medical VinaLlama2.7B) đang suy nghĩ câu trả lời......")
                question = question_normalization(text, history, 1)
                print(f"\n🧠 DAVID: Ý bạn muốn hỏi ' {question.lower()} '......")
                response = answer_question_vinaLlama(question)
            
            print(f"\n---> 🤖 DAVID: {response}\n")
            text_to_speech_azure(response, config.AUDIO_DIRS["ai_output_audio"], config.azure_speech_key, 
                                 config.azure_service_region, config.male_voice_name)

        history.insert(0, text)
        if len(history) > 6:
            history = history[:6]
        convert_to_esp32_wav(config.AUDIO_DIRS["ai_output_audio"], config.AUDIO_DIRS["output_audio_to_esp32"])
        AI = 1

    except Exception as e:
        print(f"❌ Lỗi xử lý AI: {e}")

    processing_status["is_processing"] = False
    processing_status["done"] = True

# ----------------- Hàm tiện ích -----------------

def combine_chunks(input_dir, output_file):
    chunk_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.wav')])
    with wave.open(output_file, 'wb') as wf_out:
        wf_out.setnchannels(1)
        wf_out.setsampwidth(2)  # 16-bit
        wf_out.setframerate(16000)
        for fname in chunk_files:
            with open(os.path.join(input_dir, fname), 'rb') as f:
                wf_out.writeframes(f.read())

def remove_chunk(input_dir,name_chunks):
    chunk_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.wav')])
    for fname in chunk_files:
        os.remove(os.path.join(input_dir, fname))
    global chunk_counter
    global chunk_wake_word_counter
    if name_chunks == "wake_word_chunks":
        chunk_wake_word_counter = 0
    else:
        chunk_counter = 0

def convert_to_esp32_wav(input_path, output_path):
    command = [
        r"D:\App\ffmpeg\ffmpeg-2025-04-17-git-7684243fbe-full_build\bin\ffmpeg.exe",
        "-y",
        "-i", input_path,
        "-filter:a", "volume=1.5",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_u8",
        output_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"---> 🔊 Phát âm thanh trả lời từ AI!\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi convert {input_path}: {e.stderr.decode()}")

"uvicorn iot_routes:router --host 0.0.0.0 --port 8888 --reload --log-level warning --no-access-log"