import azure.cognitiveservices.speech as speechsdk
import time
from src import config

def text_to_speech_azure(text, output_filename, 
                         speech_key=config.azure_speech_key, 
                         service_region=config.azure_service_region, 
                         voice_name=config.female_voice_name):
    
    try:
        # Cấu hình Speech
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = voice_name

        # Cấu hình xuất ra file
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Thực hiện chuyển văn bản thành giọng nói
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return True
        else:
            print(f"Lỗi: {result.reason}")
            return False
    except Exception as e:
        print("Lỗi ngoại lệ:", e)
        return False

# Ví dụ sử dụng
# text_to_speech_azure("vâng", "male_response.wav")
