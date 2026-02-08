import os
import datetime
import requests
from flask import Flask, request, Response, session
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client as TwilioClient
import azure.cognitiveservices.speech as speechsdk
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Import our refined agents
from agents import run_edu_protocol, run_consensus_protocol, generate_summary_message

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-change-this")

# Firebase Setup
try:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase initialized successfully")
except Exception as e:
    print(f"⚠ Firebase initialization error: {e}")
    db = None

# Twilio Client for SMS
try:
    twilio_client = TwilioClient(
        os.getenv("TWILIO_SID"), 
        os.getenv("TWILIO_AUTH_TOKEN")
    )
    print("✓ Twilio client initialized successfully")
except Exception as e:
    print(f"⚠ Twilio client initialization error: {e}")
    twilio_client = None

def send_sms(to_number, message):
    """Send SMS notification to the caller"""
    try:
        if not twilio_client:
            print("Twilio client not initialized, skipping SMS")
            return False
        
        # Get Twilio phone number from environment
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not from_number:
            print("TWILIO_PHONE_NUMBER not configured")
            return False
        
        message_obj = twilio_client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        print(f"✓ SMS sent successfully: {message_obj.sid}")
        return True
        
    except Exception as e:
        print(f"⚠ SMS sending error: {e}")
        return False

def transcribe_with_azure(recording_url):
    """Downloads recording and transcribes using Azure Speech-to-Text"""
    try:
        auth = (os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        
        # Download the audio file
        audio_data = requests.get(recording_url + ".wav", auth=auth, timeout=30)
        
        if audio_data.status_code != 200:
            print(f"Failed to download recording: {audio_data.status_code}")
            return ""
        
        # Save temporarily
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data.content)

        # Configure Azure Speech
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"), 
            region=os.getenv("AZURE_REGION")
        )
        
        # Support English and Hindi (Azure auto-detect supports max 4 languages)
        auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["en-IN", "hi-IN"]
        )
        
        audio_config = speechsdk.audio.AudioConfig(filename="temp_audio.wav")
        
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            auto_detect_source_language_config=auto_detect_config, 
            audio_config=audio_config
        )
        
        result = recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"✓ Transcription successful: {result.text}")
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print(f"⚠ No speech detected in audio")
            return ""
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"⚠ Transcription canceled: {cancellation.reason}")
            if cancellation.reason == speechsdk.CancellationReason.Error:
                print(f"⚠ Error details: {cancellation.error_details}")
                print(f"⚠ Check your AZURE_SPEECH_KEY and AZURE_REGION in .env")
            return ""
        else:
            print(f"⚠ Transcription failed: {result.reason}")
            return ""
            
    except Exception as e:
        print(f"⚠ Transcription error: {e}")
        return ""
    finally:
        # Cleanup
        try:
            if os.path.exists("temp_audio.wav"):
                os.remove("temp_audio.wav")
        except:
            pass

# Language selection messages
MESSAGES = {
    "en": {
        "welcome": "Welcome to Citizen Services. Press 1 for English. Hindi ke liye 2 dabaaye.",
        "menu": "Press 2 for Education Assistant. Press 3 for Utility Complaints. Press star to go back.",
        "edu_prompt": "Education mode activated. Ask your question after the beep and press hash when done.",
        "edu_continue": "Do you have another question? After the beep, ask your question and press hash when done. If you have no more questions, just wait and the call will end.",
        "complaint_prompt": "Complaint registration mode. Please state your name, location, and your complaint clearly, then press hash.",
        "missing_details": "I could not capture all details. Please state your name and location clearly after the beep, then press hash.",
        "missing_name": "I missed your name. Please state your name after the beep and press hash.",
        "missing_location": "I missed your location. Please state your location after the beep and press hash.",
        "goodbye": "Thank you for using our service. Goodbye!",
        "processing": "Please wait while I process your request."
    },
    "hi": {
        "welcome": "Naagrik sevaon mein aapka swaagat hai. English ke liye 1 dabaaye. Hindi ke liye 2 dabaaye.",
        "menu": "Shiksha sahayak ke liye 2 dabaaye. Complaint registration ke liye 3 dabaaye. Peeche jaane ke liye star dabaaye.",
        "edu_prompt": "Shiksha mode chalu. Beep ke baad apna sawaal puchiye aur hash dabaaye.",
        "edu_continue": "Kya aapka koi aur sawaal hai? Beep ke baad puchiye aur hash dabaaye. Agar koi sawaal nahi hai toh bas pratiksha karein.",
        "complaint_prompt": "Complaint registration mode. Kripya apna naam, sthaan, aur shikayat bataye, phir hash dabaaye.",
        "missing_details": "Kuch details nahin mil payi. Kripya apna naam aur sthaan phir se bataiye aur hash dabaaye.",
        "missing_name": "Aapka naam nahin mila. Kripya apna naam bataiye aur hash dabaaye.",
        "missing_location": "Aapka sthaan nahin mila. Kripya apna sthaan bataiye aur hash dabaaye.",
        "goodbye": "Hamari seva ka upyog karne ke liye dhanyavaad. Namaste!",
        "processing": "Kripya pratiksha karein, hum aapki request process kar rahe hain."
    }
}

