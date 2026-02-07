import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def translate_to_english(text):
    """Bridge: Translates Hindi/Mixed input to English for consistent analysis."""
    prompt = f"Detect the language and translate this to English. Return only the translated text: {text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# In agents.py

def agent_extractor(transcript):
    system_instruction = (
        "You are the 'Literal Extractor'. Pull facts into a STRICT JSON format. "
        "Do NOT create lists or new keys. "
        "Use ONLY these keys: 'name', 'location', 'complaint', 'category'. "
        "For 'category', choose from: 'electricity complaint', 'water complaint', 'legal complaint', 'other complaint'."
    )
    prompt = f"Analyze: '{transcript}'"
    response = model.generate_content([system_instruction, prompt])
    return response.text.strip('`json\n ')

def agent_auditor(extraction_json, transcript):
    system_instruction = (
        "You are the 'Critical Auditor'. Ensure the JSON follows this exact schema: "
        "{'name': '', 'location': '', 'complaint': '', 'category': ''}. "
        "If Agent A changed the structure (e.g., used 'facts' or 'complaint_category'), "
        "you MUST correct it back to the required schema. "
        "If schema is correct and facts are accurate, return 'VALID'."
    )
    prompt = f"Agent A Output: {extraction_json}\nRaw Transcript: {transcript}"
    response = model.generate_content([system_instruction, prompt])
    return response.text.strip()

def run_consensus_protocol(raw_voice_text):
    """
    Master A2A Handshake Protocol with strict categorization and 
    error handling for rate limits.
    """
    # 1. Standardize (A2A Prep)
    clean_transcript = translate_to_english(raw_voice_text)
    
    # 2. Agent A Proposal (The Extractor)
    draft = None
    for attempt in range(3):
        try:
            draft = agent_extractor(clean_transcript)
            break
        except exceptions.ResourceExhausted:
            time.sleep(2) # Wait for quota reset
            
    if not draft:
        return {"category": "other complaint"}, "Error: Agent A Timeout", clean_transcript

    # 3. Agent B Audit (The Handshake/Skeptic)
    audit = None
    for attempt in range(3):
        try:
            audit = agent_auditor(draft, clean_transcript)
            break
        except exceptions.ResourceExhausted:
            time.sleep(2)

    # 4. Final Logic & Fallback Safeguards
    valid_categories = ['electricity complaint', 'water complaint', 'legal complaint', 'other complaint']
    
    if audit and "VALID" in audit.upper():
        interaction_log = "Direct Consensus: Auditor verified findings."
        try:
            final_data = json.loads(draft)
        except:
            final_data = {"category": "other complaint", "error": "JSON Parse Fail"}
    else:
        interaction_log = "Reconciled: Auditor corrected Agent A's errors or ambiguity."
        try:
            # Extract JSON from Auditor's critique
            start = audit.find('{')
            end = audit.rfind('}') + 1
            final_data = json.loads(audit[start:end])
        except:
            # Fallback to Agent A's draft if Auditor JSON is broken
            try:
                final_data = json.loads(draft)
            except:
                final_data = {"category": "other complaint"}

    # --- STRICT CATEGORY ENFORCEMENT ---
    # This prevents the 'null' issue seen in your Firestore logs
    if final_data.get('category') not in valid_categories:
        final_data['category'] = 'other complaint'
            
    return final_data, interaction_log, clean_transcript