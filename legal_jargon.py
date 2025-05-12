import json
import logging
import os
import re
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from openai import OpenAI
import anthropic_helper

legal_jargon = Blueprint('legal_jargon', __name__)

# Add cache for popular terms to reduce database load
POPULAR_TERMS_CACHE = None
POPULAR_TERMS_CACHE_TIME = None

# Initialize OpenAI client if API key is available
try:
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
    else:
        openai_client = None
        logging.warning("OPENAI_API_KEY not found in environment variables")
except Exception as e:
    openai_client = None
    logging.error(f"Error initializing OpenAI client: {str(e)}")

# Import our comprehensive dictionary of legal terms
from legal_terms_database import LEGAL_TERMS

# Pre-defined legal terms with explanations
# These serve as fallbacks when AI isn't available
# We're now using our comprehensive dictionary of terms
COMMON_LEGAL_TERMS = LEGAL_TERMS

@legal_jargon.route('/legal-translator', methods=['GET', 'POST'])
@login_required
def translator():
    """Page for translating legal jargon to plain language with fun explanations"""
    result = None
    term = None
    
    if request.method == 'POST':
        term = request.form.get('legal_term', '').strip().lower()
        if not term:
            flash('Please enter a legal term to translate.', 'warning')
        else:
            # Try to get explanation from AI or fallback to predefined
            result = get_term_explanation(term)
    
    return render_template(
        'legal_translator.html',
        result=result,
        term=term
    )

@legal_jargon.route('/api/translate-term', methods=['POST'])
@login_required
def api_translate_term():
    """AJAX endpoint for translating legal terms"""
    try:
        data = request.get_json(silent=True) or {}
        
        term = str(data.get('term', '')).strip().lower()
        if not term:
            return jsonify({'error': 'No term provided'}), 400
        
        result = get_term_explanation(term)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in api_translate_term: {str(e)}")
        return jsonify({'error': 'Server error processing request'}), 500
        
@legal_jargon.route('/api/popular-terms', methods=['GET'])
@login_required
def api_popular_terms():
    """AJAX endpoint for getting popular legal terms"""
    global POPULAR_TERMS_CACHE, POPULAR_TERMS_CACHE_TIME
    from models import LegalTerm
    from datetime import datetime, timedelta
    
    try:
        # Check if we have a recent cache
        if (POPULAR_TERMS_CACHE is not None and 
            POPULAR_TERMS_CACHE_TIME is not None and 
            POPULAR_TERMS_CACHE_TIME > datetime.now() - timedelta(minutes=10)):
            return jsonify(POPULAR_TERMS_CACHE)
            
        # Get popular terms from database
        popular_terms = LegalTerm.get_popular_terms(limit=10)
        
        # Format the response
        result = [{
            'id': term.id, 
            'term': term.term, 
            'search_count': term.search_count
        } for term in popular_terms]
        
        # Cache the result
        POPULAR_TERMS_CACHE = result
        POPULAR_TERMS_CACHE_TIME = datetime.now()
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in api_popular_terms: {str(e)}")
        return jsonify([]), 200  # Return empty array on error

@legal_jargon.route('/api/search-suggestions', methods=['GET'])
@login_required
def api_search_suggestions():
    """AJAX endpoint for getting term search suggestions"""
    from models import LegalTerm
    
    try:
        query = request.args.get('q', '').strip().lower()
        if not query or len(query) < 2:
            return jsonify([]), 200
            
        # Get similar terms from database
        similar_terms = LegalTerm.get_similar_terms(query, limit=5)
        
        # Format the response
        result = [{
            'id': term.id, 
            'term': term.term
        } for term in similar_terms]
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in api_search_suggestions: {str(e)}")
        return jsonify([]), 200  # Return empty array on error