def get_language():
    """Get current language from session, default to English"""
    return session.get('language', 'en')

def get_message(key):
    """Get message in current language"""
    lang = get_language()
    return MESSAGES[lang].get(key, MESSAGES['en'].get(key, ""))

@app.route("/voice", methods=['POST'])
def start_call():
    """Initial call handler with language selection"""
    resp = VoiceResponse()
    
    # Language selection
    gather = Gather(numDigits=1, action="/language_selection", timeout=5)
    gather.say(MESSAGES['en']['welcome'], language="en-IN", voice="Polly.Aditi")
    resp.append(gather)
    
    # If no input, repeat
    resp.redirect("/voice")
    
    return Response(str(resp), mimetype='text/xml')

@app.route("/language_selection", methods=['POST'])
def language_selection():
    """Handle language selection"""
    digit = request.form.get("Digits")
    resp = VoiceResponse()
    
    # Set language in session
    if digit == "1":
        session['language'] = 'en'
    elif digit == "2":
        session['language'] = 'hi'
    else:
        # Invalid input, redirect to start
        resp.redirect("/voice")
        return Response(str(resp), mimetype='text/xml')
    
    # Proceed to main menu
    resp.redirect("/main_menu")
    return Response(str(resp), mimetype='text/xml')

@app.route("/main_menu", methods=['POST'])
def main_menu():
    """Main menu after language selection"""
    resp = VoiceResponse()
    lang = get_language()
    
    gather = Gather(numDigits=1, action="/menu_selection", timeout=5)
    gather.say(get_message('menu'), language="hi-IN" if lang == 'hi' else "en-IN", voice="Polly.Aditi")
    resp.append(gather)
    
    # If no input, repeat
    resp.redirect("/main_menu")
    
    return Response(str(resp), mimetype='text/xml')

@app.route("/menu_selection", methods=['POST'])
def menu_selection():
    """Handle main menu selection"""
    digit = request.form.get("Digits")
    resp = VoiceResponse()
    lang = get_language()
    voice_lang = "hi-IN" if lang == 'hi' else "en-IN"
    
    if digit == "2":
        # Education Assistant
        session['conversation_history'] = []  # Initialize conversation history
        resp.say(get_message('edu_prompt'), language=voice_lang, voice="Polly.Aditi")
        resp.say("You will hear a beep. After the beep, ask your question and press hash when you are done.", 
                language=voice_lang, voice="Polly.Aditi")
        resp.record(action="/edu_process", maxLength=90, finishOnKey="#", timeout=5, playBeep=True)
        
    elif digit == "3":
        # Complaint Registration
        resp.say(get_message('complaint_prompt'), language=voice_lang, voice="Polly.Aditi")
        resp.record(action="/process", maxLength=90, finishOnKey="#", timeout=5)
        
    elif digit == "*":
        # Go back to language selection
        resp.redirect("/voice")
        
    else:
        # Invalid input, return to menu
        resp.redirect("/main_menu")
    
    return Response(str(resp), mimetype='text/xml')

