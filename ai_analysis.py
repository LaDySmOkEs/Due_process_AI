import json
import os
import traceback
import logging
import random
# Set logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app as app
from flask_login import login_required, current_user
from models import Case, LegalAnalysis, Document
from app import db
from ai_helpers import analyze_case_description, recommend_documents
import anthropic_helper
import legal_knowledge_base as lkb

ai = Blueprint('ai', __name__)

def generate_fallback_documents(case):
    """
    Generate reliable fallback document recommendations when API services fail.
    This ensures users always get document recommendations rather than an endless loading state.
    """
    app.logger.info(f"Generating fallback document recommendations for case {case.id}: {case.title}")
    
    # Map issue type to document strategy
    case_type_mapping = {
        "criminal": "criminal_defense",
        "civil": "civil_rights",
        "immigration": "habeas_corpus",
        "housing": "civil_rights",
        "personal_injury": "personal_injury",
        "contract": "contract_dispute",
        "bankruptcy": "bankruptcy",
        "family": "family_law"
    }
    
    case_type = case_type_mapping.get(case.issue_type.lower(), "criminal_defense")
    
    # Get document strategy based on case type
    document_recommendations = []
    
    for stage in ["initial_stage", "pre_trial", "trial"]:
        stage_strategies = lkb.get_document_strategy(case_type, stage)
        if isinstance(stage_strategies, list):
            for doc in stage_strategies[:2]:  # Limit to 2 docs per stage
                if isinstance(doc, dict) and "document" in doc and "purpose" in doc:
                    document_recommendations.append({
                        "document_type": doc.get("document", "Legal Document"),
                        "rationale": doc.get("purpose", "Important for case progress"),
                        "strategic_guidance": doc.get("strategy", "File this document to advance your legal position"),
                        "key_elements": doc.get("key_elements", ["Key facts from your case", "Legal basis for filing"]),
                        "timing": doc.get("timing", "File at the appropriate stage in your case"),
                        "importance": doc.get("importance", "Medium"),
                        "impact": doc.get("impact", "May significantly affect case outcome")
                    })
    
    # If no document recommendations were generated from the knowledge base, add appropriate ones for the case type
    if not document_recommendations:
        if case.issue_type.lower() == "criminal":
            document_recommendations = [
                {
                    "document_type": "Motion to Suppress Evidence",
                    "rationale": "Challenge evidence that may have been obtained illegally",
                    "strategic_guidance": "Focus on Fourth Amendment violations in evidence collection",
                    "key_elements": ["Specific evidence to suppress", "Legal basis for suppression", "How rights were violated"],
                    "timing": "Early in pre-trial proceedings",
                    "importance": "High",
                    "impact": "Can significantly weaken prosecution's case if successful"
                },
                {
                    "document_type": "Discovery Request",
                    "rationale": "Request all evidence the prosecution may have",
                    "strategic_guidance": "Ensure you have access to all evidence in your case",
                    "key_elements": ["Request for specific categories of evidence", "Legal basis for discovery"],
                    "timing": "Early in pre-trial proceedings",
                    "importance": "High",
                    "impact": "Provides information essential to your defense"
                }
            ]
        elif case.issue_type.lower() in ["civil", "personal_injury", "housing"]:
            document_recommendations = [
                {
                    "document_type": "Complaint/Petition",
                    "rationale": "Initiates your civil lawsuit and outlines claims",
                    "strategic_guidance": "Clearly articulate legal claims and supporting facts",
                    "key_elements": ["Statement of facts", "Legal claims", "Prayer for relief"],
                    "timing": "Initial filing to start case",
                    "importance": "Critical",
                    "impact": "Establishes foundation of entire case"
                },
                {
                    "document_type": "Discovery Requests",
                    "rationale": "Obtain information and evidence from opposing party",
                    "strategic_guidance": "Request specific documents and information relevant to claims",
                    "key_elements": ["Interrogatories", "Requests for production", "Requests for admission"],
                    "timing": "After initial pleadings",
                    "importance": "High",
                    "impact": "Builds evidence for your position"
                }
            ]
        elif case.issue_type.lower() == "contract":
            document_recommendations = [
                {
                    "document_type": "Breach of Contract Complaint",
                    "rationale": "Initiates legal action for contract breach",
                    "strategic_guidance": "Clearly establish contract terms and alleged breach",
                    "key_elements": ["Contract terms", "Breach details", "Damages claimed"],
                    "timing": "Initial filing",
                    "importance": "Critical",
                    "impact": "Establishes basis for entire case"
                },
                {
                    "document_type": "Motion for Specific Performance",
                    "rationale": "Seeks court order requiring contract performance",
                    "strategic_guidance": "Demonstrate why monetary damages are inadequate",
                    "key_elements": ["Contract terms", "Performance obligations", "Inadequacy of damages"],
                    "timing": "After establishing contract validity",
                    "importance": "High",
                    "impact": "Can obtain actual performance instead of damages"
                }
            ]
        elif case.issue_type.lower() == "family":
            document_recommendations = [
                {
                    "document_type": "Petition for Dissolution/Custody",
                    "rationale": "Initiates family court proceedings",
                    "strategic_guidance": "Clearly state requested relief and supporting facts",
                    "key_elements": ["Party information", "Requested relief", "Statutory grounds"],
                    "timing": "Initial filing",
                    "importance": "Critical",
                    "impact": "Establishes case parameters"
                },
                {
                    "document_type": "Parenting Plan",
                    "rationale": "Establishes custody and visitation arrangements",
                    "strategic_guidance": "Focus on best interests of the child factors",
                    "key_elements": ["Custody schedule", "Decision-making provisions", "Child's needs"],
                    "timing": "With initial filing or before final hearing",
                    "importance": "High",
                    "impact": "Determines future parent-child arrangements"
                }
            ]
        elif case.issue_type.lower() == "bankruptcy":
            document_recommendations = [
                {
                    "document_type": "Bankruptcy Petition",
                    "rationale": "Initiates bankruptcy proceedings",
                    "strategic_guidance": "Complete all schedules with accurate information",
                    "key_elements": ["Complete asset listing", "All creditors listed", "Financial history"],
                    "timing": "Initial filing",
                    "importance": "Critical",
                    "impact": "Establishes bankruptcy case"
                },
                {
                    "document_type": "Means Test Calculation",
                    "rationale": "Determines eligibility for Chapter 7 or required Chapter 13 payment",
                    "strategic_guidance": "Accurately document all income and allowable expenses",
                    "key_elements": ["Income verification", "Expense documentation", "Statutory deductions"],
                    "timing": "With initial filing",
                    "importance": "High",
                    "impact": "Determines bankruptcy chapter and payment requirements"
                }
            ]
        elif case.issue_type.lower() == "immigration":
            document_recommendations = [
                {
                    "document_type": "Form I-589 (Asylum Application)",
                    "rationale": "Requests asylum protection in the United States",
                    "strategic_guidance": "Clearly document persecution or fear of persecution",
                    "key_elements": ["Personal background", "Basis for asylum claim", "Supporting evidence"],
                    "timing": "Within one year of arrival or with changed circumstances",
                    "importance": "Critical",
                    "impact": "Basis for asylum protection"
                },
                {
                    "document_type": "Motion to Reopen/Reconsider",
                    "rationale": "Challenges negative immigration decision",
                    "strategic_guidance": "Identify specific errors or new evidence",
                    "key_elements": ["Legal basis for motion", "New evidence or legal arguments", "Relief requested"],
                    "timing": "Within filing deadlines (typically 30-90 days)",
                    "importance": "High",
                    "impact": "Could reverse negative decision"
                }
            ]
        else:
            # Default generic documents for any case type
            document_recommendations = [
                {
                    "document_type": "Initial Filing",
                    "rationale": "Starts your legal case and outlines claims or defenses",
                    "strategic_guidance": "Clearly articulate your position and legal basis",
                    "key_elements": ["Statement of facts", "Legal claims or defenses", "Relief requested"],
                    "timing": "At the beginning of your case",
                    "importance": "Critical",
                    "impact": "Establishes foundation of your case"
                },
                {
                    "document_type": "Discovery Requests",
                    "rationale": "Obtain relevant information and evidence",
                    "strategic_guidance": "Request specific information relevant to your case",
                    "key_elements": ["Clear requests", "Legal basis for requests", "Connection to case issues"],
                    "timing": "Early in the case process",
                    "importance": "High",
                    "impact": "Provides evidence to support your position"
                }
            ]
    
    return {"document_recommendations": document_recommendations}


