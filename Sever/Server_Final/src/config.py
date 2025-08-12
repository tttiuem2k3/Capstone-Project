api_keys_llama = [
    "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"
]
api_key_gemini="AIzaSyCphqcgUiM14qGLka09MfjUm4LGMldkrzQ"

PV_ACCESS_KEY ="zOFGxTcv8MhGz9VBIwldl43+NbGNPAUoJjWirlFgBnRlPVUEyAiGjw=="

azure_speech_key="5hY1DjrBaoePB2V00TLr74Fzcr8sS3i8RE3wPToDRA8t1U12WtplJQQJ99BFACqBBLyXJ3w3AAAYACOGXhch"
azure_service_region="southeastasia"
male_voice_name = "vi-VN-NamMinhNeural"
female_voice_name = "vi-VN-HoaiMyNeural"

PV_KEYWORD_PATHS = [
    r"./src/wake_detection/david_en_windows_v3_0_0.ppn",   
    r"./src/wake_detection/maven_en_windows_v3_0_0.ppn"    
]

# model_viT5_path= "./model/Medical_QA_model_ViT5_base_epoch_50"
model_viT5_path= "./model/Medical_QA_model_ViT5_base_epoch_150"
# model_vinaLlama_path ="./model/Medical_QA_model_VinaLlama2.7B_epoch_6"
model_vinaLlama_path ="./model/Medical_QA_model_VinaLlama2.7B_epoch_23"
# Đường dẫn thư mục của hệ thống iot
AUDIO_DIRS = {
    "music": "./src/iot/music",
    "alarm": "./src/iot/alarm",
    "audio_wake_respon": "./src/iot/audio_wake_respon",
    "chunks": "./src/iot/stream_chunks",
    "wake_word_chunks": "./src/iot/wake_word_chunks",
    "esp32_wake_word_audio": "./src/iot/esp32_wake_word_audio.wav",
    "input_audio_from_esp32": "./src/iot/input_audio_from_esp32.wav",
    "ai_output_audio": "./src/iot/ai_output_audio.wav",
    "output_audio_to_esp32": "./src/iot/output_audio_to_esp32.wav"
}

