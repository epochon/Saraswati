import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import azure.cognitiveservices.speech as speechsdk
import requests
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from agents import run_consensus_protocol

load_dotenv()
app = Flask(__name__)

# Firebase Setup
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def transcribe_with_azure(recording_url):
    audio_data = requests.get(recording_url + ".wav", auth=(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_data.content)

    speech_config = speechsdk.SpeechConfig(subscription=os.getenv("AZURE_SPEECH_KEY"), region=os.getenv("AZURE_REGION"))
    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-IN", "hi-IN"])
    audio_config = speechsdk.audio.AudioConfig(filename="temp_audio.wav")
    
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, auto_detect_source_language_config=auto_detect_config, audio_config=audio_config)
    result = recognizer.recognize_once()
    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else ""

@app.route("/voice", methods=['POST'])
def start_call():
    resp = VoiceResponse()
    resp.say("Welcome. Please state your name, location, and complaint after the beep. Press hash when done.", language="en-IN")
    resp.record(action="/process", maxLength=60, finishOnKey="#")
    return str(resp)

@app.route("/process", methods=['POST'])
def process():
    rec_url = request.form.get("RecordingUrl")
    from_num = request.form.get("From")
    
    # Voice-to-Text via Azure
    raw_text = transcribe_with_azure(rec_url)
    
    # 🔥 The variables are named here:
    final_data, agent_log, english_text = run_consensus_protocol(raw_text)

    db.collection('complaints').add({
        'phone': from_num,
        'raw_transcript': raw_text,
        'english_text': english_text,
        'consensus_data': final_data,
        'metadata': {
            'protocol': 'A2A-v2-Consensus',
            'interaction_log': agent_log,
            'timestamp': datetime.datetime.now()
        }
    })

    resp = VoiceResponse()
    # ✅ FIX: Use 'final_data' instead of 'final_report'
    # ✅ FIX: Use .get() to avoid KeyError if 'category' is missing
    category = final_data.get('category', 'complaint')
    resp.say(f"Consensus reached. Your {category} has been logged.")
    resp.hangup()
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True, port=5000)