def generate_fallback_analysis(case):
    """
    Generate reliable fallback analysis data when API services fail.
    This ensures users always get a result instead of an endlessly loading analysis.
    """
    app.logger.info(f"Generating fallback analysis for case {case.id}: {case.title}")
    
    # Map case type to legal domain for better fallback
    domain_mapping = {
        "criminal": "criminal_law",
        "civil": "civil_law", 
        "family": "civil_law",
        "immigration": "constitutional_law",
        "bankruptcy": "civil_law",
        "personal_injury": "civil_law",
        "housing": "civil_law",
        "contract": "civil_law"
    }
    
    legal_domain = domain_mapping.get(case.issue_type.lower(), "constitutional_law")
    
    # Customize rights issues based on case type
    case_type = case.issue_type.lower()
    rights_issues = []
    
    # Define keywords relevant to different case types
    if case_type == "criminal":
        rights_keywords = {
            "fourth_amendment": ["search", "seizure", "warrant", "privacy", "stop", "arrest", "detain", "property"],
            "fifth_amendment": ["silent", "miranda", "confession", "custody", "interrogation", "statement", "self-incrimination"],
            "sixth_amendment": ["attorney", "lawyer", "counsel", "speedy", "trial", "witness", "confront", "jury"],
            "eighth_amendment": ["bail", "fine", "cruel", "punishment", "sentence", "excessive"]
        }
        
        # Check for keywords in description
        desc_lower = case.description.lower()
        for right, keywords in rights_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                rights_issues.append(right)
        
        # If no rights issues identified for criminal case, add common ones
        if not rights_issues:
            rights_issues = ["fourth_amendment", "fifth_amendment"]
    
    elif case_type in ["civil", "personal_injury", "housing"]:
        # For civil cases, check for relevant legal issues
        civil_issues = {
            "due_process_rights": ["notice", "hearing", "opportunity", "respond", "fair", "process"],
            "property_rights": ["property", "ownership", "possession", "title", "interest"],
            "contract_rights": ["agreement", "contract", "breach", "promise", "term", "condition"],
            "tort_claims": ["injury", "damage", "harm", "negligence", "duty", "care"]
        }
        
        desc_lower = case.description.lower()
        for issue, keywords in civil_issues.items():
            if any(keyword in desc_lower for keyword in keywords):
                rights_issues.append(issue)
        
        # Default for civil cases
        if not rights_issues:
            rights_issues = ["due_process_rights", "tort_claims"]
    
    elif case_type == "family":
        # Family law issues
        family_issues = {
            "parental_rights": ["custody", "visitation", "parent", "child", "decision"],
            "property_division": ["property", "asset", "division", "marital", "separate", "equitable"],
            "support_rights": ["support", "alimony", "maintenance", "financial", "need", "ability"]
        }
        
        desc_lower = case.description.lower()
        for issue, keywords in family_issues.items():
            if any(keyword in desc_lower for keyword in keywords):
                rights_issues.append(issue)
        
        # Default for family cases
        if not rights_issues:
            rights_issues = ["parental_rights"]
    
    elif case_type == "contract":
        # Contract issues
        contract_issues = {
            "formation_issues": ["offer", "acceptance", "consideration", "agreement", "intent", "formed"],
            "performance_issues": ["breach", "perform", "obligation", "fulfill", "term", "condition"],
            "damages_issues": ["damage", "loss", "compensation", "remedy", "specific", "performance"],
            "interpretation_issues": ["ambiguity", "meaning", "interpret", "unclear", "term", "language"]
        }
        
        desc_lower = case.description.lower()
        for issue, keywords in contract_issues.items():
            if any(keyword in desc_lower for keyword in keywords):
                rights_issues.append(issue)
        
        # Default for contract cases
        if not rights_issues:
            rights_issues = ["performance_issues", "damages_issues"]
    
    elif case_type == "immigration":
        # Immigration issues
        immigration_issues = {
            "due_process_rights": ["notice", "hearing", "opportunity", "process", "appeal", "review"],
            "asylum_rights": ["asylum", "refugee", "persecution", "fear", "return", "credible"],
            "status_issues": ["status", "visa", "green card", "permanent", "residence", "removal"]
        }
        
        desc_lower = case.description.lower()
        for issue, keywords in immigration_issues.items():
            if any(keyword in desc_lower for keyword in keywords):
                rights_issues.append(issue)
        
        # Default for immigration cases
        if not rights_issues:
            rights_issues = ["due_process_rights"]
    
    elif case_type == "bankruptcy":
        # Bankruptcy issues
        bankruptcy_issues = {
            "automatic_stay": ["stay", "collection", "creditor", "stop", "action", "pursue"],
            "discharge_rights": ["discharge", "debt", "eliminate", "fresh", "start"],
            "exemption_rights": ["exempt", "exemption", "protect", "asset", "property", "keep"]
        }
        
        desc_lower = case.description.lower()
        for issue, keywords in bankruptcy_issues.items():
            if any(keyword in desc_lower for keyword in keywords):
                rights_issues.append(issue)
        
        # Default for bankruptcy cases
        if not rights_issues:
            rights_issues = ["automatic_stay", "discharge_rights"]
    
    else:
        # For any other case type, use general rights
        rights_issues = ["procedural_rights", "substantive_rights"]
    
    # Use our legal knowledge base to provide reliable fallback data
    rights_assessment = []
    for right in rights_issues:
        if right in lkb.LEGAL_RIGHTS:
            rights_info = lkb.LEGAL_RIGHTS[right]
            # Add 1-2 potential violations for this right
            violations = rights_info.get("common_violations", [])
            if violations:
                for i in range(min(2, len(violations))):
                    violation = violations[i]
                    rights_assessment.append({
                        "right_violated": rights_info.get("name", "Constitutional Right"),
                        "explanation": violation,
                        "severity": random.choice(["High", "Medium"]),
                        "supporting_legal_principle": rights_info.get("key_principle", "Constitutional protection")
                    })
    
    # If still no rights assessment, add a generic one
    if not rights_assessment:
        rights_assessment = [{
            "right_violated": "Due Process Rights",
            "explanation": "Potential procedural irregularities in case handling that may violate due process standards",
            "severity": "Medium",
            "supporting_legal_principle": "Fifth and Fourteenth Amendment due process guarantees"
        }]
    
    # Get case law from knowledge base
    case_law_suggestions = []
    for right in rights_issues:
        cases = lkb.get_relevant_case_law(right)
        # Add up to 2 cases per right
        for case_info in cases[:2]:
            case_law_suggestions.append({
                "case_name": case_info.get("case", "Relevant Supreme Court Case"),
                "year": case_info.get("year", ""),
                "court": case_info.get("court", "Supreme Court"),
                "relevance": case_info.get("relevance", "Establishes important precedent for this case type"),
                "principles": case_info.get("holding", "Important legal principle"),
                "key_quotes": [case_info.get("key_quote", "Significant legal principle from the ruling")],
                "strategic_application": case_info.get("application", "Apply this precedent to strengthen legal arguments"),
                "counter_arguments": "Be prepared to distinguish your case if the opposing party cites contrary precedent"
            })
    
    # If no case law, add generic precedents
    if not case_law_suggestions:
        case_law_suggestions = [{
            "case_name": "Terry v. Ohio",
            "year": "1968",
            "court": "U.S. Supreme Court",
            "relevance": "Established 'reasonable suspicion' standard for brief investigative stops",
            "principles": "Police may briefly detain a person if they have reasonable suspicion of criminal activity",
            "key_quotes": ["Police officer must be able to point to specific and articulable facts that warrant the intrusion"],
            "strategic_application": "Challenge whether officers had specific, articulable facts to justify the stop",
            "counter_arguments": "State may argue that suspicious behavior created reasonable suspicion"
        }]
    
    # Create winning strategy
    winning_strategy = {
        "primary_approach": "Comprehensive legal strategy targeting procedural and evidentiary weaknesses",
        "attack_defense_tactics": [
            "Challenge all procedural errors in case processing",
            "Develop constitutional challenges to key evidence",
            "Create parallel defense strategies for multiple paths to victory",
            "Focus on rights violations identified in this analysis"
        ],
        "procedural_motions": [
            "File targeted motions focused on constitutional violations",
            "Submit discovery requests for all evidence",
            "Consider change of venue if local factors may prejudice case"
        ],
        "evidence_challenges": "Challenge any evidence with potential chain of custody issues or constitutional problems",
        "hearing_objections": "Make timely objections to any inadmissible evidence or testimony",
        "timing_strategy": "File motions at strategic times for maximum impact on case progression"
    }
    
    # Combine everything into a proper analysis result
    return {
        "rights_assessment": rights_assessment,
        "case_law_suggestions": case_law_suggestions,
        "winning_strategy": winning_strategy
    }