def get_term_explanation(term):
    """Get explanation for a legal term using database, AI, or fallback to predefined terms"""
    from models import LegalTerm, db
    
    # First, check the database for the term
    db_term = LegalTerm.get_term(term)
    if db_term:
        # Increment search count
        LegalTerm.increment_search_count(db_term.id)
        # Return the explanation
        return db_term.to_dict()
    
    # Next, check if term is in our predefined list
    if term in COMMON_LEGAL_TERMS:
        # Store the predefined term in the database for future use
        try:
            term_data = COMMON_LEGAL_TERMS[term]
            LegalTerm.create_term(
                term=term,
                simple_explanation=term_data['simple_explanation'],
                fun_explanation=term_data['fun_explanation'],
                cartoon_description=term_data['cartoon_description'],
                ai_generated=False,
                verified=True
            )
        except Exception as e:
            logging.error(f"Error storing predefined term {term} in database: {str(e)}")
            
        return COMMON_LEGAL_TERMS[term]
    
    # Try to get explanation from OpenAI if the client is initialized
    explanation = None
    try:
        if openai_client is not None:
            explanation = get_openai_explanation(term)
            if explanation:
                # Store the AI-generated explanation in the database
                try:
                    LegalTerm.create_term(
                        term=term,
                        simple_explanation=explanation['simple_explanation'],
                        fun_explanation=explanation['fun_explanation'],
                        cartoon_description=explanation['cartoon_description'],
                        ai_generated=True,
                        verified=False
                    )
                except Exception as e:
                    logging.error(f"Error storing OpenAI explanation for {term} in database: {str(e)}")
                    
                return explanation
    except Exception as e:
        logging.error(f"Error getting OpenAI explanation: {str(e)}")
    
    # Try Anthropic as fallback
    try:
        if anthropic_helper.is_available():
            explanation = get_anthropic_explanation(term)
            if explanation:
                # Store the AI-generated explanation in the database
                try:
                    LegalTerm.create_term(
                        term=term,
                        simple_explanation=explanation['simple_explanation'],
                        fun_explanation=explanation['fun_explanation'],
                        cartoon_description=explanation['cartoon_description'],
                        ai_generated=True,
                        verified=False
                    )
                except Exception as e:
                    logging.error(f"Error storing Anthropic explanation for {term} in database: {str(e)}")
                    
                return explanation
    except Exception as e:
        logging.error(f"Error getting Anthropic explanation: {str(e)}")
    
    # If term is not in predefined list and AI fails, provide a generic response
    generic_response = {
        "simple_explanation": "This legal term isn't in our database yet.",
        "fun_explanation": "Even our legal experts are scratching their heads on this one! Try another term or check a legal dictionary.",
        "cartoon_description": "A cartoon of a confused judge, lawyer, and client all looking at a giant question mark."
    }
    
    return generic_response

def get_openai_explanation(term):
    """Get explanation from OpenAI"""
    # Check if OpenAI client is available
    if not openai_client:
        logging.warning("OpenAI client not available when called in get_openai_explanation")
        return None
        
    try:
        prompt = f"""You are a helpful legal expert with a knack for explaining complex legal concepts in simple terms.

Please explain the legal term "{term}" in three ways:

1. Simple explanation: A clear, straightforward explanation that anyone can understand
2. Fun explanation: A playful, analogy-based explanation that makes the concept memorable
3. Cartoon description: A brief description of what a cartoon illustrating this concept might look like (should be humorous)

Format your response as a JSON object with these keys: "simple_explanation", "fun_explanation", and "cartoon_description".

Example:
{{
  "simple_explanation": "A legal principle that means...",
  "fun_explanation": "It's like when you...",
  "cartoon_description": "A cartoon showing..."
}}

If this is not actually a legal term or concept, clearly indicate that and provide a general response.
"""

        response = openai_client.chat.completions.create(
            model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant that explains legal concepts simply."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=500
        )
        
        if response.choices and response.choices[0].message.content:
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # If not valid JSON, extract as much as possible
                content = response.choices[0].message.content
                simple = re.search(r'"simple_explanation":\s*"([^"]+)"', content)
                fun = re.search(r'"fun_explanation":\s*"([^"]+)"', content)
                cartoon = re.search(r'"cartoon_description":\s*"([^"]+)"', content)
                
                return {
                    "simple_explanation": simple.group(1) if simple else "Explanation unavailable",
                    "fun_explanation": fun.group(1) if fun else "Fun explanation unavailable",
                    "cartoon_description": cartoon.group(1) if cartoon else "Cartoon description unavailable"
                }
    except Exception as e:
        logging.error(f"Error in OpenAI explanation: {str(e)}")
        return None

def get_anthropic_explanation(term):
    """Get explanation from Anthropic"""
    try:
        prompt = f"""You are a helpful legal expert with a knack for explaining complex legal concepts in simple terms.

Please explain the legal term "{term}" in three ways:

1. Simple explanation: A clear, straightforward explanation that anyone can understand (1-2 sentences)
2. Fun explanation: A playful, analogy-based explanation that makes the concept memorable (1-2 sentences)
3. Cartoon description: A brief description of what a cartoon illustrating this concept might look like (should be humorous, 1-2 sentences)

Format your response precisely with simple_explanation: followed by your explanation, then fun_explanation: followed by that explanation, then cartoon_description: followed by that description. No other text.

If this is not actually a legal term or concept, clearly indicate that and provide a general response using the same format.
"""

        response = anthropic_helper.analyze_case_text(prompt)
        if response:
            # Parse structured text into a dict
            simple_match = re.search(r'simple_explanation:(.*?)(?=fun_explanation:|$)', response, re.DOTALL)
            fun_match = re.search(r'fun_explanation:(.*?)(?=cartoon_description:|$)', response, re.DOTALL)
            cartoon_match = re.search(r'cartoon_description:(.*?)(?=$)', response, re.DOTALL)
            
            return {
                "simple_explanation": simple_match.group(1).strip() if simple_match else "Explanation unavailable",
                "fun_explanation": fun_match.group(1).strip() if fun_match else "Fun explanation unavailable",
                "cartoon_description": cartoon_match.group(1).strip() if cartoon_match else "Cartoon description unavailable"
            }
    except Exception as e:
        logging.error(f"Error in Anthropic explanation: {str(e)}")
        return None