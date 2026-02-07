import azure.cognitiveservices.speech as speechsdk
import requests
import os

def transcribe_and_translate(recording_url):
    # Setup Azure Config
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_KEY"), 
        region=os.getenv("AZURE_REGION")
    )
    # Auto-detect English and Hindi
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["en-IN", "hi-IN"]
    )
    
    # Download file from Twilio
    audio_data = requests.get(recording_url + ".wav", auth=(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH")))
    with open("temp.wav", "wb") as f:
        f.write(audio_data.content)

    audio_config = speechsdk.audio.AudioConfig(filename="temp.wav")
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, 
        auto_detect_source_language_config=auto_detect_config, 
        audio_config=audio_config
    )
    
    result = recognizer.recognize_once()
    # Note: If Hindi is detected, you can call a simple Gemini prompt here to translate to English
    return result.text