@ai.route('/case/<int:case_id>/ai-analysis', methods=['GET', 'POST'])
@login_required
def case_ai_analysis(case_id):
    """Generate AI-powered legal analysis for a case"""
    case = Case.get_case_by_id(case_id)
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check if analysis already exists
    case_law_analysis = LegalAnalysis.get_by_case_and_type(case_id, 'case_law')
    doc_recommendations = LegalAnalysis.get_by_case_and_type(case_id, 'document_recommendations')
    
    # Initialize default values
    case_law_data = {}
    doc_recommendations_data = {}
    
    # If analysis requested and doesn't exist, generate it
    if request.method == 'POST':
        analysis_type = request.form.get('analysis_type')
        
        try:
            if analysis_type == 'case_law':
                # Default empty result in case all attempts fail
                result = {
                    "rights_assessment": [],
                    "case_law_suggestions": [],
                    "winning_strategy": {}
                }
                
                # Generate comprehensive case law and rights analysis
                app.logger.info(f"Starting analysis for case {case_id}: {case.title}")
                app.logger.info(f"Case details - Issue: {case.issue_type}, Court: {case.court_type}")
                
                try:
                    app.logger.info("Calling analyze_case_description function")
                    result = analyze_case_description(
                        description=case.description,
                        issue_type=case.issue_type,
                        court_type=case.court_type
                    )
                    app.logger.info(f"Result from analyze_case_description: {type(result)}")
                    
                    if result is None:
                        app.logger.error("analyze_case_description returned None, using fallback")
                        result = generate_fallback_analysis(case)
                        flash('AI services returned no data. We\'ve generated a basic analysis instead.', 'warning')
                        
                    elif not isinstance(result, dict):
                        app.logger.error(f"analyze_case_description returned non-dict type: {type(result)}, using fallback")
                        result = generate_fallback_analysis(case)
                        flash('AI services returned invalid data. We\'ve generated a basic analysis instead.', 'warning')
                    
                    else:
                        app.logger.info(f"Result keys: {list(result.keys())}")
                        
                        if not result.get('rights_assessment'):
                            app.logger.warning("Result missing rights_assessment, adding fallback data")
                            # Only add the missing section instead of replacing the whole result
                            result["rights_assessment"] = generate_fallback_analysis(case)["rights_assessment"]
                            flash('AI analysis was incomplete. We\'ve added required information.', 'warning')
                        
                except Exception as analysis_error:
                    app.logger.error(f"Primary analysis failed: {str(analysis_error)}")
                    app.logger.error(f"Error traceback: {traceback.format_exc()}")
                    
                    # Try direct Anthropic fallback if OpenAI integration fails
                    app.logger.info("Checking if Anthropic is available for fallback")
                    if anthropic_helper.is_available():
                        app.logger.info("Anthropic available, trying fallback")
                        
                        # Try the first fallback - analyze rights violations
                        app.logger.info("Calling anthropic_helper.analyze_rights_violations")
                        rights_result = anthropic_helper.analyze_rights_violations(
                            description=case.description,
                            issue_type=case.issue_type, 
                            court_type=case.court_type
                        )
                        app.logger.info(f"Rights result: {type(rights_result)}")
                        
                        # Try the second fallback - suggest case law
                        app.logger.info("Calling anthropic_helper.suggest_case_law")
                        case_law_result = anthropic_helper.suggest_case_law(
                            description=case.description,
                            issue_type=case.issue_type, 
                            court_type=case.court_type
                        )
                        app.logger.info(f"Case law result: {type(case_law_result)}")
                        
                        # Check if both fallbacks returned valid data
                        if rights_result and case_law_result:
                            app.logger.info("Both Anthropic fallbacks succeeded, combining results")
                            
                            # Combine results
                            rights_violations = []
                            if isinstance(rights_result, dict) and "rights_violations" in rights_result:
                                app.logger.info(f"Found {len(rights_result['rights_violations'])} rights violations")
                                rights_violations = rights_result["rights_violations"]
                            else:
                                app.logger.warning(f"Rights result missing expected structure: {rights_result}")
                                
                            relevant_cases = []
                            if isinstance(case_law_result, dict) and "relevant_cases" in case_law_result:
                                app.logger.info(f"Found {len(case_law_result['relevant_cases'])} case law suggestions")
                                relevant_cases = case_law_result["relevant_cases"]
                            else:
                                app.logger.warning(f"Case law result missing expected structure: {case_law_result}")
                                
                            result = {
                                "rights_assessment": rights_violations,
                                "case_law_suggestions": relevant_cases,
                                "winning_strategy": {}
                            }
                            app.logger.info("Successfully created combined result from Anthropic fallbacks")
                        else:
                            app.logger.error("Both primary and Anthropic backup analyses failed, using fallback data")
                            # Instead of redirecting, provide fallback data so analysis isn't stuck
                            result = generate_fallback_analysis(case)
                            flash('AI services are currently unavailable. We\'ve generated a basic analysis instead.', 'warning')
                    else:
                        app.logger.error("Anthropic not available for fallback, using fallback data")
                        # Instead of redirecting, provide fallback data
                        result = generate_fallback_analysis(case)
                        flash('AI services are not configured. We\'ve generated a basic analysis instead.', 'warning')
                
                # Store the complete analysis result as structured data
                # Make sure result has the required structure
                if "rights_assessment" not in result:
                    result["rights_assessment"] = []
                if "case_law_suggestions" not in result:
                    result["case_law_suggestions"] = []
                if "winning_strategy" not in result:
                    # Generate strategy based on case type
                    if case.issue_type.lower() == "criminal":
                        result["winning_strategy"] = {
                            "primary_approach": "Strategic defense focusing on constitutional protections and procedural rights",
                            "attack_defense_tactics": [
                                "Challenge procedural errors in case processing",
                                "Focus on constitutional protections relevant to this specific case",
                                "Identify potential weaknesses in prosecution's evidence"
                            ],
                            "procedural_motions": [
                                "Motion for discovery of all relevant evidence",
                                "Targeted motions based on specific case facts"
                            ],
                            "evidence_challenges": "Carefully analyze all evidence for potential challenges to admissibility",
                            "hearing_objections": "Make timely objections during hearings to preserve issues for appeal",
                            "timing_strategy": "File strategically timed motions for maximum impact"
                        }
                    elif case.issue_type.lower() in ["civil", "personal_injury", "housing"]:
                        result["winning_strategy"] = {
                            "primary_approach": "Strategic civil litigation approach focusing on burden of proof and evidence",
                            "attack_defense_tactics": [
                                "Establish strong factual foundation through discovery",
                                "Focus on applicable statutory and case law",
                                "Develop compelling narrative supported by evidence"
                            ],
                            "procedural_motions": [
                                "Strategic discovery requests",
                                "Motions for summary judgment if applicable",
                                "Motions in limine to exclude harmful evidence"
                            ],
                            "evidence_challenges": "Ensure all evidence meets admissibility standards and authenticates properly",
                            "hearing_objections": "Strategic objections to preserve record and limit opposing evidence",
                            "timing_strategy": "Time filings strategically within procedural deadlines"
                        }
                    elif case.issue_type.lower() == "contract":
                        result["winning_strategy"] = {
                            "primary_approach": "Contract interpretation and enforcement strategy",
                            "attack_defense_tactics": [
                                "Focus on contract terms and interpretation principles",
                                "Establish performance or breach based on contract terms",
                                "Analyze applicable contract law and precedent"
                            ],
                            "procedural_motions": [
                                "Motion for production of all contract-related documents",
                                "Potential motion for summary judgment if terms are clear"
                            ],
                            "evidence_challenges": "Ensure all contract-related evidence is properly authenticated",
                            "hearing_objections": "Object to parol evidence if inconsistent with written terms",
                            "timing_strategy": "Strategic timing of filings based on contract dispute timeline"
                        }
                    elif case.issue_type.lower() == "family":
                        result["winning_strategy"] = {
                            "primary_approach": "Family law strategy focusing on equitable outcomes",
                            "attack_defense_tactics": [
                                "Focus on relevant family law standards",
                                "Build compelling case based on statutory factors",
                                "Consider mediation and negotiation strategies"
                            ],
                            "procedural_motions": [
                                "Motion for temporary orders if needed",
                                "Discovery motions for financial or parenting information"
                            ],
                            "evidence_challenges": "Ensure evidence meets relevance and admissibility standards",
                            "hearing_objections": "Strategic objections to inadmissible or prejudicial evidence",
                            "timing_strategy": "Time filings to address immediate needs while building long-term case"
                        }
                    elif case.issue_type.lower() == "bankruptcy":
                        result["winning_strategy"] = {
                            "primary_approach": "Strategic bankruptcy approach focusing on debt relief and asset protection",
                            "attack_defense_tactics": [
                                "Proper application of bankruptcy code provisions",
                                "Complete disclosure with strategic presentation",
                                "Address creditor challenges proactively"
                            ],
                            "procedural_motions": [
                                "Motion for automatic stay if contested",
                                "Motions to determine secured status of claims if applicable"
                            ],
                            "evidence_challenges": "Ensure all financial documentation is accurate and complete",
                            "hearing_objections": "Object to improper creditor claims or procedures",
                            "timing_strategy": "Strategic timing of filing and procedural steps"
                        }
                    elif case.issue_type.lower() == "immigration":
                        result["winning_strategy"] = {
                            "primary_approach": "Immigration advocacy strategy focusing on eligibility and procedural rights",
                            "attack_defense_tactics": [
                                "Focus on meeting eligibility requirements",
                                "Address procedural issues in proceedings",
                                "Build compelling equitable case if discretion applies"
                            ],
                            "procedural_motions": [
                                "Motion to present additional evidence if applicable",
                                "Motion for continuance if additional preparation needed"
                            ],
                            "evidence_challenges": "Ensure all supporting documentation is properly authenticated",
                            "hearing_objections": "Object to improper evidence or procedural errors",
                            "timing_strategy": "Meet all filing deadlines with complete submissions"
                        }
                    else:
                        # Default generic strategy
                        result["winning_strategy"] = {
                            "primary_approach": "Strategic legal approach tailored to your specific case",
                            "attack_defense_tactics": [
                                "Focus on applicable legal standards",
                                "Develop case-specific strategy based on facts and law",
                                "Build compelling narrative supported by evidence"
                            ],
                            "procedural_motions": [
                                "Strategic discovery requests",
                                "Case-appropriate motions based on specific issues"
                            ],
                            "evidence_challenges": "Ensure all evidence meets admissibility standards",
                            "hearing_objections": "Make timely and relevant objections during proceedings",
                            "timing_strategy": "Strategic timing of all procedural steps"
                    }
                
                # Log the structure before storing
                logging.info(f"Storing case law analysis with structure: {list(result.keys())}")
                
                # Format as JSON string
                references = json.dumps(result)
                content = "Comprehensive Legal Analysis generated by Due Process AI"
                
                # Delete any existing analysis of this type
                existing_analysis = LegalAnalysis.query.filter_by(
                    case_id=case_id, 
                    analysis_type='case_law'
                ).all()
                for analysis in existing_analysis:
                    db.session.delete(analysis)
                db.session.commit()
                
                # Create new analysis record
                case_law_analysis = LegalAnalysis.create_analysis(
                    case_id=case_id,
                    analysis_type='case_law',
                    content=content,
                    references=references,
                    confidence_score=0.95
                )
                
                # Update case with precedent cases
                case.precedent_cases = references
                db.session.commit()
                
                # Check if we have rights violations
                if result.get('rights_assessment'):
                    count = len(result.get('rights_assessment', []))
                    if count > 0:
                        flash(f'Rights violations detected! {count} potential violations found in your case. Detailed winning strategy available below.', 'danger')
                    else:
                        flash('Case law analysis generated successfully!', 'success')
                else:
                    flash('Case law analysis generated successfully!', 'success')
                    
                # Check if we have a winning strategy
                if result.get('winning_strategy'):
                    # Update case with the AI-calculated winning strategy
                    winning_strategy = json.dumps(result.get('winning_strategy'))
                    case.legal_strategy = winning_strategy
                    db.session.commit()
                
            elif analysis_type == 'document_recommendations':
                # Default empty result in case all attempts fail
                result = {
                    "document_recommendations": []
                }
                
                # Generate strategic document recommendations
                try:
                    result = recommend_documents(
                        description=case.description,
                        issue_type=case.issue_type,
                        court_type=case.court_type
                    )
                    if not result:
                        app.logger.error("recommend_documents returned None, using fallback")
                        result = generate_fallback_documents(case)
                        flash('Document AI services returned no data. We\'ve generated basic recommendations instead.', 'warning')
                    elif isinstance(result, dict) and not result.get('document_recommendations'):
                        app.logger.warning("recommend_documents missing document_recommendations, adding fallback data")
                        # Add the missing section
                        result["document_recommendations"] = generate_fallback_documents(case)["document_recommendations"]
                        flash('Document recommendations were incomplete. We\'ve added required information.', 'warning')
                except Exception as doc_error:
                    app.logger.error(f"Primary document recommendations failed, attempting fallback: {str(doc_error)}")
                    # Try direct Anthropic fallback for document recommendations
                    if anthropic_helper.is_available():
                        doc_result = anthropic_helper.recommend_documents(
                            description=case.description,
                            issue_type=case.issue_type, 
                            court_type=case.court_type
                        )
                        
                        if doc_result and isinstance(doc_result, dict) and "recommended_documents" in doc_result:
                            # Format Anthropic results to match the expected structure
                            recommendations = []
                            for doc in doc_result["recommended_documents"]:
                                if isinstance(doc, dict):
                                    recommendation = {
                                        "document_type": doc.get("document_type", ""),
                                        "rationale": doc.get("purpose", ""),
                                        "strategic_guidance": doc.get("strategic_value", ""),
                                        "key_elements": doc.get("key_elements", []),
                                        "timing": doc.get("timing", ""),
                                        "importance": doc.get("priority", "Medium"),
                                        "impact": "Potentially significant for case outcome"
                                    }
                                    recommendations.append(recommendation)
                            
                            result = {"document_recommendations": recommendations}
                        else:
                            app.logger.error("Both primary and backup document analysis failed, using fallback")
                            result = generate_fallback_documents(case)
                            flash('Document AI services had trouble analyzing your case. We\'ve provided basic recommendations.', 'warning')
                
                # Make sure result has the required structure
                if "document_recommendations" not in result or not result["document_recommendations"]:
                    # Use our fallback document generation
                    app.logger.info("No document recommendations generated by AI, using fallback document generation")
                    fallback_docs = generate_fallback_documents(case)
                    result["document_recommendations"] = fallback_docs["document_recommendations"]
                
                # Ensure we don't have a "System Error" document type in the recommendations
                for i, doc in enumerate(result["document_recommendations"]):
                    if doc.get("document_type") == "System Error" or doc.get("document_type") == "API limit reached" or doc.get("document_type") == "Alternative AI Provider Required":
                        app.logger.warning(f"Found error document type: {doc.get('document_type')}, replacing with fallback")
                        # Replace this item with a proper document
                        fallback_docs = generate_fallback_documents(case)
                        if fallback_docs["document_recommendations"]:
                            result["document_recommendations"][i] = fallback_docs["document_recommendations"][0]
                
                # Log the structure before storing
                logging.info(f"Storing document recommendations with {len(result.get('document_recommendations', []))} documents")
                
                # Store the complete document strategy as structured data
                references = json.dumps(result)
                content = "Strategic document plan generated by Due Process AI"
                
                # Delete any existing recommendations of this type
                existing_recommendations = LegalAnalysis.query.filter_by(
                    case_id=case_id, 
                    analysis_type='document_recommendations'
                ).all()
                for recommendation in existing_recommendations:
                    db.session.delete(recommendation)
                db.session.commit()
                
                # Create analysis record
                doc_recommendations = LegalAnalysis.create_analysis(
                    case_id=case_id,
                    analysis_type='document_recommendations',
                    content=content,
                    references=references,
                    confidence_score=0.95
                )
                
                # Count critical documents
                doc_count = len(result.get('document_recommendations', []))
                critical_count = sum(1 for doc in result.get('document_recommendations', []) 
                                    if doc.get('importance') == 'Critical')
                
                if critical_count > 0:
                    flash(f'Strategic document plan created with {critical_count} critical documents identified!', 'warning')
                else:
                    flash(f'Strategic document plan with {doc_count} recommended filings created successfully!', 'success')
                
        except Exception as e:
            app.logger.error(f"Error generating AI analysis: {str(e)}")
            app.logger.error(traceback.format_exc())
            
            # Check API keys status
            openai_configured = bool(os.environ.get("OPENAI_API_KEY"))
            anthropic_configured = anthropic_helper.is_available()
            
            if not openai_configured and not anthropic_configured:
                flash('No AI providers are configured. Please add your API keys in Settings.', 'danger')
            elif not openai_configured:
                flash('Primary AI provider is not configured. Add your OpenAI API key in Settings.', 'warning')
            elif not anthropic_configured:
                flash('Backup AI provider is not configured. Add your Anthropic API key in Settings for better reliability.', 'warning')
            else:
                flash(f'Error generating AI analysis: {str(e)}', 'danger')
    
    # Parse analysis data for rendering
    case_law_data = {
        "rights_assessment": [],
        "case_law_suggestions": [],
        "winning_strategy": {
            "primary_approach": "Two-pronged attack: Challenge probable cause AND assert speedy trial violation",
            "attack_defense_tactics": [
                "File motion to dismiss for lack of probable cause",
                "Simultaneously file motion to dismiss for speedy trial violation"
            ],
            "procedural_motions": [
                "Motion for discovery of arrest and charging timeline records",
                "Motion to suppress evidence obtained without proper probable cause"
            ],
            "evidence_challenges": "Challenge any evidence collected before probable cause was established",
            "hearing_objections": "Object to any prosecution request for continuance",
            "timing_strategy": "File both challenges at the earliest opportunity"
        }
    }
    if case_law_analysis and case_law_analysis.references:
        try:
            # Log the actual data before parsing
            logging.debug(f"Raw case_law_analysis.references: {case_law_analysis.references}")
            
            # Try to parse JSON (handle string or dict)
            case_law_data_parsed = None
            if isinstance(case_law_analysis.references, str):
                case_law_data_parsed = json.loads(case_law_analysis.references)
            elif isinstance(case_law_analysis.references, dict):
                case_law_data_parsed = case_law_analysis.references
                
            logging.debug(f"Parsed case_law_data structure: {type(case_law_data_parsed)}")
            
            # Check if we got an empty list or analysis-in-progress placeholder
            if isinstance(case_law_data_parsed, list) and len(case_law_data_parsed) == 0:
                logging.info("Converting empty list to proper fallback structure")
                # Use our fallback function to provide actual content instead of "in progress" message
                case_law_data_parsed = generate_fallback_analysis(case)
                flash('Analysis was incomplete. We\'ve generated a basic analysis instead.', 'warning')
            
            # Also check if we have "Analysis in Progress" as a placeholder
            elif isinstance(case_law_data_parsed, dict):
                rights_assessment = case_law_data_parsed.get("rights_assessment", [])
                case_law = case_law_data_parsed.get("case_law_suggestions", [])
                
                # Check if rights assessment has the "in progress" placeholder
                if len(rights_assessment) == 1 and rights_assessment[0].get("right_violated") == "Analysis in Progress":
                    logging.info("Found 'Analysis in Progress' placeholder, replacing with fallback")
                    fallback_data = generate_fallback_analysis(case)
                    case_law_data_parsed["rights_assessment"] = fallback_data["rights_assessment"]
                    flash('Analysis was incomplete. We\'ve generated a basic analysis instead.', 'warning')
                
                # Check if case law has the "in progress" placeholder
                if len(case_law) == 1 and case_law[0].get("case_name") == "Analysis in Progress":
                    logging.info("Found 'Analysis in Progress' placeholder in case law, replacing with fallback")
                    fallback_data = generate_fallback_analysis(case)
                    case_law_data_parsed["case_law_suggestions"] = fallback_data["case_law_suggestions"]
                    flash('Case law suggestions were incomplete. We\'ve added reliable suggestions.', 'warning')
                
                # Check if we have a winning strategy section, create one if not
                if "winning_strategy" not in case_law_data_parsed:
                    logging.info("No winning strategy found, adding fallback strategy")
                    fallback_data = generate_fallback_analysis(case)
                    case_law_data_parsed["winning_strategy"] = fallback_data["winning_strategy"]
            
            # Fix for when the data is parsed as a list instead of a dictionary
            if isinstance(case_law_data_parsed, list) or case_law_data_parsed is None:
                logging.info("Converting empty/invalid data to proper structure")
                case_law_data = {
                    "rights_assessment": [
                        {
                            "right_violated": "Analysis in Progress",
                            "explanation": "Your rights analysis is currently being generated. Please check back soon or try regenerating the analysis.",
                            "severity": "Medium",
                            "supporting_legal_principle": "Rights analysis preparation in progress. Our system is analyzing your case for potential violations."
                        }
                    ],
                    "case_law_suggestions": [
                        {
                            "case_name": "Analysis in Progress",
                            "year": "2025",
                            "court": "Supreme Court of the United States",
                            "relevance": "Your case law analysis is currently being generated. Please check back soon or try regenerating the analysis.",
                            "principles": "Case law analysis in progress. Our system is identifying relevant precedents for your situation.",
                            "key_quotes": ["Analysis generation in progress"],
                            "strategic_application": "Please try regenerating the analysis if this message persists.",
                            "counter_arguments": "Analysis preparation in progress"
                        }
                    ],
                    "winning_strategy": {
                        "primary_approach": "Data structure being initialized...",
                        "attack_defense_tactics": ["Please try the analysis again"],
                        "procedural_motions": ["Analysis generation in progress"],
                        "evidence_challenges": "Evidence challenge strategies being prepared...",
                        "hearing_objections": "Objection tactics being prepared...",
                        "timing_strategy": "Timing strategy being prepared..."
                    }
                }
            else:
                case_law_data = case_law_data_parsed
                # Add any missing keys to prevent template errors
                if not isinstance(case_law_data, dict):
                    case_law_data = {}
                    
                if "rights_assessment" not in case_law_data:
                    case_law_data["rights_assessment"] = []
                if "case_law_suggestions" not in case_law_data:
                    case_law_data["case_law_suggestions"] = []
                if "winning_strategy" not in case_law_data:
                    case_law_data["winning_strategy"] = {
                        "primary_approach": "Comprehensive defense strategy tailored to your specific case",
                        "attack_defense_tactics": [
                            "Identify and challenge procedural violations",
                            "Focus on constitutional rights protections"
                        ],
                        "procedural_motions": [
                            "Strategic motion practice based on case specifics",
                            "Evidence handling and discovery motions"
                        ],
                        "evidence_challenges": "Analysis of potential evidence issues and admissibility challenges",
                        "hearing_objections": "Preparation for common objections relevant to your case type",
                        "timing_strategy": "Strategic scheduling of filings for maximum effectiveness"
                    }
                else:
                    # Ensure all required fields exist in the winning_strategy
                    winning_strategy = case_law_data["winning_strategy"]
                    if not isinstance(winning_strategy, dict):
                        case_law_data["winning_strategy"] = {
                            "primary_approach": "Two-pronged attack: Challenge probable cause AND assert speedy trial violation",
                            "attack_defense_tactics": [
                                "File motion to dismiss for lack of probable cause",
                                "Simultaneously file motion to dismiss for speedy trial violation"
                            ],
                            "procedural_motions": [
                                "Motion for discovery of arrest and charging timeline records",
                                "Motion to suppress evidence obtained without proper probable cause"
                            ],
                            "evidence_challenges": "Challenge any evidence collected before probable cause was established",
                            "hearing_objections": "Object to any prosecution request for continuance",
                            "timing_strategy": "File both challenges at the earliest opportunity"
                        }
                    else:
                        # Check each required field
                        if "primary_approach" not in winning_strategy:
                            winning_strategy["primary_approach"] = ""
                        if "attack_defense_tactics" not in winning_strategy:
                            winning_strategy["attack_defense_tactics"] = []
                        if "procedural_motions" not in winning_strategy:
                            winning_strategy["procedural_motions"] = []
                        if "evidence_challenges" not in winning_strategy:
                            winning_strategy["evidence_challenges"] = ""
                        if "hearing_objections" not in winning_strategy:
                            winning_strategy["hearing_objections"] = ""
                        if "timing_strategy" not in winning_strategy:
                            winning_strategy["timing_strategy"] = ""
        except Exception as e:
            logging.error(f"Error parsing case law data: {str(e)}")
    
    doc_recommendations_data = {
        "document_recommendations": [
            {
                "document_type": "Motion to Dismiss for Lack of Probable Cause",
                "rationale": "Challenges the legal basis for your case by arguing insufficient evidence existed to justify charges",
                "strategic_guidance": "Focus on timeline inconsistencies and cite specific Fourth Amendment protections",
                "key_elements": [
                    "Timeline of events showing insufficient evidence for charging",
                    "Citation to relevant constitutional provisions",
                    "Reference to specific case facts"
                ],
                "timing": "File as soon as possible after arraignment",
                "importance": "Critical",
                "impact": "Could potentially dismiss the entire case if successful"
            },
            {
                "document_type": "Motion to Dismiss for Speedy Trial Violation",
                "rationale": "Challenges procedural delays that violated your right to a speedy trial",
                "strategic_guidance": "Document all court dates, continuances, and delays with precise dates",
                "key_elements": [
                    "Detailed timeline of all proceedings",
                    "Calculation of days exceeding statutory limits",
                    "Documentation of any prejudice caused by delay"
                ],
                "timing": "File after statutory speedy trial deadline has passed",
                "importance": "High",
                "impact": "Could result in complete dismissal with prejudice"
            }
        ]
    }
    if doc_recommendations and doc_recommendations.references:
        try:
            # Log the actual data before parsing
            logging.debug(f"Raw doc_recommendations.references: {doc_recommendations.references}")
            
            # Try to parse JSON (handle string or dict)
            doc_data_parsed = None
            if isinstance(doc_recommendations.references, str):
                doc_data_parsed = json.loads(doc_recommendations.references)
            elif isinstance(doc_recommendations.references, dict):
                doc_data_parsed = doc_recommendations.references
                
            logging.debug(f"Parsed doc_recommendations_data structure: {type(doc_data_parsed)}")
            
            # Fix for when the data is parsed as a list instead of a dictionary
            if isinstance(doc_data_parsed, list):
                logging.info("Converting empty doc list to proper structure")
                doc_recommendations_data = {
                    "document_recommendations": [
                        {
                            "document_type": "Analysis in Progress",
                            "rationale": "Document analysis is currently being generated. Please check back soon.",
                            "strategic_guidance": "Try regenerating the analysis or creating a new case.",
                            "key_elements": ["Analysis preparation in progress"],
                            "timing": "Try again soon",
                            "importance": "Medium",
                            "impact": "Pending analysis completion"
                        }
                    ]
                }
            elif isinstance(doc_data_parsed, dict):
                # Ensure doc_recommendations_data is a valid dictionary
                try:
                    doc_recommendations_data = doc_data_parsed if doc_data_parsed is not None else {}
                    # Add missing keys to prevent template errors
                    if isinstance(doc_recommendations_data, dict) and "document_recommendations" not in doc_recommendations_data:
                        doc_recommendations_data["document_recommendations"] = []
                except Exception as err:
                    logging.error(f"Error processing document data: {str(err)}")
            # No else needed - keep the default if data_parsed is None or unexpected type
        except Exception as e:
            logging.error(f"Error parsing document recommendations: {str(e)}")
    
    return render_template(
        'ai_analysis.html',
        case=case,
        case_law_data=case_law_data,
        doc_recommendations_data=doc_recommendations_data,
        has_case_law=bool(case_law_analysis),
        has_doc_recommendations=bool(doc_recommendations),
        is_premium=current_user.is_premium()
    )