@app.route("/edu_process", methods=['POST'])
def edu_process():
    """Handle education assistant conversation"""
    try:
        rec_url = request.form.get("RecordingUrl")
        from_num = request.form.get("From")
        
        # Check if there's a pending query from redirect
        pending_query = session.pop('pending_query', None)
        
        if pending_query:
            query = pending_query
        elif not rec_url:
            # No recording, might be timeout
            resp = VoiceResponse()
            resp.say("I didn't receive your question. Let's try again.", language="en-IN")
            resp.redirect("/main_menu")
            return Response(str(resp), mimetype='text/xml')
        else:
            # Transcribe the question
            query = transcribe_with_azure(rec_url)
        
        if not query or len(query.strip()) < 3:
            resp = VoiceResponse()
            resp.say("I couldn't understand that. Please try again.", language="en-IN", voice="Polly.Aditi")
            resp.say("You will hear a beep. Ask your question and press hash when done.", language="en-IN", voice="Polly.Aditi")
            resp.record(action="/edu_process", maxLength=90, finishOnKey="#", timeout=5, playBeep=True)
            return Response(str(resp), mimetype='text/xml')
        
        print(f"Education query: {query}")
        
        # Get conversation history from session
        conversation_history = session.get('conversation_history', [])
        
        # Run education protocol
        result = run_edu_protocol(query, conversation_history)
        
        # Update conversation history
        conversation_history.append({
            'query': query,
            'answer': result.get('answer', '')
        })
        session['conversation_history'] = conversation_history
        
        resp = VoiceResponse()
        lang = get_language()
        voice_lang = "hi-IN" if lang == 'hi' else "en-IN"
        
        # Speak the answer
        answer = result.get('answer', "I'm processing your request.")
        resp.say(answer, language=voice_lang, voice="Polly.Aditi")
        
        if result.get('status') == "NEED_INFO" and result.get('follow_up'):
            # Agent needs more information
            resp.pause(length=1)
            resp.say(result.get('follow_up'), language=voice_lang, voice="Polly.Aditi")
            resp.say("Please answer after the beep and press hash when done.", language=voice_lang, voice="Polly.Aditi")
            resp.record(action='/edu_process', maxLength=90, finishOnKey='#', timeout=5, playBeep=True)
        else:
            # Answer is complete, ask if they want to continue
            resp.pause(length=1)
            resp.say(get_message('edu_continue'), language=voice_lang, voice="Polly.Aditi")
            # Record for next question - this will play the beep
            resp.record(action='/edu_continue', maxLength=90, finishOnKey='#', timeout=10, 
                       playBeep=True)
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in edu_process: {e}")
        resp = VoiceResponse()
        resp.say("Sorry, there was an error. Please try again.", language="en-IN")
        resp.redirect("/main_menu")
        return Response(str(resp), mimetype='text/xml')

@app.route("/edu_followup", methods=['POST'])
def edu_followup():
    """Handle follow-up responses in education mode"""
    try:
        # Get the speech result
        speech_result = request.form.get("SpeechResult", "")
        
        if not speech_result or len(speech_result.strip()) < 3:
            # Try to get recording URL if speech recognition failed
            rec_url = request.form.get("RecordingUrl")
            if rec_url:
                speech_result = transcribe_with_azure(rec_url)
        
        if not speech_result or len(speech_result.strip()) < 3:
            resp = VoiceResponse()
            resp.say("I couldn't understand that. Let me ask again.", language="en-IN", voice="Polly.Aditi")
            resp.redirect("/edu_process")
            return Response(str(resp), mimetype='text/xml')
        
        # Treat this as a new query in the conversation
        session['temp_query'] = speech_result
        resp = VoiceResponse()
        resp.redirect("/edu_process")
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in edu_followup: {e}")
        resp = VoiceResponse()
        resp.say("Sorry, there was an error.", language="en-IN")
        resp.redirect("/main_menu")
        return Response(str(resp), mimetype='text/xml')

@app.route("/edu_continue", methods=['POST'])
def edu_continue():
    """Handle continuation choice in education mode"""
    rec_url = request.form.get("RecordingUrl")
    from_num = request.form.get("From")
    lang = get_language()
    voice_lang = "hi-IN" if lang == 'hi' else "en-IN"
    
    resp = VoiceResponse()
    
    # If there's a recording, it means user asked another question
    if rec_url:
        # Process as new question
        query = transcribe_with_azure(rec_url)
        
        if query and len(query.strip()) >= 3:
            # Valid question - redirect to process it
            # Store the query temporarily
            session['pending_query'] = query
            resp.redirect("/edu_process")
            return Response(str(resp), mimetype='text/xml')
    
    # No recording or invalid - end session
    resp.say(get_message('goodbye'), language=voice_lang, voice="Polly.Aditi")
    resp.hangup()
    
    # Send SMS with all Q&A from the session
    conversation_history = session.get('conversation_history', [])
    if conversation_history:
        summary = generate_education_summary(conversation_history)
        send_sms(from_num, summary)
    else:
        summary = generate_summary_message({}, is_education=True)
        send_sms(from_num, summary)
    
    # Clear session
    session.pop('conversation_history', None)
    
    return Response(str(resp), mimetype='text/xml')

