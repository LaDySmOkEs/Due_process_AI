import json
import logging
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_required, current_user
from models import Case, Evidence, LegalAnalysis, db
import anthropic_helper

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create blueprint
evidence_ai = Blueprint('evidence_ai', __name__)

@evidence_ai.route('/case/<int:case_id>/evidence/analysis', methods=['GET', 'POST'])
@login_required
def evidence_analysis(case_id):
    """Display and process AI-powered evidence analysis"""
    # Get case details
    case = Case.query.get_or_404(case_id)
    
    # Security check - make sure the current user owns this case
    if case.user_id != current_user.id:
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Get evidence items
    evidence_items = case.get_evidence()
    
    # Check for existing evidence relevance analysis
    evidence_relevance = LegalAnalysis.query.filter_by(
        case_id=case_id, 
        analysis_type='evidence_relevance'
    ).first()
    
    # Check for existing exhibit organization
    exhibit_org = LegalAnalysis.query.filter_by(
        case_id=case_id, 
        analysis_type='exhibit_organization'
    ).first()
    
    # Initialize analysis data
    relevance_analysis = None
    exhibit_organization = None
    
    # Load existing analyses if available
    if evidence_relevance:
        try:
            relevance_analysis = json.loads(evidence_relevance.content)
        except:
            app.logger.error("Failed to parse evidence relevance JSON")
    
    if exhibit_org:
        try:
            exhibit_organization = json.loads(exhibit_org.content)
        except:
            app.logger.error("Failed to parse exhibit organization JSON")
    
    # Handle POST request - Generate new analysis
    if request.method == 'POST':
        analysis_type = request.form.get('analysis_type')
        
        # If there's no evidence, don't attempt analysis
        if not evidence_items:
            flash('Please add evidence to your case before requesting analysis.', 'warning')
            return redirect(url_for('cases.upload_evidence', case_id=case_id))
        
        # Get case details for AI analysis
        description = case.description
        issue_type = case.issue_type
        court_type = case.court_type
        
        # Format evidence for AI analysis
        evidence_descriptions = [
            {
                "id": i+1,
                "type": item.evidence_type,
                "description": item.description,
                "platform": item.platform if item.platform else None,
                "file_type": item.file_type if item.file_type else None
            } for i, item in enumerate(evidence_items)
        ]
        
        # Evidence Relevance Analysis
        if analysis_type == 'evidence_relevance':
            try:
                # Perform the AI analysis
                ai_result = analyze_evidence_relevance(
                    case_id, 
                    description, 
                    issue_type, 
                    court_type, 
                    evidence_descriptions
                )
                
                if ai_result:
                    # Save or update the analysis in the database
                    if evidence_relevance:
                        evidence_relevance.content = json.dumps(ai_result)
                        db.session.commit()
                    else:
                        LegalAnalysis.create_analysis(
                            case_id=case_id,
                            analysis_type='evidence_relevance',
                            content=json.dumps(ai_result)
                        )
                    
                    flash('Evidence relevance analysis generated successfully.', 'success')
                    return redirect(url_for('evidence_ai.evidence_analysis', case_id=case_id))
                else:
                    flash('Failed to generate evidence analysis. Please try again.', 'danger')
                    
            except Exception as e:
                app.logger.error(f"Error in evidence relevance analysis: {str(e)}")
                flash('An error occurred during analysis. Please try again later.', 'danger')
                
        # Exhibit Organization
        elif analysis_type == 'exhibit_organization':
            if not relevance_analysis:
                flash('Please generate evidence relevance analysis first.', 'warning')
                return redirect(url_for('evidence_ai.evidence_analysis', case_id=case_id))
                
            try:
                # Perform the AI analysis
                ai_result = organize_exhibits(
                    case_id, 
                    description, 
                    issue_type, 
                    court_type, 
                    relevance_analysis
                )
                
                if ai_result:
                    # Save or update the analysis in the database
                    if exhibit_org:
                        exhibit_org.content = json.dumps(ai_result)
                        db.session.commit()
                    else:
                        LegalAnalysis.create_analysis(
                            case_id=case_id,
                            analysis_type='exhibit_organization',
                            content=json.dumps(ai_result)
                        )
                    
                    flash('Exhibit organization plan generated successfully.', 'success')
                    return redirect(url_for('evidence_ai.evidence_analysis', case_id=case_id))
                else:
                    flash('Failed to generate exhibit organization. Please try again.', 'danger')
                    
            except Exception as e:
                app.logger.error(f"Error in exhibit organization: {str(e)}")
                flash('An error occurred during analysis. Please try again later.', 'danger')
    
    # Check if Anthropic is configured
    anthropic_configured = anthropic_helper.is_available()
    
    # Render the evidence analysis template
    return render_template(
        'evidence_analysis.html',
        case=case,
        evidence_items=evidence_items,
        relevance_analysis=relevance_analysis,
        exhibit_organization=exhibit_organization,
        has_relevance_analysis=evidence_relevance is not None,
        has_exhibit_organization=exhibit_org is not None,
        anthropic_configured=anthropic_configured
    )