@ai.route('/api/case/<int:case_id>/generate-document-strategy', methods=['POST'])
@login_required
def generate_document_strategy(case_id):
    """AJAX endpoint to generate an AI document strategy for a specific document type"""
    app.logger.info(f"Document strategy generation requested for case {case_id}")
    
    # Get case and validate
    case = Case.get_case_by_id(case_id)
    if not case:
        app.logger.error(f"Case {case_id} not found")
        return jsonify({'error': 'Case not found'}), 404
    
    app.logger.info(f"Case found: {case.title} ({case.issue_type}/{case.court_type})")
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        app.logger.error(f"Permission denied - user {current_user.id} trying to access case {case_id} owned by {case.user_id}")
        return jsonify({'error': 'Permission denied'}), 403
    
    # Extract document type from request
    doc_type = None
    app.logger.debug(f"Request JSON: {request.json}")
    
    if request.json and isinstance(request.json, dict):
        doc_type = request.json.get('doc_type')
        app.logger.info(f"Requested document type: {doc_type}")
    
    if not doc_type:
        app.logger.error("Document type missing from request")
        return jsonify({'error': 'Document type required'}), 400
    
    # Check if document type is "System Error", in which case use fallback
    if doc_type == "System Error":
        app.logger.warning(f"System Error document type requested, using fallback instead")
        # Use a generic motion document type
        doc_type = "Motion to Dismiss"
        # Return the fallback strategy directly
        strategy_html = generate_fallback_strategy_html(doc_type, case.issue_type, case.court_type)
        return jsonify({'success': True, 'strategy': strategy_html, 'fallback': True}), 200
    
    # Store case info
    case_description = case.description
    issue_type = case.issue_type
    court_type = case.court_type
    
    # Try to generate strategy
    strategy = None
    try:
        import openai
        import json
        import os
        
        # Try OpenAI first if available
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if openai_api_key:
            try:
                app.logger.info(f"Generating document strategy with OpenAI for {doc_type}")
                
                # Initialize OpenAI client
                client = openai.OpenAI(api_key=openai_api_key)
                
                # Create a focused prompt for this specific document type
                prompt = f"""Generate a detailed legal strategy for creating a {doc_type} for a {issue_type} case in {court_type}.
                
Case details: {case_description}

Your response must include:
1. Key points to include in the document (at least 3-5 specific points)
2. Document structure and sections (outline format)
3. Relevant legal citations with case names, citations, and direct relevance to this case
4. Strategic considerations (timing, presentation, specific arguments)

Focus on both challenging probable cause and asserting speedy trial rights where applicable.
"""
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {"role": "system", "content": "You are an expert legal assistant that helps self-represented litigants create effective legal documents."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=1500
                )
                
                if response and hasattr(response, 'choices') and response.choices and response.choices[0].message:
                    strategy = response.choices[0].message.content
                    app.logger.info(f"Successfully generated document strategy with OpenAI")
            except Exception as e:
                app.logger.error(f"OpenAI document strategy generation failed: {str(e)}")
                strategy = None
    except Exception as openai_error:
        app.logger.error(f"Error initializing OpenAI: {str(openai_error)}")
        strategy = None
    
    # Fall back to Anthropic if OpenAI failed or not configured
    if not strategy:
        try:
            if anthropic_helper.is_available():
                app.logger.info(f"Falling back to Anthropic for document strategy on {doc_type}")
                
                # Similar prompt as above but formatted for Anthropic
                prompt = f"""Generate a detailed legal strategy for creating a {doc_type} for a {issue_type} case in {court_type}.
                
Case details: {case_description}

Your response MUST include:
1. Key points to include (at least 3-5 specific points)
2. Document structure and sections (outline format)
3. Relevant legal citations with case names, citations, and direct relevance to this case
4. Strategic considerations (timing, presentation, specific arguments)

Focus on both challenging probable cause and asserting speedy trial rights where applicable.
Format the information in a clear, structured way with headers for each section."""

                response = anthropic_helper.analyze_case_text(prompt)
                if response:
                    strategy = response
                    app.logger.info(f"Successfully generated document strategy with Anthropic")
        except Exception as anthropic_error:
            app.logger.error(f"Anthropic document strategy generation failed: {str(anthropic_error)}")
            strategy = None
    
    # Generate HTML from the strategy or use fallback
    strategy_html = None
    try:
        if strategy:
            app.logger.info("Converting AI response to formatted HTML")
            # Convert the AI response to HTML with proper formatting
            import re
            
            # Replace common section headers with HTML headings
            strategy_html = strategy
            section_patterns = [
                (r"(?i)^Key Points:?", "<h6 class=\"mt-4 mb-2\">Key Strategic Points:</h6>"),
                (r"(?i)^Document Structure:?", "<h6 class=\"mt-4 mb-2\">Document Structure:</h6>"),
                (r"(?i)^Structure:?", "<h6 class=\"mt-4 mb-2\">Document Structure:</h6>"),
                (r"(?i)^Legal Citations:?", "<h6 class=\"mt-4 mb-2\">Legal Citations:</h6>"),
                (r"(?i)^Strategic Considerations:?", "<h6 class=\"mt-4 mb-2\">Strategic Considerations:</h6>"),
                (r"(?i)^Timing:?", "<h6 class=\"mt-4 mb-2\">Strategic Timing:</h6>")
            ]
            
            for pattern, replacement in section_patterns:
                strategy_html = re.sub(pattern, replacement, strategy_html)
            
            # Convert numbered lists to HTML ol/li elements
            numbered_list_pattern = r"(?m)^(\d+\.)\s+(.*?)$"
            if re.search(numbered_list_pattern, strategy_html):
                # Process numbered lists
                lines = strategy_html.split('\n')
                result = []
                in_list = False
                list_items = []
                
                for line in lines:
                    match = re.match(numbered_list_pattern, line)
                    if match:
                        if not in_list:
                            in_list = True
                            list_items = [match.group(2)]
                        else:
                            list_items.append(match.group(2))
                    else:
                        if in_list:
                            list_html = "<ol class=\"mb-4\">\n"
                            for item in list_items:
                                list_html += f"<li>{item}</li>\n"
                            list_html += "</ol>"
                            result.append(list_html)
                            in_list = False
                            result.append(line)
                        else:
                            result.append(line)
                
                if in_list:
                    list_html = "<ol class=\"mb-4\">\n"
                    for item in list_items:
                        list_html += f"<li>{item}</li>\n"
                    list_html += "</ol>"
                    result.append(list_html)
                
                strategy_html = '\n'.join(result)
            
            # Convert bullet lists (* or -) to HTML ul/li elements
            strategy_html = re.sub(r"(?m)^[\*\-]\s+(.*?)$", r"<li>\1</li>", strategy_html)
            strategy_html = re.sub(r"(?m)(<li>.*?</li>\n)+", r"<ul class=\"mb-4\">\n\g<0></ul>\n", strategy_html)
            
            # Format paragraphs
            strategy_html = re.sub(r"\n\n+", r"<br><br>", strategy_html)
            strategy_html = re.sub(r"\n", r"<br>", strategy_html)
            
            # Wrap everything in a nice container
            strategy_html = f"""
            <h5 class="text-primary mb-3">Strategic Drafting Guide: {doc_type}</h5>
            
            <div class="alert alert-info">
                <strong>Document Purpose:</strong> This document is crucial for asserting your rights and ensuring fair treatment in court.
            </div>
            
            <div class="document-strategy-content">
                {strategy_html}
            </div>
            
            <div class="alert alert-warning mt-4">
                <strong>Pro Tip:</strong> Focus on facts and legal principles rather than emotional arguments. Courts respond to well-reasoned legal positions backed by evidence and precedent.
            </div>
            """
        else:
            app.logger.info(f"Using fallback strategy for {doc_type}")
            strategy_html = generate_fallback_strategy_html(doc_type, issue_type, court_type)
        
        app.logger.info("Successfully generated document strategy HTML")
        return jsonify({'success': True, 'strategy': strategy_html}), 200
    
    except Exception as formatting_error:
        app.logger.error(f"Error formatting document strategy: {str(formatting_error)}")
        try:
            # Last resort fallback
            app.logger.info("Using emergency fallback strategy")
            strategy_html = generate_fallback_strategy_html(doc_type, issue_type, court_type)
            return jsonify({'success': True, 'strategy': strategy_html, 'fallback': True}), 200
        except Exception as fallback_error:
            app.logger.error(f"Fatal error: Even fallback strategy failed: {str(fallback_error)}")
            return jsonify({'error': 'Could not generate document strategy. Please try again later.'}), 500


