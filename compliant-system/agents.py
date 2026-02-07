import os
import json
import time
import google.generativeai as genai
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv
from google.api_core import exceptions

load_dotenv()

# Initialize Clients with error handling
try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
    print("✓ All AI clients initialized successfully")
except Exception as e:
    print(f"⚠ Client initialization error: {e}")
    raise

def safe_json_loads(text):
    """Helper to strip markdown backticks and parse JSON safely."""
    try:
        # Remove markdown formatting
        clean_text = text.replace("```json", "").replace("```", "").strip()
        
        # Try to find JSON object in the text
        if "{" in clean_text and "}" in clean_text:
            start = clean_text.index("{")
            end = clean_text.rindex("}") + 1
            clean_text = clean_text[start:end]
        
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw Text: {text[:200]}...")
        return None
    except Exception as e:
        print(f"Unexpected error in JSON parsing: {e}")
        return None

# --- EDUCATION ASSISTANT AGENTS ---

def run_edu_protocol(query, conversation_history=None):
    """
    Hybrid A2A + RAG Handshake:
    1. Groq (Llama 3.1) for fast routing.
    2. Tavily for live RAG when needed.
    3. Gemini 2.0 Flash for pedagogical responses.
    
    Args:
        query: User's question
        conversation_history: List of previous exchanges for context
    
    Returns:
        dict: {answer, status, follow_up}
    """
    try:
        # Build conversation context
        context_text = ""
        if conversation_history:
            context_text = "\n".join([
                f"Student: {item['query']}\nAssistant: {item['answer']}" 
                for item in conversation_history[-3:]  # Keep last 3 exchanges
            ])
        
        # Agent 1: Groq (Fast Router with retry)
        max_retries = 3
        fast_analysis = ""
        
        for attempt in range(max_retries):
            try:
                response = groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "Analyze if the student query needs web search for current facts/news/statistics (respond 'SEARCH') or can be answered with general knowledge (respond 'DIRECT'). Consider the query carefully."
                        },
                        {
                            "role": "user", 
                            "content": f"Query: {query}"
                        }
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.3,
                )
                fast_analysis = response.choices[0].message.content
                break
            except Exception as e:
                print(f"Groq attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    fast_analysis = "DIRECT"  # Fallback to direct response
                time.sleep(1)

        # Agent 2: Tavily (Search when needed)
        context = ""
        if "SEARCH" in fast_analysis.upper():
            try:
                search_result = tavily_client.search(
                    query=query, 
                    search_depth="advanced",
                    max_results=3
                )
                # Extract relevant content
                if search_result and 'results' in search_result:
                    context = "\n".join([
                        f"Source: {r.get('title', '')}\n{r.get('content', '')}" 
                        for r in search_result['results'][:3]
                    ])
                else:
                    context = str(search_result)
            except Exception as e:
                print(f"Tavily search error: {e}")
                context = "Search unavailable, using general knowledge."

        # Agent 3: Gemini (The Educator)
        audit_prompt = f"""You are an educational assistant for rural students in India. Be friendly, clear, and encouraging.

Previous conversation:
{context_text if context_text else "This is the start of the conversation."}

Current Student Query: {query}

{f"Web Search Results: {context}" if context else "No web search was performed."}

Instructions:
1. Answer the student's question clearly and simply
2. Use examples relevant to rural Indian context when helpful
3. If the question is too vague or you need more information, ask ONE specific follow-up question
4. Be encouraging and supportive

You MUST respond in this EXACT JSON format (no other text):
{{
    "answer": "your helpful answer here (2-4 sentences)",
    "status": "COMPLETE or NEED_INFO",
    "follow_up": "your follow-up question if status is NEED_INFO, otherwise empty string"
}}"""

        # Generate response with retry logic
        max_retries = 3
        result = None
        
        for attempt in range(max_retries):
            try:
                response = gemini_model.generate_content(
                    audit_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_output_tokens": 500,
                    }
                )
                
                result = safe_json_loads(response.text)
                
                # Validate the result
                if result and 'answer' in result and 'status' in result:
                    # Ensure follow_up exists
                    if 'follow_up' not in result:
                        result['follow_up'] = ""
                    
                    # Validate status
                    if result['status'] not in ['COMPLETE', 'NEED_INFO']:
                        result['status'] = 'COMPLETE'
                    
                    break
                else:
                    print(f"Invalid JSON structure on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"Gemini attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    # Final fallback
                    result = {
                        "answer": response.text if 'response' in locals() else "I'm having trouble processing your question. Could you please rephrase it?",
                        "status": "COMPLETE",
                        "follow_up": ""
                    }
                time.sleep(1)
        
        return result
        
    except Exception as e:
        print(f"Critical error in run_edu_protocol: {e}")
        return {
            "answer": "I apologize, I'm experiencing technical difficulties. Please try again.",
            "status": "COMPLETE",
            "follow_up": ""
        }

# --- COMPLAINT SYSTEM AGENTS ---

def translate_to_english(text):
    """Translate any language input to English"""
    try:
        prompt = f"""Detect the language and translate the following text to English. 
Return ONLY the English translation, nothing else.

Text: {text}"""
        
        response = gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0.3}
        )
        
        translation = response.text.strip()
        # Remove any markdown or extra formatting
        translation = translation.replace("```", "").strip()
        return translation
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original if translation fails