@app.route("/process", methods=['POST'])
def process():
    """Process complaint registration"""
    try:
        rec_url = request.form.get("RecordingUrl")
        from_num = request.form.get("From")
        lang = get_language()
        voice_lang = "hi-IN" if lang == 'hi' else "en-IN"
        
        if not rec_url:
            resp = VoiceResponse()
            resp.say("No recording received. Please try again.", language=voice_lang)
            resp.redirect("/main_menu")
            return Response(str(resp), mimetype='text/xml')
        
        print(f"Processing complaint from {from_num}")
        
        # Transcribe
        raw_text = transcribe_with_azure(rec_url)
        
        if not raw_text or len(raw_text.strip()) < 5:
            resp = VoiceResponse()
            resp.say(get_message('missing_details'), language=voice_lang, voice="Polly.Aditi")
            resp.record(action='/retry_both', maxLength=90, finishOnKey='#', timeout=5)
            return Response(str(resp), mimetype='text/xml')
        
        print(f"Raw transcript: {raw_text}")
        
        # Run consensus protocol
        final_data, agent_log, english_text = run_consensus_protocol(raw_text)
        
        name = final_data.get('name', 'Unknown')
        location = final_data.get('location', 'Unknown')
        
        resp = VoiceResponse()

        # Validation Logic
        if name == "Unknown" and location == "Unknown":
            # Missing both
            resp.say(get_message('missing_details'), language=voice_lang, voice="Polly.Aditi")
            resp.record(action='/retry_both', maxLength=90, finishOnKey='#', timeout=5)
            return Response(str(resp), mimetype='text/xml')
            
        elif name == "Unknown":
            # Missing name only
            session['temp_complaint'] = final_data
            resp.say(get_message('missing_name'), language=voice_lang, voice="Polly.Aditi")
            resp.record(action='/retry_name', maxLength=60, finishOnKey='#', timeout=5)
            return Response(str(resp), mimetype='text/xml')
            
        elif location == "Unknown":
            # Missing location only
            session['temp_complaint'] = final_data
            resp.say(get_message('missing_location'), language=voice_lang, voice="Polly.Aditi")
            resp.record(action='/retry_location', maxLength=60, finishOnKey='#', timeout=5)
            return Response(str(resp), mimetype='text/xml')

        # All details captured - save to Firebase
        if db:
            try:
                db.collection('complaints').add({
                    'phone': from_num,
                    'raw_transcript': raw_text,
                    'english_transcript': english_text,
                    'consensus_data': final_data,
                    'metadata': {
                        'protocol': 'A2A-v2',
                        'log': agent_log,
                        'timestamp': datetime.datetime.now(),
                        'language': lang
                    }
                })
                print("✓ Complaint saved to Firebase")
            except Exception as e:
                print(f"⚠ Firebase save error: {e}")
        
        # Confirm to user
        category_name = final_data.get('category', 'complaint').replace(' complaint', '')
        confirmation = f"Your {category_name} complaint has been registered successfully. Thank you, {name}."
        
        if lang == 'hi':
            confirmation = f"Aapki {category_name} shikayat safaltapurvak register ho gayi hai. Dhanyavaad, {name}."
        
        resp.say(confirmation, language=voice_lang, voice="Polly.Aditi")
        resp.say(get_message('goodbye'), language=voice_lang, voice="Polly.Aditi")
        resp.hangup()
        
        # Send SMS summary
        summary = generate_summary_message(final_data, is_education=False)
        send_sms(from_num, summary)
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in process: {e}")
        resp = VoiceResponse()
        resp.say("Sorry, there was an error processing your complaint. Please try again.", language="en-IN")
        resp.redirect("/main_menu")
        return Response(str(resp), mimetype='text/xml')

@app.route("/retry_both", methods=['POST'])
def retry_both():
    """Retry capturing both name and location"""
    try:
        rec_url = request.form.get("RecordingUrl")
        from_num = request.form.get("From")
        lang = get_language()
        voice_lang = "hi-IN" if lang == 'hi' else "en-IN"
        
        raw_text = transcribe_with_azure(rec_url)
        final_data, _, english_text = run_consensus_protocol(raw_text)
        
        name = final_data.get('name', 'Unknown')
        location = final_data.get('location', 'Unknown')
        
        resp = VoiceResponse()
        
        if name == "Unknown" or location == "Unknown":
            # Still missing, ask one more time
            resp.say("I still couldn't capture the details. Please call again.", language=voice_lang, voice="Polly.Aditi")
            resp.redirect("/main_menu")
        else:
            # Got it, save and confirm
            session['temp_complaint'] = final_data
            resp.redirect("/save_complaint")
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in retry_both: {e}")
        resp = VoiceResponse()
        resp.redirect("/main_menu")
        return Response(str(resp), mimetype='text/xml')

