"""
AI Helper Functions - Simplified version to get the application running
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)

# Import Anthropic helper for fallback
import anthropic_helper

# Configure OpenAI
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    MODEL = "gpt-4o"  # Using the most capable model
except ImportError:
    logging.warning("OpenAI SDK not found, some AI features may be limited")
    client = None
    MODEL = None

def fallback_to_anthropic(description, issue_type, court_type):
    """
    Try to use Anthropic's Claude as a fallback when OpenAI is unavailable or fails
    """
    logging.info("Using Anthropic fallback")
    
    try:
        if anthropic_helper.is_available():
            # Use Anthropic's Claude for rights violations analysis
            rights_result = anthropic_helper.analyze_rights_violations(description, issue_type, court_type)
            
            # Use Anthropic for case law suggestions
            case_law_result = anthropic_helper.suggest_case_law(description, issue_type, court_type)
            
            if rights_result and case_law_result:
                # Combine the results
                rights_violations = []
                if isinstance(rights_result, dict) and "rights_violations" in rights_result:
                    rights_violations = rights_result["rights_violations"]
                
                relevant_cases = []
                if isinstance(case_law_result, dict) and "relevant_cases" in case_law_result:
                    relevant_cases = case_law_result["relevant_cases"]
                
                # Create a winning strategy structure
                winning_strategy = {
                    "primary_approach": "Comprehensive legal strategy",
                    "attack_defense_tactics": [
                        "Challenge evidence and procedural issues",
                        "Focus on constitutional protections",
                        "Build multiple defense layers"
                    ],
                    "procedural_motions": [
                        "File discovery motions",
                        "Submit relevant suppression motions",
                        "Consider strategic timing"
                    ],
                    "evidence_challenges": "Challenge evidence based on constitutional grounds",
                    "hearing_objections": "Make strategic objections during hearings",
                    "timing_strategy": "Deploy legal maneuvers in strategic sequence"
                }
                
                combined_result = {
                    "rights_assessment": rights_violations,
                    "case_law_suggestions": relevant_cases,
                    "winning_strategy": winning_strategy
                }
                
                logging.info("Successfully used Anthropic as fallback")
                return combined_result
    except Exception as e:
        logging.error(f"Anthropic fallback error: {str(e)}")
    
    # Default fallback
    return {
        "rights_assessment": [
            {
                "right_violated": "AI Analysis Limited",
                "explanation": "Our analysis system is currently limited. Consider adding your API key for full functionality.",
                "severity": "N/A",
                "supporting_legal_principle": "We recommend setting up an API key or consulting with a legal professional."
            }
        ],
        "case_law_suggestions": [],
        "winning_strategy": {
            "primary_approach": "API Configuration Required",
            "attack_defense_tactics": [
                "Configure API key for unlimited analysis",
                "Visit Settings to add your API credentials"
            ],
            "procedural_motions": ["Add API key in Settings"],
            "evidence_challenges": "Full analysis available after API configuration",
            "timing_strategy": "Configure API keys and retry analysis"
        }
    }

def analyze_case_description(description, issue_type, court_type):
    """
    Analyze a case description and suggest relevant case law.
    Returns a dictionary with case law suggestions, rights violations, and explanations.
    """
    # Check for missing parameters
    if not description or not issue_type or not court_type:
        logging.error("Missing required parameters for case analysis")
        return {
            "rights_assessment": [
                {
                    "right_violated": "Incomplete Information",
                    "explanation": "Complete case details needed for accurate analysis",
                    "severity": "N/A",
                    "supporting_legal_principle": "Please provide complete case information"
                }
            ],
            "case_law_suggestions": [],
            "winning_strategy": {
                "primary_approach": "Additional Information Required",
                "attack_defense_tactics": ["More case details needed"],
                "procedural_motions": ["Please provide complete case description"],
                "evidence_challenges": "Analysis requires full case details",
                "hearing_objections": "Complete information needed",
                "timing_strategy": "Update information and retry analysis"
            }
        }
    
    try:
        # For tribal court cases, check for special considerations
        if 'tribal' in court_type.lower() or 'cfr' in court_type.lower():
            logging.info("Tribal court case detected, applying specialized analysis")
            
            # Import tribal helper functions
            try:
                import tribal_court_helper
                tribal_analysis = tribal_court_helper.analyze_tribal_case(description, issue_type, court_type)
                if tribal_analysis:
                    return tribal_analysis
            except ImportError:
                logging.warning("Tribal court helper not available, using standard analysis")
        
        # Check if OpenAI is configured
        if not client or not MODEL:
            logging.error("OpenAI API not configured")
            return fallback_to_anthropic(description, issue_type, court_type)
        
        # Customize prompt based on case type
        is_criminal = issue_type.lower() == "criminal"
        is_civil = issue_type.lower() in ["civil", "personal_injury", "housing"]
        is_family = issue_type.lower() == "family"
        is_contract = issue_type.lower() == "contract"
        is_bankruptcy = issue_type.lower() == "bankruptcy" 
        is_immigration = issue_type.lower() == "immigration"
        
        # Base prompt that works for any case type
        prompt = f"""Analyze this legal case in a neutral and objective manner, identifying key legal issues and relevant case law:
        
        Case Description: {description}
        Issue Type: {issue_type}
        Court Type: {court_type}
        
        Provide your analysis in JSON format with rights_assessment, case_law_suggestions, and winning_strategy sections tailored to this specific type of case."""
        
        # Add specialized instructions based on case type
        if is_criminal:
            prompt += """
            
            For criminal cases, focus on:
            - Constitutional rights violations (4th, 5th, 6th Amendments)
            - Procedural and evidence collection issues
            - Criminal procedure and defense strategy"""
        elif is_civil:
            prompt += """
            
            For civil cases, focus on:
            - Relevant statutory and civil rights
            - Procedural standards for civil litigation
            - Burden of proof considerations
            - Elements of applicable civil claims or defenses"""
        elif is_family:
            prompt += """
            
            For family law cases, focus on:
            - Relevant family law statutes and standards
            - Best interest of child considerations if applicable
            - Procedural requirements for family court
            - Equitable distribution principles if relevant"""
        elif is_contract:
            prompt += """
            
            For contract disputes, focus on:
            - Contract formation and validity issues
            - Breach of contract elements
            - Potential remedies and damages
            - Contract interpretation principles"""
        elif is_bankruptcy:
            prompt += """
            
            For bankruptcy matters, focus on:
            - Applicable bankruptcy code provisions
            - Debtor protections and obligations
            - Creditor rights and limitations
            - Asset protection strategies"""
        elif is_immigration:
            prompt += """
            
            For immigration cases, focus on:
            - Relevant immigration statutes and regulations
            - Procedural rights in immigration proceedings
            - Strategic options for the specific immigration issue
            - Potential remedies or relief available"""
        
        # Attempt to call OpenAI
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a legal expert providing case analysis."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            if content:
                try:
                    result = json.loads(content)
                    return result
                except json.JSONDecodeError:
                    logging.error("Failed to parse OpenAI response as JSON")
                    return fallback_to_anthropic(description, issue_type, court_type)
            else:
                return fallback_to_anthropic(description, issue_type, court_type)
                
        except Exception:
            logging.error("OpenAI API error")
            return fallback_to_anthropic(description, issue_type, court_type)
            
    except Exception as e:
        logging.error(f"Error in analyze_case_description: {str(e)}")
        return fallback_to_anthropic(description, issue_type, court_type)

def recommend_documents(description, issue_type, court_type):
    """
    Recommend documents for a case based on its description.
    Returns a dictionary with document recommendations.
    """
    # Check for missing parameters
    if not description or not issue_type or not court_type:
        logging.error("Missing required parameters for document recommendations")
        return {
            "document_recommendations": [
                {
                    "document_type": "Incomplete Information",
                    "rationale": "Cannot generate recommendations with incomplete case details",
                    "strategic_guidance": "Please provide full case information",
                    "key_elements": ["Additional case information required"],
                    "timing": "N/A",
                    "importance": "N/A",
                    "impact": "N/A"
                }
            ]
        }
    
    try:
        # For tribal cases, use specialized recommendations
        if 'tribal' in court_type.lower() or 'cfr' in court_type.lower():
            try:
                import tribal_court_helper
                tribal_docs = tribal_court_helper.recommend_tribal_documents(description, issue_type, court_type)
                if tribal_docs:
                    return tribal_docs
            except ImportError:
                logging.warning("Tribal court helper not available, using standard recommendations")
        
        # Check if OpenAI is configured
        if not client or not MODEL:
            logging.error("OpenAI API not configured for document recommendations")
            # Try fallback
            try:
                if anthropic_helper.is_available():
                    doc_result = anthropic_helper.recommend_documents(description, issue_type, court_type)
                    if doc_result:
                        return doc_result
            except Exception:
                pass
            
            # Default fallback
            return {
                "document_recommendations": [
                    {
                        "document_type": "API Configuration Required",
                        "rationale": "Document recommendation system requires API configuration",
                        "strategic_guidance": "Please configure API key in settings",
                        "key_elements": ["API configuration needed"],
                        "timing": "N/A",
                        "importance": "N/A",
                        "impact": "N/A"
                    }
                ]
            }
        
        # Customize prompt based on case type
        is_criminal = issue_type.lower() == "criminal"
        is_civil = issue_type.lower() in ["civil", "personal_injury", "housing"]
        is_family = issue_type.lower() == "family"
        is_contract = issue_type.lower() == "contract"
        is_bankruptcy = issue_type.lower() == "bankruptcy" 
        is_immigration = issue_type.lower() == "immigration"
        
        # Base prompt that works for any case type
        prompt = f"""You are a legal document specialist. Recommend appropriate legal documents for this case:
        
        Case Description: {description}
        Issue Type: {issue_type}
        Court Type: {court_type}
        
        For each document, include:
        - Document name
        - Why it's important for this specific case
        - Strategic guidance on preparing it
        - Key elements to include
        - Timing considerations
        - Importance level
        
        Provide your recommendations in JSON format with a document_recommendations array."""
        
        # Add specialized instructions based on case type
        if is_criminal:
            prompt += """
            
            For criminal cases, focus on documents such as:
            - Motions to suppress evidence
            - Brady motions
            - Motions to dismiss based on procedural issues
            - Discovery requests for police records
            - Other documents relevant to criminal defense"""
        elif is_civil:
            prompt += """
            
            For civil cases, focus on documents such as:
            - Complaints and answers
            - Discovery requests and responses
            - Motions for summary judgment
            - Settlement demand letters
            - Other documents relevant to civil litigation"""
        elif is_family:
            prompt += """
            
            For family law cases, focus on documents such as:
            - Petitions for dissolution or separation
            - Custody and visitation motions
            - Financial declarations
            - Parenting plans
            - Other documents relevant to family court proceedings"""
        elif is_contract:
            prompt += """
            
            For contract disputes, focus on documents such as:
            - Breach of contract complaints
            - Motions related to contract interpretation
            - Discovery requests for contract documentation
            - Settlement proposals
            - Other documents relevant to contract litigation"""
        elif is_bankruptcy:
            prompt += """
            
            For bankruptcy matters, focus on documents such as:
            - Bankruptcy petitions
            - Schedules of assets and liabilities
            - Means test calculations
            - Motions for automatic stay
            - Other documents relevant to bankruptcy proceedings"""
        elif is_immigration:
            prompt += """
            
            For immigration cases, focus on documents such as:
            - Applications for specific immigration benefits
            - Motions to reopen or reconsider
            - Asylum applications
            - Appeals of immigration decisions
            - Other documents relevant to immigration proceedings"""
        
        # Call OpenAI
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a legal document specialist."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if content:
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                pass
        
        # Default response if parsing fails
        return {
            "document_recommendations": [
                {
                    "document_type": "Analysis System Limited",
                    "rationale": "The document recommendation system is currently limited",
                    "strategic_guidance": "Please try again later or provide more details",
                    "key_elements": ["Additional information may help"],
                    "timing": "N/A",
                    "importance": "N/A",
                    "impact": "N/A"
                }
            ]
        }
            
    except Exception as e:
        logging.error(f"Error in recommend_documents: {str(e)}")
        return {
            "document_recommendations": [
                {
                    "document_type": "System Error",
                    "rationale": "An error occurred during document analysis",
                    "strategic_guidance": "Please try again later",
                    "key_elements": ["System error occurred"],
                    "timing": "Try again later",
                    "importance": "N/A",
                    "impact": "N/A"
                }
            ]
        }

def generate_legal_strategy(case_id, description, issue_type, court_type, evidence_descriptions=None):
    """
    Generate a comprehensive legal strategy for a case.
    Returns a dictionary with strategy components.
    """
    try:
        # Import legal knowledge base here to avoid circular imports
        import legal_knowledge_base as lkb
        
        # Try OpenAI first
        if os.environ.get('OPENAI_API_KEY'):
            try:
                import openai
                from openai import OpenAI

                client = OpenAI(
                    api_key=os.environ.get('OPENAI_API_KEY')
                )
                
                # Adapt strategy prompt based on case type
                if issue_type.lower() == 'criminal':
                    system_prompt = "You are an expert criminal defense attorney with expertise in constitutional rights violations and procedural challenges."
                elif issue_type.lower() == 'civil':
                    system_prompt = "You are an expert civil rights attorney specializing in constitutional claims and procedural due process."
                elif issue_type.lower() == 'family':
                    system_prompt = "You are a family law specialist with expertise in custody disputes, domestic relations, and family court procedures."
                elif issue_type.lower() in ['contract', 'business']:
                    system_prompt = "You are a business law expert specializing in contract disputes, commercial litigation, and business remedies."
                elif issue_type.lower() == 'immigration':
                    system_prompt = "You are an immigration law expert with knowledge of asylum claims, deportation defense, and administrative proceedings."
                elif issue_type.lower() == 'housing':
                    system_prompt = "You are a housing rights attorney specializing in tenant protections, eviction defense, and fair housing laws."
                else:
                    system_prompt = f"You are an expert legal strategist specializing in {issue_type} law with particular knowledge of {court_type} procedures."
                
                # Create detailed prompt with guidance for comprehensive strategy
                user_prompt = f"""For the following case, provide a comprehensive winning legal strategy:

Case Description: {description}
Issue Type: {issue_type}
Court Type: {court_type}

Structure your response as a JSON object with the following components:
1. "winning_strategy" - a dictionary containing:
   - "primary_approach": A concise statement of your main strategic approach
   - "attack_defense_tactics": An array of specific tactical approaches to attack opposing evidence or claims
   - "procedural_motions": An array of specific motions to file that could gain procedural advantages
   - "evidence_challenges": Approach to challenging opposition evidence or presenting your own
   - "hearing_objections": Strategy for objections during hearings
   - "timing_strategy": Strategic use of timing for maximum advantage

Focus on innovative legal arguments, constitutional issues, technical procedure violations, 
and aggressive defense/offense tactics specifically tailored to this type of case.
"""
                
                logging.info("Generating comprehensive legal strategy via OpenAI")
                
                response = client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                
                try:
                    if content:
                        strategy = json.loads(content)
                        return strategy
                except json.JSONDecodeError:
                    logging.error("Failed to parse OpenAI strategy JSON response")
            
            except Exception as openai_error:
                logging.error(f"OpenAI strategy generation error: {str(openai_error)}")
        
        # Try Anthropic as fallback
        if anthropic_helper.is_available():
            try:
                logging.info("Falling back to Anthropic for strategy generation")
                
                # Create strategy prompt specific to case type
                strategy_prompt = f"""For the following case, provide a comprehensive winning legal strategy:

Case Description: {description}
Issue Type: {issue_type}
Court Type: {court_type}

Structure your response as a JSON object with the following components:
1. "winning_strategy" - a dictionary containing:
   - "primary_approach": A concise statement of your main strategic approach
   - "attack_defense_tactics": An array of specific tactical approaches to attack opposing evidence or claims
   - "procedural_motions": An array of specific motions to file that could gain procedural advantages
   - "evidence_challenges": Approach to challenging opposition evidence or presenting your own
   - "hearing_objections": Strategy for objections during hearings
   - "timing_strategy": Strategic use of timing for maximum advantage

Focus on innovative legal arguments, constitutional issues, technical procedure violations, 
and aggressive defense/offense tactics specifically tailored to this type of case.

Return ONLY valid JSON.
"""
                
                # Call Anthropic's Claude for strategy
                strategy_result = anthropic_helper.analyze_case_text(strategy_prompt, json_format=True)
                
                if isinstance(strategy_result, dict) and "winning_strategy" in strategy_result:
                    return strategy_result
                
            except Exception as claude_error:
                logging.error(f"Anthropic strategy generation error: {str(claude_error)}")
        
        # Use legal knowledge base for fallback
        logging.info("Using legal knowledge base for fallback strategy generation")
        
        # Get relevant rights issues based on case type
        rights_issues = []
        if issue_type.lower() == 'criminal':
            rights_issues = ["fourth_amendment", "fifth_amendment", "sixth_amendment"]
        elif issue_type.lower() == 'civil':
            rights_issues = ["due_process", "equal_protection"]
        elif issue_type.lower() == 'immigration':
            rights_issues = ["due_process", "immigration_specific"]
        elif issue_type.lower() == 'housing':
            rights_issues = ["fair_housing", "tenant_rights"]
        elif issue_type.lower() in ['contract', 'business']:
            rights_issues = ["contract_remedies", "commercial_rights"]
        
        # Use legal knowledge base to generate strategy
        comprehensive_strategy = lkb.format_comprehensive_strategy(issue_type.lower(), rights_issues)
        
        # Transform to expected format if needed
        if "winning_strategy" not in comprehensive_strategy:
            winning_strategy = {
                "primary_approach": comprehensive_strategy.get("primary_strategy", "Develop a multi-faceted approach targeting procedural and substantive weaknesses in the opposition's case"),
                "attack_defense_tactics": comprehensive_strategy.get("key_tactics", [
                    "Challenge jurisdiction and venue if applicable",
                    "Scrutinize all procedural steps for technical violations",
                    "Request all discoverable documents with detailed specificity",
                    "Identify inconsistencies in opposition's documentation",
                    "Prepare detailed timeline to identify procedural irregularities"
                ]),
                "procedural_motions": comprehensive_strategy.get("recommended_motions", [
                    "Motion to Dismiss for failure to state a claim",
                    "Motion for Discovery",
                    "Motion to Suppress evidence (if applicable)",
                    "Motion for Summary Judgment",
                    "Motion for Continuance (if strategically advantageous)"
                ]),
                "evidence_challenges": comprehensive_strategy.get("evidence_strategy", "Scrutinize chain of custody for all evidence and identify potential authentication issues"),
                "hearing_objections": comprehensive_strategy.get("hearing_strategy", "Prepare specific objections based on hearsay, relevance, and authentication issues"),
                "timing_strategy": comprehensive_strategy.get("timing_approach", "Strategic use of continuances when advantageous while asserting speedy trial rights when beneficial")
            }
            return {"winning_strategy": winning_strategy}
        
        return comprehensive_strategy
        
    except Exception as e:
        logging.error(f"Error in generate_legal_strategy: {str(e)}")
        # Provide reliable fallback
        return {
            "winning_strategy": {
                "primary_approach": "Multi-faceted approach focusing on procedural and substantive weaknesses",
                "attack_defense_tactics": [
                    "Challenge jurisdiction and venue if applicable",
                    "Scrutinize all procedural steps for technical violations",
                    "Request all discoverable documents with detailed specificity",
                    "Identify inconsistencies in opposition's documentation",
                    "Prepare detailed timeline to identify procedural irregularities"
                ],
                "procedural_motions": [
                    "Motion to Dismiss for failure to state a claim",
                    "Motion for Discovery",
                    "Motion to Suppress evidence (if applicable)",
                    "Motion for Summary Judgment",
                    "Motion for Continuance (if strategically advantageous)"
                ],
                "evidence_challenges": "Scrutinize chain of custody for all evidence and identify potential authentication issues",
                "hearing_objections": "Prepare specific objections based on hearsay, relevance, and authentication issues",
                "timing_strategy": "Strategic use of continuances when advantageous while asserting speedy trial rights when beneficial"
            }
        }

def calculate_success_probability(case_id, description, issue_type, court_type, evidence_descriptions=None):
    """
    Calculate probability of success for a case.
    Returns a dictionary with success probability and rationale.
    """
    try:
        # Import here to avoid circular imports
        import legal_knowledge_base as lkb
        
        # Try OpenAI first
        if os.environ.get('OPENAI_API_KEY'):
            try:
                import openai
                from openai import OpenAI

                client = OpenAI(
                    api_key=os.environ.get('OPENAI_API_KEY')
                )
                
                # Create detailed prompt for probability assessment
                user_prompt = f"""For the following case, calculate the probability of success:

Case Description: {description}
Issue Type: {issue_type}
Court Type: {court_type}

Analyze this case and provide a detailed probability assessment. 
Structure your response as a JSON object with the following:

1. "success_probability": A float value between 0.0 and 1.0 representing the likelihood of success
2. "confidence_level": How confident you are in this assessment (Low, Medium, High)
3. "key_factors": Array of specific factors affecting this probability
4. "improvement_suggestions": Array of actions that could improve the probability

Base your assessment on legal precedents, strength of evidence descriptions, procedural factors,
and typical outcomes for similar cases in this jurisdiction.
"""
                
                logging.info("Calculating success probability via OpenAI")
                
                response = client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[
                        {"role": "system", "content": "You are an expert legal analyst specializing in case outcome prediction based on precedent and legal factors."},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.4
                )
                
                content = response.choices[0].message.content
                
                try:
                    # Handle when content is None or empty
                    if content is None or not content.strip():
                        logging.error("Empty content returned from OpenAI")
                        return None
                        
                    probability_result = json.loads(content)
                    return probability_result
                except json.JSONDecodeError:
                    logging.error("Failed to parse OpenAI probability JSON response")
                    # Try to extract JSON from the response if it contains markdown or explanatory text
                    import re
                    # Make sure content is a string for regex
                    if content and isinstance(content, str):
                        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                        if json_match:
                            try:
                                probability_result = json.loads(json_match.group(1))
                                return probability_result
                            except:
                                pass
                    
                    # Return structured result if parsing fails
                    return {
                        "success_probability": 50,
                        "confidence": "Medium",
                        "probability_factors": [
                            "Based on case description and evidence",
                            "Limited by inability to parse exact AI analysis",
                            "General assessment of similar cases"
                        ]
                    }
            
            except Exception as openai_error:
                logging.error(f"OpenAI probability calculation error: {str(openai_error)}")
        
        # Try Anthropic as fallback
        if anthropic_helper.is_available():
            try:
                logging.info("Falling back to Anthropic for probability calculation")
                
                # Create probability assessment prompt
                probability_prompt = f"""For the following case, calculate the probability of success:

Case Description: {description}
Issue Type: {issue_type}
Court Type: {court_type}

Analyze this case and provide a detailed probability assessment. 
Structure your response as a JSON object with the following:

1. "success_probability": A float value between 0.0 and 1.0 representing the likelihood of success
2. "confidence_level": How confident you are in this assessment (Low, Medium, High)
3. "key_factors": Array of specific factors affecting this probability
4. "improvement_suggestions": Array of actions that could improve the probability

Base your assessment on legal precedents, strength of evidence descriptions, procedural factors,
and typical outcomes for similar cases in this jurisdiction.

Return ONLY valid JSON.
"""
                
                # Call Anthropic's Claude for probability assessment
                probability_result = anthropic_helper.analyze_case_text(probability_prompt, json_format=True)
                
                if isinstance(probability_result, dict) and "success_probability" in probability_result:
                    return probability_result
                
            except Exception as claude_error:
                logging.error(f"Anthropic probability calculation error: {str(claude_error)}")
        
        # Fall back to case-type based assessment
        logging.info("Using fallback probability calculation based on case type")
        
        # Default factors based on issue type
        key_factors = []
        improvement_suggestions = []
        base_probability = 0.5
        confidence = "Medium"
        
        if issue_type.lower() == 'criminal':
            key_factors = [
                "Statistical analysis of similar criminal cases in this jurisdiction",
                "Procedural adherence by law enforcement",
                "Quality and admissibility of evidence",
                "Potential constitutional rights violations"
            ]
            improvement_suggestions = [
                "Document any procedural violations by law enforcement",
                "File motions challenging evidence admissibility",
                "Develop timeline to support speedy trial claims",
                "Consider expert witness for technical evidence challenges"
            ]
            
        elif issue_type.lower() == 'civil':
            key_factors = [
                "Burden of proof requirements for civil claims",
                "Documentary evidence strength",
                "Witness credibility assessment",
                "Relevant precedent in similar civil matters"
            ]
            improvement_suggestions = [
                "Strengthen documentation of damages",
                "Gather additional witness testimony",
                "Research similar cases with favorable outcomes",
                "Consider settlement negotiations as fallback"
            ]
            
        elif issue_type.lower() == 'family':
            key_factors = [
                "Court's tendency to favor specific outcomes in family cases",
                "Documentation of relevant family history",
                "Expert testimony availability",
                "Family court precedent in the jurisdiction"
            ]
            improvement_suggestions = [
                "Strengthen documentation of family circumstances",
                "Consider child welfare expert testimony",
                "Document history of care and responsibility",
                "Prepare clear parenting or support plan"
            ]
            
        elif issue_type.lower() in ['contract', 'business']:
            key_factors = [
                "Contract language clarity and interpretation",
                "Evidence of performance or breach",
                "Documentation of damages",
                "Relevant business relationship history"
            ]
            improvement_suggestions = [
                "Strengthen documentation of contract performance",
                "Calculate damages with greater precision",
                "Gather communication records showing intent",
                "Consider alternative dispute resolution"
            ]
            
        else:
            key_factors = [
                "Case complexity and specific legal issues",
                "Documentation quality and completeness",
                "Jurisdiction tendencies for similar cases",
                "Potential procedural or substantive challenges"
            ]
            improvement_suggestions = [
                "Provide more detailed case information",
                "Upload relevant evidence documentation",
                "Research similar cases in your jurisdiction",
                "Consider consultation with specialized counsel"
            ]
        
        return {
            "success_probability": base_probability,
            "confidence_level": confidence,
            "key_factors": key_factors,
            "improvement_suggestions": improvement_suggestions
        }
        
    except Exception as e:
        logging.error(f"Error in calculate_success_probability: {str(e)}")
        return {
            "success_probability": 0.5,
            "confidence_level": "Low",
            "key_factors": [
                "Case requires detailed analysis",
                "Success probability would be calculated based on multiple factors",
                "Specific case details would refine this assessment"
            ],
            "improvement_suggestions": [
                "Provide more detailed case information",
                "Upload relevant evidence documentation",
                "Include specific procedural history details",
                "Note any potential rights violations"
            ]
        }