def agent_extractor(transcript):
    """Extract structured information from complaint transcript"""
    try:
        system = """You are a complaint data extractor. Extract the following information from the transcript:
- name: Person's name
- location: City, village, or area name
- complaint: Brief description of the issue
- category: Must be one of: 'electricity complaint', 'water complaint', 'legal complaint', 'other complaint'

Return ONLY valid JSON in this exact format:
{
    "name": "extracted name or 'Unknown'",
    "location": "extracted location or 'Unknown'",
    "complaint": "brief complaint description",
    "category": "one of the 4 categories"
}"""
        
        prompt = f"{system}\n\nTranscript: {transcript}"
        
        response = gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0.2}
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Extractor error: {e}")
        return json.dumps({
            "name": "Unknown",
            "location": "Unknown",
            "complaint": transcript[:100],
            "category": "other complaint"
        })

def agent_auditor(extraction_json, transcript):
    """Verify and fix extraction if needed"""
    try:
        system = """You are a quality auditor. Check if the JSON has these required fields with valid values:
- name (not empty)
- location (not empty)
- complaint (not empty)
- category (must be exactly one of: 'electricity complaint', 'water complaint', 'legal complaint', 'other complaint')

If the JSON is valid, respond with just: VALID

If invalid, fix it and return the corrected JSON in this exact format:
{
    "name": "corrected name",
    "location": "corrected location",
    "complaint": "corrected complaint",
    "category": "valid category"
}

Use the original transcript to fill missing information."""
        
        prompt = f"{system}\n\nExtracted JSON: {extraction_json}\n\nOriginal Transcript: {transcript}"
        
        response = gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0.1}
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Auditor error: {e}")
        return extraction_json  # Return original if audit fails

def run_consensus_protocol(raw_voice_text):
    """
    Process complaint through multi-agent system
    
    Returns:
        tuple: (final_data dict, log string, english_transcript string)
    """
    try:
        # Step 0: Translate to English
        clean_transcript = translate_to_english(raw_voice_text)
        print(f"Translated transcript: {clean_transcript}")
        
        # Step 1: Extract
        draft = agent_extractor(clean_transcript)
        print(f"Extracted: {draft}")
        
        # Step 2: Audit
        audit = agent_auditor(draft, clean_transcript)
        print(f"Audit result: {audit}")
        
        valid_categories = ['electricity complaint', 'water complaint', 'legal complaint', 'other complaint']
        
        # Parse the result
        if "VALID" in audit.upper():
            final_data = safe_json_loads(draft)
            log = "Direct consensus reached - extraction approved"
        else:
            final_data = safe_json_loads(audit)
            log = "Auditor corrected extraction errors"

        # Fallback for parsing failures
        if not final_data:
            print("JSON parsing failed, using fallback")
            final_data = {
                "name": "Unknown",
                "location": "Unknown",
                "complaint": clean_transcript[:200],
                "category": "other complaint"
            }
            log = "Fallback data used due to parsing error"

        # Validate category
        if final_data.get('category') not in valid_categories:
            final_data['category'] = 'other complaint'
        
        # Ensure all required fields exist
        final_data.setdefault('name', 'Unknown')
        final_data.setdefault('location', 'Unknown')
        final_data.setdefault('complaint', clean_transcript[:200])
        
        print(f"Final data: {final_data}")
        return final_data, log, clean_transcript
        
    except Exception as e:
        print(f"Critical error in consensus protocol: {e}")
        return {
            "name": "Unknown",
            "location": "Unknown",
            "complaint": raw_voice_text[:200],
            "category": "other complaint"
        }, f"Error: {str(e)}", raw_voice_text

def generate_summary_message(complaint_data, is_education=False):
    """Generate a summary message to send to the caller"""
    try:
        if is_education:
            return "Thank you for using our Education Assistant service. We hope we could help with your query. For more questions, call us anytime!"
        
        category = complaint_data.get('category', 'complaint')
        name = complaint_data.get('name', 'there')
        
        message = f"Hello {name}, your {category} has been registered successfully. "
        message += f"Reference details - Location: {complaint_data.get('location', 'Not specified')}. "
        message += "Our team will review and respond soon. Thank you for contacting us."
        
        return message
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Your request has been registered. Thank you for contacting us."

def generate_education_summary(conversation_history):
    """Generate detailed SMS summary with all Q&A from education session"""
    try:
        if not conversation_history:
            return "Thank you for using our Education Assistant!"
        
        message = "📚 Education Session Summary:\n\n"
        
        for i, exchange in enumerate(conversation_history, 1):
            question = exchange.get('query', 'N/A')
            answer = exchange.get('answer', 'N/A')
            
            # Limit answer to 200 chars for SMS
            if len(answer) > 200:
                answer = answer[:197] + "..."
            
            message += f"Q{i}: {question}\n"
            message += f"A{i}: {answer}\n\n"
        
        message += "Thank you for learning with us! Call anytime for more help."
        
        # SMS has 1600 char limit for concatenated messages
        if len(message) > 1600:
            message = message[:1597] + "..."
        
        return message
        
    except Exception as e:
        print(f"Error generating education summary: {e}")
        return "Thank you for using our Education Assistant service!"