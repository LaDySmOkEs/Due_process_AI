import os
import sys
import json
import logging
from anthropic import Anthropic

# Initialize the client
anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
client = None

if anthropic_key:
    client = Anthropic(api_key=anthropic_key)

# The newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

def is_available():
    """Check if Anthropic API is configured and available"""
    return client is not None

def analyze_case_text(prompt, json_format=False):
    """Analyze text using Anthropic's Claude"""
    if not is_available():
        logging.error("Anthropic API is not available - missing API key")
        return None
    
    try:
        system_message = "You are a highly skilled legal assistant analyzing case details and providing accurate, helpful legal information."
        
        if json_format:
            system_message += " Respond with a valid JSON object only."
        
        # Ensure client is initialized
        if client is None:
            logging.error("Anthropic client is None - cannot make API call")
            return None
            
        logging.debug(f"Calling Anthropic API with model: {DEFAULT_MODEL}")
        
        try:
            # Call the Anthropic API
            response = client.messages.create(
                model=DEFAULT_MODEL,
                system=system_message,
                max_tokens=1500,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the text content from the response
            content = ""
            if hasattr(response, 'content') and isinstance(response.content, list):
                for item in response.content:
                    if hasattr(item, 'type') and item.type == 'text':
                        content = item.text
                        break
            
            # If we couldn't get content, use the string representation
            if not content:
                content = str(response)
                
            logging.debug("Successfully received content from Anthropic API")
            
        except Exception as api_error:
            error_msg = str(api_error)
            logging.error(f"Error with Anthropic API: {error_msg}")
            
            # Try a fallback model if the requested model wasn't found
            if "not_found_error" in error_msg and "model" in error_msg:
                fallback_model = "claude-3-opus-20240229"
                logging.warning(f"Trying fallback model: {fallback_model}")
                
                try:
                    response = client.messages.create(
                        model=fallback_model,
                        system=system_message,
                        max_tokens=1500,
                        temperature=0.2,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    # Extract content from the fallback response
                    content = ""
                    if hasattr(response, 'content') and isinstance(response.content, list):
                        for item in response.content:
                            if hasattr(item, 'type') and item.type == 'text':
                                content = item.text
                                break
                    
                    # If still no content, use string representation
                    if not content:
                        content = str(response)
                        
                    logging.info("Successfully received content using fallback model")
                    
                except Exception as fallback_error:
                    logging.error(f"Fallback model also failed: {fallback_error}")
                    return None
            else:
                # For other types of errors, return None
                return None
        
        # Process the content if JSON format was requested
        if json_format and content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract a JSON object from the content
                import re
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except:
                        logging.warning("Could not parse extracted JSON-like content")
                
                # If we still don't have valid JSON, return a structured error
                logging.warning("Failed to parse content as JSON")
                return {
                    "error": "Invalid JSON response",
                    "raw_content": content[:200] if len(content) > 200 else content
                }
        
        return content
        
    except Exception as e:
        logging.error(f"Unexpected error in analyze_case_text: {e}")
        return None


def analyze_rights_violations(description, issue_type, court_type):
    """Analyze potential rights violations in a case"""
    if not description or not issue_type or not court_type:
        logging.error("Missing required parameters for rights violation analysis")
        return {
            "rights_violations": [
                {
                    "right_violated": "Incomplete Information",
                    "explanation": "Not enough case details were provided for analysis.",
                    "severity": "N/A",
                    "supporting_legal_principle": "Additional case information required for legal analysis."
                }
            ]
        }
    
    prompt = f"""
    Analyze this legal case description and identify any potential violations of rights related to probable cause issues
    and Fourth Amendment protections. Create analysis so simple that ANYONE can use it to defend themselves without 
    relying on public defenders who are paid by the same entity as prosecutors and judges.
    Format your response as JSON with the following structure:
    
    {{
        "rights_violations": [
            {{
                "right_violated": "Name of the specific right (focus on probable cause and 4th Amendment issues)",
                "explanation": "Brief description of the potential violation showing why probable cause may be invalid",
                "supporting_legal_principle": "Constitutional amendment, statute, or case law basis related to probable cause standards",
                "severity": "High/Medium/Low"
            }}
        ]
    }}
    
    Case details:
    Issue type: {issue_type}
    Court type: {court_type}
    Description: {description}
    
    If you don't identify any potential rights violations, return an empty array for "rights_violations".
    """
    
    try:
        result = analyze_case_text(prompt, json_format=True)
        
        # Ensure we return a dict with the expected structure even if API call fails
        if not result or not isinstance(result, dict):
            logging.error("Rights violation analysis returned invalid result")
            return {"rights_violations": []}
        
        # If the result doesn't have the expected format, return an empty structure
        if "rights_violations" not in result:
            logging.warning("Rights violation response missing expected key 'rights_violations'")
            # Try to adjust the structure if needed (Claude might return a different format)
            if "violations" in result:
                result["rights_violations"] = result.pop("violations")
            else:
                result["rights_violations"] = []
        
        return result
    except Exception as e:
        logging.error(f"Error in analyze_rights_violations: {str(e)}")
        return {"rights_violations": []}

def recommend_documents(description, issue_type, court_type):
    """Recommend documents for a case"""
    if not description or not issue_type or not court_type:
        logging.error("Missing required parameters for document recommendations")
        return {
            "recommended_documents": [
                {
                    "document_type": "Missing Information",
                    "purpose": "Cannot generate recommendations with incomplete information",
                    "strategic_value": "Please provide complete case details",
                    "timing": "N/A",
                    "key_elements": ["Additional case information required"],
                    "priority": "N/A"
                }
            ]
        }
        
    prompt = f"""
    Based on this legal case description, recommend the most effective legal documents 
    that attack BOTH probable cause AND speedy trial rights violations to get a criminal case dismissed.
    Create document instructions so simple and straightforward that even someone with no legal 
    training could successfully prepare and file them. Format your response as JSON with the following structure:
    
    {{
        "recommended_documents": [
            {{
                "document_type": "Name of the document",
                "purpose": "What this document aims to accomplish",
                "strategic_value": "Why this document is important for the case",
                "timing": "When this should be filed for maximum effect",
                "key_elements": ["Important elements to include in this document"],
                "priority": "High/Medium/Low"
            }}
        ]
    }}
    
    Case details:
    Issue type: {issue_type}
    Court type: {court_type}
    Description: {description}
    """
    
    try:
        result = analyze_case_text(prompt, json_format=True)
        
        # Ensure we return a dict with the expected structure even if API call fails
        if not result or not isinstance(result, dict):
            logging.error("Document recommendation analysis returned invalid result")
            return {"recommended_documents": []}
        
        # If the result doesn't have the expected format, return an empty structure
        if "recommended_documents" not in result:
            logging.warning("Document recommendation response missing expected key 'recommended_documents'")
            # Try to adjust the structure if needed (Claude might return a different format)
            if "documents" in result:
                result["recommended_documents"] = result.pop("documents")
            else:
                result["recommended_documents"] = []
        
        return result
    except Exception as e:
        logging.error(f"Error in recommend_documents: {str(e)}")
        return {"recommended_documents": []}

def suggest_case_law(description, issue_type, court_type):
    """Suggest relevant case law"""
    if not description or not issue_type or not court_type:
        logging.error("Missing required parameters for case law suggestions")
        return {
            "relevant_cases": [
                {
                    "case_name": "Missing Information",
                    "key_holding": "Cannot suggest relevant case law with incomplete information",
                    "relevance": "Please provide complete case details",
                    "jurisdiction": "N/A",
                    "strength": "N/A"
                }
            ]
        }
        
    prompt = f"""
    Analyze this legal case and suggest the most powerful case law precedents related to
    BOTH probable cause challenges AND speedy trial rights violations that could help dismiss a criminal case.
    Focus on landmark Supreme Court decisions that any defendant could easily cite to win their case.
    Explain these cases in simple terms that anyone could understand and use in court.
    Format your response as JSON with the following structure:
    
    {{
        "relevant_cases": [
            {{
                "case_name": "Full case citation",
                "key_holding": "The main legal principle established by this case",
                "relevance": "Specifically how this applies to the current case",
                "jurisdiction": "The court that decided this case",
                "strength": "How strongly this supports the client's position (Strong/Moderate/Limited)"
            }}
        ]
    }}
    
    Case details:
    Issue type: {issue_type}
    Court type: {court_type}
    Description: {description}
    """
    
    try:
        result = analyze_case_text(prompt, json_format=True)
        
        # Ensure we return a dict with the expected structure even if API call fails
        if not result or not isinstance(result, dict):
            logging.error("Case law suggestion analysis returned invalid result")
            return {"relevant_cases": []}
        
        # If the result doesn't have the expected format, return an empty structure
        if "relevant_cases" not in result:
            logging.warning("Case law suggestion response missing expected key 'relevant_cases'")
            # Try to adjust the structure if needed (Claude might return a different format)
            if "cases" in result:
                result["relevant_cases"] = result.pop("cases")
            elif "case_law" in result:
                result["relevant_cases"] = result.pop("case_law")
            else:
                result["relevant_cases"] = []
        
        return result
    except Exception as e:
        logging.error(f"Error in suggest_case_law: {str(e)}")
        return {"relevant_cases": []}

def analyze_evidence_relevance(description, issue_type, court_type, evidence_descriptions):
    """Analyze evidence for relevance to the case"""
    if not description or not issue_type or not court_type or not evidence_descriptions:
        logging.error("Missing required parameters for evidence relevance analysis")
        return {
            "evidence_analysis": [
                {
                    "evidence_id": 0,
                    "relevance_score": "N/A",
                    "key_points": ["Missing information - cannot analyze evidence relevance"]
                }
            ]
        }
        
    prompt = f"""
    You are an expert legal evidence analyst tasked with identifying opportunities to SUPPRESS EVIDENCE
    using the "fruit of the poisonous tree" doctrine. Create step-by-step instructions so simple that
    ANYONE can get evidence thrown out without legal training.
    
    CASE DETAILS:
    Description: {description}
    Issue Type: {issue_type}
    Court Type: {court_type}
    
    EVIDENCE ITEMS:
    {json.dumps(evidence_descriptions, indent=2)}
    
    For each piece of evidence, assess:
    1. Whether it's suppressible under "fruit of the poisonous tree" doctrine (High/Medium/Low likelihood)
    2. The exact initial "poisonous tree" violation that makes this evidence illegal
    3. Precise language to use in a motion to suppress this evidence
    4. How this evidence connects to other evidence that should also be suppressed as "fruit"
    5. Supreme Court cases supporting suppression that anyone can cite without a lawyer
    
    Format your response as a JSON object structured like this:
    {{
      "evidence_analysis": [
        {{
          "evidence_id": 1,
          "relevance_score": "High",
          "key_points": [
            "This evidence directly supports the plaintiff's claim of damages",
            "Establishes timeline of events crucial to determining liability",
            "Contains specific information that contradicts defendant's statements"
          ],
          "strategic_value": "Use this evidence to establish the factual basis for your claim",
          "presentation_recommendations": "Present early to establish context for the case"
        }}
      ]
    }}
    
    Provide detailed, legally sound analysis for each piece of evidence that could help strengthen the case.
    """
    
    try:
        result = analyze_case_text(prompt, json_format=True)
        
        # Ensure we return a dict with the expected structure even if API call fails
        if not result or not isinstance(result, dict):
            logging.error("Evidence analysis returned invalid result")
            return {"evidence_analysis": []}
        
        # If the result doesn't have the expected format, return an empty structure
        if "evidence_analysis" not in result:
            logging.warning("Evidence analysis response missing expected key 'evidence_analysis'")
            # Try to adjust the structure if needed (Claude might return a different format)
            if "analysis" in result:
                result["evidence_analysis"] = result.pop("analysis")
            else:
                result["evidence_analysis"] = []
        
        return result
    except Exception as e:
        logging.error(f"Error in analyze_evidence_relevance: {str(e)}")
        return {"evidence_analysis": []}

def organize_exhibits(description, issue_type, court_type, relevance_analysis):
    """Organize evidence into logical exhibit groups for court presentation"""
    if not description or not issue_type or not court_type or not relevance_analysis:
        logging.error("Missing required parameters for exhibit organization")
        return {
            "exhibit_plan": [
                {
                    "exhibit_group": "Missing Information",
                    "strategic_purpose": "Cannot organize exhibits with incomplete information",
                    "evidence_items": [],
                    "presentation_order": "N/A",
                    "introduction_strategy": "Please provide complete case details"
                }
            ]
        }
        
    prompt = f"""
    You are an expert legal strategist creating a battle plan anyone can use to win their case without a lawyer.
    Organize evidence to expose the inherent conflict of interest in a system where public defenders,
    prosecutors and judges are all paid by the same entity.
    
    CASE DETAILS:
    Description: {description}
    Issue Type: {issue_type}
    Court Type: {court_type}
    
    EVIDENCE RELEVANCE ANALYSIS:
    {json.dumps(relevance_analysis, indent=2)}
    
    Create a simple step-by-step plan that ANYONE can follow to win their case by:
    1. Organizing evidence into groups that attack BOTH probable cause AND speedy trial violations
    2. Creating a presentation order so compelling even a child could understand it
    3. Providing exact wording to use when introducing each exhibit in court
    4. Explaining how each evidence group exposes the system's built-in conflicts of interest
    5. Showing exactly how to present timeline evidence to prove speedy trial violations
    
    Format your response as a JSON object structured like this:
    {{
      "exhibit_plan": [
        {{
          "exhibit_group": "A: Timeline Evidence",
          "strategic_purpose": "Establishes clear chronology of events leading to the dispute",
          "evidence_items": [3, 1, 5],
          "presentation_order": "Chronological",
          "introduction_strategy": "Begin with these exhibits to create a foundation for the case narrative",
          "key_points_to_emphasize": [
            "Note the timestamps on documents",
            "Highlight the sequence of communications",
            "Emphasize time between incidents and responses"
          ]
        }},
        ...additional exhibit groups...
      ]
    }}
    
    Create a comprehensive, strategic exhibit organization that would maximize persuasiveness and clarity in court.
    """
    
    try:
        result = analyze_case_text(prompt, json_format=True)
        
        # Ensure we return a dict with the expected structure even if API call fails
        if not result or not isinstance(result, dict):
            logging.error("Exhibit organization returned invalid result")
            return {"exhibit_plan": []}
        
        # If the result doesn't have the expected format, return an empty structure
        if "exhibit_plan" not in result:
            logging.warning("Exhibit organization response missing expected key 'exhibit_plan'")
            # Try to adjust the structure if needed (Claude might return a different format)
            if "exhibits" in result:
                result["exhibit_plan"] = result.pop("exhibits")
            elif "plan" in result:
                result["exhibit_plan"] = result.pop("plan")
            else:
                result["exhibit_plan"] = []
        
        return result
    except Exception as e:
        logging.error(f"Error in organize_exhibits: {str(e)}")
        return {"exhibit_plan": []}