@app.route("/retry_name", methods=['POST'])
def retry_name():
    """Retry capturing name only"""
    try:
        rec_url = request.form.get("RecordingUrl")
        raw_text = transcribe_with_azure(rec_url)
        
        # Extract just the name
        prompt = f"Extract only the person's name from this text. Return just the name, nothing else: {raw_text}"
        import google.generativeai as genai
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        name = response.text.strip()
        
        # Update temp complaint
        complaint_data = session.get('temp_complaint', {})
        complaint_data['name'] = name if name else "Unknown"
        session['temp_complaint'] = complaint_data
        
        # Check if we have everything now
        if complaint_data.get('name') != "Unknown" and complaint_data.get('location') != "Unknown":
            resp = VoiceResponse()
            resp.redirect("/save_complaint")
        else:
            resp = VoiceResponse()
            resp.say("I still couldn't get your name. Please try again.", language="en-IN")
            resp.redirect("/main_menu")
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in retry_name: {e}")
        resp = VoiceResponse()
        resp.redirect("/main_menu")
        return Response(str(resp), mimetype='text/xml')

@app.route("/retry_location", methods=['POST'])
def retry_location():
    """Retry capturing location only"""
    try:
        rec_url = request.form.get("RecordingUrl")
        raw_text = transcribe_with_azure(rec_url)
        
        # Extract just the location
        prompt = f"Extract only the location/place/city/village name from this text. Return just the location, nothing else: {raw_text}"
        import google.generativeai as genai
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        location = response.text.strip()
        
        # Update temp complaint
        complaint_data = session.get('temp_complaint', {})
        complaint_data['location'] = location if location else "Unknown"
        session['temp_complaint'] = complaint_data
        
        # Check if we have everything now
        if complaint_data.get('name') != "Unknown" and complaint_data.get('location') != "Unknown":
            resp = VoiceResponse()
            resp.redirect("/save_complaint")
        else:
            resp = VoiceResponse()
            resp.say("I still couldn't get your location. Please try again.", language="en-IN")
            resp.redirect("/main_menu")
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in retry_location: {e}")
        resp = VoiceResponse()
        resp.redirect("/main_menu")
        return Response(str(resp), mimetype='text/xml')

@app.route("/save_complaint", methods=['POST'])
def save_complaint():
    """Save complaint after all retries"""
    try:
        complaint_data = session.get('temp_complaint', {})
        from_num = request.form.get("From")
        lang = get_language()
        voice_lang = "hi-IN" if lang == 'hi' else "en-IN"
        
        # Save to Firebase
        if db and complaint_data:
            try:
                db.collection('complaints').add({
                    'phone': from_num,
                    'consensus_data': complaint_data,
                    'metadata': {
                        'protocol': 'A2A-v2-retry',
                        'timestamp': datetime.datetime.now(),
                        'language': lang
                    }
                })
                print("✓ Complaint saved to Firebase after retry")
            except Exception as e:
                print(f"⚠ Firebase save error: {e}")
        
        resp = VoiceResponse()
        
        category_name = complaint_data.get('category', 'complaint').replace(' complaint', '')
        name = complaint_data.get('name', 'there')
        
        confirmation = f"Thank you {name}. Your {category_name} complaint has been registered."
        if lang == 'hi':
            confirmation = f"Dhanyavaad {name}. Aapki {category_name} shikayat register ho gayi hai."
        
        resp.say(confirmation, language=voice_lang, voice="Polly.Aditi")
        resp.say(get_message('goodbye'), language=voice_lang, voice="Polly.Aditi")
        resp.hangup()
        
        # Send SMS summary
        summary = generate_summary_message(complaint_data, is_education=False)
        send_sms(from_num, summary)
        
        # Clear session
        session.pop('temp_complaint', None)
        
        return Response(str(resp), mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in save_complaint: {e}")
        resp = VoiceResponse()
        resp.say("Complaint saved. Thank you.", language="en-IN")
        resp.hangup()
        return Response(str(resp), mimetype='text/xml')

@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Citizen Services IVR System Starting...")
    print("="*50)
    print("\nRequired Environment Variables:")
    print("✓ TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
    print("✓ AZURE_SPEECH_KEY, AZURE_REGION")
    print("✓ GROQ_API_KEY, GEMINI_API_KEY, TAVILY_API_KEY")
    print("✓ FLASK_SECRET_KEY")
    print("\nServer starting on http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)