def analyze_evidence_relevance(case_id, description, issue_type, court_type, evidence_descriptions):
    """
    Analyze evidence for suppression under "fruit of the poisonous tree" doctrine.
    Uses AI to identify evidence that can be challenged and thrown out.
    """
    try:
        # Check which AI provider to use
        if anthropic_helper.is_available():
            # Try Anthropic first if available
            result = anthropic_helper.analyze_evidence_relevance(
                description, 
                issue_type, 
                court_type, 
                evidence_descriptions
            )
            if result:
                return result
        
        # Fall back to OpenAI
        # Prepare the prompt for OpenAI
        prompt = f"""You are an expert evidence suppression specialist helping individuals identify "fruit of the poisonous tree" opportunities.
        Your goal is to find every possible piece of evidence that could be suppressed because it stems from an initial 
        illegal search, seizure, or other constitutional violation.
        
        CASE DETAILS:
        Description: {description}
        Issue Type: {issue_type}
        Court Type: {court_type}
        
        EVIDENCE ITEMS:
        {json.dumps(evidence_descriptions, indent=2)}
        
        For each piece of evidence, determine:
        1. Is it a "poisonous tree" itself (direct constitutional violation)?
        2. Is it "fruit" (evidence derived from an initial violation)?
        3. Which Supreme Court cases support suppression?
        4. What exact language to use in a suppression motion that anyone could file?
        5. How suppressing this evidence impacts other evidence in the case?
        
        Format your response as a JSON object structured like this:
        {{
          "evidence_analysis": [
            {{
              "evidence_id": 1,
              "suppressible": "High/Medium/Low chance",
              "suppression_basis": "The Fourth Amendment violation that makes this evidence illegal",
              "case_precedents": ["Mapp v. Ohio", "Wong Sun v. United States"],
              "suppression_motion_language": "Exact language to use in motion",
              "connected_evidence": [2, 3],
              "strategic_value": "How important suppressing this is to the case"
            }},
            ...additional evidence analyses...
          ]
        }}
        
        Provide detailed, legally sound analysis for each piece of evidence that could help strengthen the case.
        """
        
        # Call OpenAI API
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        MODEL = "gpt-4o"  # The newest OpenAI model
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a justice-focused legal evidence analyst helping individuals fight unfairness in courts. Provide detailed, strategic analysis of legal evidence with accurate, well-structured JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
            return result
        else:
            logging.error("Empty response from OpenAI")
            return None
            
    except Exception as e:
        logging.error(f"Error in analyze_evidence_relevance: {str(e)}")
        return None

def organize_exhibits(case_id, description, issue_type, court_type, relevance_analysis):
    """
    Organize evidence into logical exhibit groups for court presentation.
    Uses AI to create an organized exhibit plan.
    """
    try:
        # Check which AI provider to use
        if anthropic_helper.is_available():
            # Try Anthropic first if available
            result = anthropic_helper.organize_exhibits(
                description, 
                issue_type, 
                court_type, 
                relevance_analysis
            )
            if result:
                return result
        
        # Fall back to OpenAI
        # Prepare the prompt for OpenAI
        prompt = f"""You are an expert legal strategist tasked with organizing evidence into effective exhibits for a legal case.
        
        CASE DETAILS:
        Description: {description}
        Issue Type: {issue_type}
        Court Type: {court_type}
        
        EVIDENCE RELEVANCE ANALYSIS:
        {json.dumps(relevance_analysis, indent=2)}
        
        Based on the relevance analysis of each piece of evidence, create a strategic organization plan that:
        1. Groups related evidence into logical exhibit categories
        2. Arranges exhibits in the most compelling order for presentation
        3. Suggests effective labeling for each exhibit
        4. Explains the strategic purpose of each exhibit group
        5. Provides guidance on how to introduce and use each exhibit for maximum impact
        
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
        
        # Call OpenAI API
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        MODEL = "gpt-4o"  # The newest OpenAI model
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a justice-focused legal strategist helping individuals fight unfairness in courts. Provide strategic exhibit organization with accurate, well-structured JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
            return result
        else:
            logging.error("Empty response from OpenAI")
            return None
            
    except Exception as e:
        logging.error(f"Error in organize_exhibits: {str(e)}")
        return None