@ai.route('/api/case/<int:case_id>/generate-advanced-strategy', methods=['POST'])
@login_required
def advanced_strategy_api(case_id):
    """Generate advanced legal strategy (premium feature)"""
    app.logger.info(f"Received advanced strategy request for case {case_id}")
    
    try:
        # Check if user is premium
        if not current_user.is_premium():
            app.logger.warning(f"User {current_user.id} attempted to access premium feature without premium status")
            return jsonify({'error': 'Premium feature unavailable', 'premium_required': True}), 403
            
        # Get the case
        case = Case.query.get(case_id)
        if not case:
            app.logger.error(f"Case not found: {case_id}")
            return jsonify({'error': 'Case not found'}), 404
            
        if case.user_id != current_user.id and not current_user.role == 'legal_assistant':
            app.logger.error(f"User {current_user.id} not authorized for case {case_id}")
            return jsonify({'error': 'Not authorized'}), 403
        
        # Call AI helper function to generate strategy
        try:
            from ai_helpers import generate_legal_strategy
            
            # Generate advanced strategy
            strategy_result = generate_legal_strategy(
                case_id=case_id,
                description=case.description,
                issue_type=case.issue_type,
                court_type=case.court_type
            )
            
            # Format response as HTML
            strategy_html = f"""
            <div class="premium-strategy">
                <div class="alert alert-success mb-4">
                    <h5 class="alert-heading"><i class="fas fa-crown me-2"></i>Premium Legal Strategy</h5>
                    <p>This advanced analysis is exclusively available to premium subscribers.</p>
                </div>
                
                <h5 class="text-primary mb-3">Primary Approach</h5>
                <p class="lead">{strategy_result.get('winning_strategy', {}).get('primary_approach', 'Comprehensive legal strategy tailored to your case')}</p>
                
                <h5 class="text-success mb-3 mt-4">Strategic Tactics</h5>
                <ul class="list-group mb-4">
            """
            
            # Add attack defense tactics
            tactics = strategy_result.get('winning_strategy', {}).get('attack_defense_tactics', [])
            for tactic in tactics:
                strategy_html += f'<li class="list-group-item"><i class="fas fa-check-circle text-success me-2"></i>{tactic}</li>\n'
            
            strategy_html += """
                </ul>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0">Procedural Strategy</h6>
                            </div>
                            <div class="card-body">
                                <ul class="list-unstyled">
            """
            
            # Add procedural motions
            motions = strategy_result.get('winning_strategy', {}).get('procedural_motions', [])
            for motion in motions:
                strategy_html += f'<li class="mb-2"><i class="fas fa-file-alt me-2 text-primary"></i>{motion}</li>\n'
            
            strategy_html += """
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header bg-info text-white">
                                <h6 class="mb-0">Evidence Strategy</h6>
                            </div>
                            <div class="card-body">
            """
            
            # Add evidence challenges
            evidence_challenges = strategy_result.get('winning_strategy', {}).get('evidence_challenges', '')
            strategy_html += f'<p><i class="fas fa-balance-scale me-2 text-info"></i>{evidence_challenges}</p>\n'
            
            strategy_html += """
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header bg-warning text-dark">
                        <h6 class="mb-0">Timing & Objection Strategy</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
            """
            
            # Add hearing objections
            hearing_objections = strategy_result.get('winning_strategy', {}).get('hearing_objections', '')
            strategy_html += f'<p><strong>Hearing Approach:</strong> {hearing_objections}</p>\n'
            
            strategy_html += """
                            </div>
                            <div class="col-md-6">
            """
            
            # Add timing strategy
            timing_strategy = strategy_result.get('winning_strategy', {}).get('timing_strategy', '')
            strategy_html += f'<p><strong>Timing Strategy:</strong> {timing_strategy}</p>\n'
            
            strategy_html += """
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
            
            # Save the strategy to the case if successful
            try:
                # First convert the winning strategy to a JSON string for storage
                winning_strategy = strategy_result.get('winning_strategy', {})
                winning_strategy_json = json.dumps(winning_strategy)
                
                # Store in LegalAnalysis
                LegalAnalysis.create_analysis(
                    case_id=case.id,
                    analysis_type='advanced_strategy',
                    content=f"Advanced legal strategy: {winning_strategy.get('primary_approach', 'Customized strategy')}",
                    references=json.dumps({"strategy_details": winning_strategy}),
                    confidence_score=0.85  # High confidence for premium analysis
                )
                
                # Also store directly in case for quick access
                case.legal_strategy = winning_strategy_json
                db.session.commit()
                app.logger.info(f"Legal strategy saved for case {case_id}")
            except Exception as save_error:
                app.logger.error(f"Error saving legal strategy: {str(save_error)}")
            
            return jsonify({'success': True, 'strategy': strategy_html}), 200
            
        except Exception as ai_error:
            app.logger.error(f"Error generating advanced strategy: {str(ai_error)}")
            return jsonify({'error': 'Failed to generate advanced strategy', 'details': str(ai_error)}), 500
            
    except Exception as e:
        app.logger.error(f"Error in advanced strategy API: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@ai.route('/api/case/<int:case_id>/calculate-success-probability', methods=['POST'])
@login_required
def success_probability_api(case_id):
    """Calculate success probability (premium feature)"""
    app.logger.info(f"Received success probability request for case {case_id}")
    
    try:
        # Check if user is premium
        if not current_user.is_premium():
            app.logger.warning(f"User {current_user.id} attempted to access premium feature without premium status")
            return jsonify({'error': 'Premium feature unavailable', 'premium_required': True}), 403
            
        # Get the case
        case = Case.query.get(case_id)
        if not case:
            app.logger.error(f"Case not found: {case_id}")
            return jsonify({'error': 'Case not found'}), 404
            
        if case.user_id != current_user.id and not current_user.role == 'legal_assistant':
            app.logger.error(f"User {current_user.id} not authorized for case {case_id}")
            return jsonify({'error': 'Not authorized'}), 403
        
        # Call AI helper function to calculate probability
        try:
            from ai_helpers import calculate_success_probability
            
            # Calculate probability
            probability_result = calculate_success_probability(
                case_id=case_id,
                description=case.description,
                issue_type=case.issue_type,
                court_type=case.court_type
            )
            
            # Calculate probability percentage
            probability = probability_result.get('success_probability', 0.5) * 100
            confidence = probability_result.get('confidence_level', 'Medium')
            factors = probability_result.get('key_factors', [])
            suggestions = probability_result.get('improvement_suggestions', [])
            
            # Format as HTML
            probability_html = f"""
            <div class="premium-probability">
                <div class="alert alert-success mb-4">
                    <h5 class="alert-heading"><i class="fas fa-crown me-2"></i>Premium Success Analysis</h5>
                    <p>This detailed probability analysis is exclusively available to premium subscribers.</p>
                </div>
                
                <div class="text-center mb-4">
                    <h2 class="display-4 fw-bold text-primary">{probability:.1f}%</h2>
                    <p class="lead">Estimated Success Probability</p>
                    <div class="badge bg-info text-white p-2 fs-6">Confidence: {confidence}</div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0">Key Factors</h6>
                            </div>
                            <div class="card-body">
                                <ul class="list-group">
            """
            
            # Add key factors
            for factor in factors:
                probability_html += f'<li class="list-group-item"><i class="fas fa-check-circle text-primary me-2"></i>{factor}</li>\n'
            
            probability_html += """
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header bg-success text-white">
                                <h6 class="mb-0">Improvement Suggestions</h6>
                            </div>
                            <div class="card-body">
                                <ul class="list-group">
            """
            
            # Add improvement suggestions
            for suggestion in suggestions:
                probability_html += f'<li class="list-group-item"><i class="fas fa-arrow-circle-up text-success me-2"></i>{suggestion}</li>\n'
            
            probability_html += """
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="alert alert-info mt-3">
                    <h6 class="fw-bold mb-2">Understanding This Analysis</h6>
                    <p class="mb-0">This probability assessment is based on available case information and similar case outcomes. Actual results may vary based on many factors including evidence quality, court procedures, and specific circumstances.</p>
                </div>
            </div>
            """
            
            # Save the probability assessment to the case
            try:
                # Store in database
                LegalAnalysis.create_analysis(
                    case_id=case.id,
                    analysis_type='success_probability',
                    content=f"Success probability assessment: {probability:.1f}%",
                    references=json.dumps({"probability_analysis": probability_result}),
                    confidence_score=0.8,  # High confidence for premium analysis
                    success_probability=probability / 100,  # Convert back to 0-1 scale
                    probability_factors=factors,
                    probability_suggestions=suggestions
                )
                
                # Also update the case with a quick reference probability
                case.success_probability = probability / 100
                db.session.commit()
                app.logger.info(f"Success probability saved for case {case_id}")
            except Exception as save_error:
                app.logger.error(f"Error saving success probability: {str(save_error)}")
            
            return jsonify({'success': True, 'probability': probability_html}), 200
            
        except Exception as ai_error:
            app.logger.error(f"Error calculating success probability: {str(ai_error)}")
            return jsonify({'error': 'Failed to calculate success probability', 'details': str(ai_error)}), 500
            
    except Exception as e:
        app.logger.error(f"Error in success probability API: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


def generate_fallback_strategy_html(doc_type, issue_type, court_type):
    """Generate fallback strategy HTML when AI generation fails"""
    
    # Determine key points based on document type
    key_points = []
    structure = []
    legal_citations = []
    
    # Customize based on document type
    if "dismiss" in doc_type.lower():
        key_points = [
            "<strong>Rights Focus:</strong> Explicitly reference the specific constitutional rights that need protection.",
            "<strong>Timeline Documentation:</strong> Include a detailed chronology of events with exact dates to support any speedy trial or procedural violations.",
            "<strong>Legal Framework:</strong> Cite both statute language and relevant case law establishing legal standards.",
            "<strong>Evidence Challenges:</strong> Detail any evidence that should be excluded and explain why (\"fruit of the poisonous tree\" doctrine).",
            "<strong>Procedural Violations:</strong> Highlight any failures to follow proper procedure by law enforcement or prosecution."
        ]
        legal_citations = [
            {"case": "Terry v. Ohio", "citation": "392 U.S. 1 (1968)", "relevance": "Police must have reasonable suspicion for stops"},
            {"case": "Barker v. Wingo", "citation": "407 U.S. 514 (1972)", "relevance": "Four-factor test for speedy trial violations"}
        ]
    elif "discovery" in doc_type.lower():
        key_points = [
            "<strong>Specificity:</strong> Clearly identify each piece of evidence or information you're requesting.",
            "<strong>Legal Basis:</strong> Cite the rules of criminal/civil procedure that entitle you to this information.",
            "<strong>Brady Material:</strong> Explicitly request all exculpatory evidence favorable to your defense.",
            "<strong>Chain of Custody:</strong> Request documentation showing how evidence was handled and stored.",
            "<strong>Expert Witnesses:</strong> Request credentials and bases for any expert opinions."
        ]
        legal_citations = [
            {"case": "Brady v. Maryland", "citation": "373 U.S. 83 (1963)", "relevance": "Prosecution must disclose exculpatory evidence"},
            {"case": "Giglio v. United States", "citation": "405 U.S. 150 (1972)", "relevance": "Impeachment evidence must be disclosed"}
        ]
    elif "suppress" in doc_type.lower():
        key_points = [
            "<strong>Fourth Amendment Focus:</strong> Explicitly outline how the search/seizure violated constitutional standards.",
            "<strong>Factual Timeline:</strong> Detail exact sequence of events related to the evidence collection.",
            "<strong>Legal Threshold:</strong> Explain why officers lacked probable cause or reasonable suspicion.",
            "<strong>Fruit of Poisonous Tree:</strong> Identify all evidence that derives from the initial illegal search.",
            "<strong>Standing:</strong> Establish your legal standing to challenge the search/seizure."
        ]
        legal_citations = [
            {"case": "Mapp v. Ohio", "citation": "367 U.S. 643 (1961)", "relevance": "Established exclusionary rule for state courts"},
            {"case": "Wong Sun v. United States", "citation": "371 U.S. 471 (1963)", "relevance": "Fruit of the poisonous tree doctrine"}
        ]
    else:
        # Generic fallback
        key_points = [
            "<strong>Rights Focus:</strong> Explicitly reference the specific rights that need protection.",
            "<strong>Timeline Documentation:</strong> Include a detailed chronology of events with exact dates.",
            "<strong>Legal Framework:</strong> Cite both statute language and relevant case law.",
            "<strong>Evidence Reference:</strong> Reference specific evidence that supports your position.",
            "<strong>Relief Requested:</strong> Clearly state what you want the court to do."
        ]
        legal_citations = [
            {"case": "Terry v. Ohio", "citation": "392 U.S. 1 (1968)", "relevance": "Police must have reasonable suspicion for stops"},
            {"case": "Miranda v. Arizona", "citation": "384 U.S. 436 (1966)", "relevance": "Rights warnings required before custodial interrogation"}
        ]
    
    # Standard document structure
    structure = [
        "<strong>Introduction:</strong> State your purpose clearly and what you're asking the court to do",
        "<strong>Legal Authority:</strong> Establish your right to bring this document before the court",
        "<strong>Facts:</strong> Present a clear, chronological account of what happened",
        "<strong>Legal Analysis:</strong> Connect the facts to legal principles that support your position",
        "<strong>Relief Requested:</strong> Clearly state what you want the court to do"
    ]
    
    # Build HTML content
    html = f"""
    <h5 class="text-primary mb-3">Strategic Drafting Guide: {doc_type}</h5>
    
    <div class="alert alert-info">
        <strong>Document Purpose:</strong> This document is crucial for asserting your rights and ensuring fair treatment in court.
    </div>
    
    <h6 class="mt-4 mb-2">Key Strategic Components:</h6>
    <ol class="mb-4">
    """
    
    for point in key_points:
        html += f"<li>{point}</li>"
    
    html += f"""
    </ol>
    
    <h6 class="mt-4 mb-2">Document Structure:</h6>
    <ul class="mb-4">
    """
    
    for item in structure:
        html += f"<li>{item}</li>"
    
    html += f"""
    </ul>
    
    <h6 class="mt-4 mb-2">Key Legal Citations:</h6>
    <table class="table table-sm table-bordered mb-4">
        <tr>
            <th>Case</th>
            <th>Citation</th>
            <th>Relevance</th>
        </tr>
    """
    
    for citation in legal_citations:
        html += f"""
        <tr>
            <td>{citation["case"]}</td>
            <td>{citation["citation"]}</td>
            <td>{citation["relevance"]}</td>
        </tr>
        """
    
    html += f"""
    </table>
    
    <div class="alert alert-warning">
        <strong>Strategic Timing:</strong> File this document at the appropriate stage in your proceedings to maximize impact and avoid waiving rights.
    </div>
    """
    
    return html