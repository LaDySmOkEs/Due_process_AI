"""
Audio processing module for evidence transcription and analysis
"""
import os
import json
from openai import OpenAI
from anthropic import Anthropic
from datetime import datetime

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Initialize the Anthropic client as a fallback
try:
    anthropic_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    anthropic_available = True
except Exception as e:
    print(f"Warning: Anthropic client initialization failed: {e}")
    anthropic_available = False

def transcribe_audio(file_path):
    """
    Transcribe audio or video file using OpenAI's Whisper model
    Returns a dict with the transcript and metadata
    
    This function works with both audio (mp3, wav, etc.) and video (mp4, mov, etc.) files
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": "Audio file not found",
            "transcript": None
        }
    
    try:
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        return {
            "success": True,
            "transcript": transcription.text,
            "processed_at": datetime.utcnow().isoformat(),
            "model": "whisper-1"
        }
    
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "transcript": None
        }

def analyze_transcript(transcript, case_description, issue_type, court_type):
    """
    Analyze an audio transcript for relevant legal claims and evidence
    Returns a structured analysis of key points, claims, and relevance
    """
    if not transcript:
        return None
    
    try:
        # Prepare the analysis prompt
        system_prompt = """You are an expert legal investigator analyzing audio evidence transcripts.
Analyze this audio transcript for a legal case and return ONLY a JSON object with the following structure:
{
  "key_points": [array of 3-5 key points from the transcript],
  "legal_claims": [array of legal claims or assertions from the transcript],
  "relevance": "a paragraph explaining how this audio relates to the case",
  "actionable_insights": "strategic recommendations based on this evidence"
}

Only include these exact fields: key_points, legal_claims, relevance, and actionable_insights.
Never include additional fields or other text outside the JSON structure."""

        user_prompt = f"""Analyze this transcript from an audio recording related to a legal case:

CASE DESCRIPTION: {case_description}
ISSUE TYPE: {issue_type}
COURT TYPE: {court_type}

TRANSCRIPT:
{transcript}

Return ONLY a properly formatted JSON object with key_points, legal_claims, relevance, and actionable_insights."""

        try:
            # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis_json = response.choices[0].message.content
            try:
                analysis = json.loads(analysis_json)
                # Ensure we have all required fields with defaults if missing
                if "key_points" not in analysis:
                    analysis["key_points"] = ["No key points identified"]
                if "legal_claims" not in analysis:
                    analysis["legal_claims"] = ["No specific legal claims identified"]
                if "relevance" not in analysis:
                    analysis["relevance"] = "The relevance to the case could not be determined."
                if "actionable_insights" not in analysis:
                    analysis["actionable_insights"] = "No specific actionable insights could be determined."
                return analysis
            except json.JSONDecodeError:
                # If we can't parse the JSON, create a structured response anyway
                return {
                    "key_points": ["Error parsing analysis"],
                    "legal_claims": ["Could not extract legal claims"],
                    "relevance": "The system encountered an error analyzing this transcript.",
                    "actionable_insights": "Please try regenerating the analysis or contact support if the issue persists."
                }
        except Exception as openai_error:
            print(f"OpenAI analysis failed, trying Anthropic fallback: {str(openai_error)}")
            
            # Fallback to Anthropic if available
            if anthropic_available:
                # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024.
                # do not change this unless explicitly requested by the user
                response = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    system=system_prompt,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                try:
                    # Try to parse as JSON
                    analysis = json.loads(response.content[0].text)
                    # Ensure we have all required fields with defaults if missing
                    if "key_points" not in analysis:
                        analysis["key_points"] = ["No key points identified"]
                    if "legal_claims" not in analysis:
                        analysis["legal_claims"] = ["No specific legal claims identified"]
                    if "relevance" not in analysis:
                        analysis["relevance"] = "The relevance to the case could not be determined."
                    if "actionable_insights" not in analysis:
                        analysis["actionable_insights"] = "No specific actionable insights could be determined."
                    return analysis
                except json.JSONDecodeError:
                    # If we can't parse the JSON, create a structured response anyway
                    return {
                        "key_points": ["Error parsing analysis"],
                        "legal_claims": ["Could not extract legal claims"],
                        "relevance": "The system encountered an error analyzing this transcript.",
                        "actionable_insights": "Please try regenerating the analysis or contact support if the issue persists."
                    }
            
            # If we got here, both OpenAI and Anthropic failed
            return {
                "key_points": ["Analysis failed"],
                "legal_claims": ["Unable to analyze audio transcript"],
                "relevance": "The system encountered an error while analyzing this transcript.",
                "actionable_insights": "Please try regenerating the analysis or contact support if the issue persists."
            }
    
    except Exception as e:
        print(f"Error analyzing transcript: {str(e)}")
        return {
            "key_points": ["System error occurred"],
            "legal_claims": ["Unable to analyze audio transcript"],
            "relevance": "The system encountered an error while analyzing this transcript.",
            "actionable_insights": "Please try regenerating the analysis or contact support if the issue persists."
        }