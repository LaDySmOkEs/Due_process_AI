"""
Client interview questions module for identifying potential rights violations and defense opportunities.
These questions are designed to help clients identify systemic issues and constitutional violations
that can be used to challenge evidence and potentially win their case.
"""

import json
import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Case, User, LegalAnalysis, db
import anthropic_helper
from openai import OpenAI

# Create blueprint
client_interview = Blueprint('client_interview', __name__)

# Constants
INTERVIEW_QUESTIONS = {
    "initial_contact": [
        {
            "question": "Did law enforcement tell you why they stopped, detained, or arrested you?",
            "follow_up": "If yes, what reason did they give? If no, this could be a Fourth Amendment violation."
        },
        {
            "question": "Were you shown a warrant before any search of your person, vehicle, or property?",
            "follow_up": "If no, did they claim any exception like 'plain view' or 'emergency'?"
        },
        {
            "question": "Were you read your Miranda rights before questioning?",
            "follow_up": "If no, any statements made may be suppressible."
        }
    ],
    "search_and_seizure": [
        {
            "question": "Where were you when officers first approached you? (public place, private home, vehicle, etc.)",
            "follow_up": "Different locations have different Fourth Amendment protections."
        },
        {
            "question": "Did officers search beyond the area they had permission or authority to search?",
            "follow_up": "Describe any areas they searched that weren't included in a warrant or consent."
        },
        {
            "question": "Did officers take any evidence from anywhere other than where they initially searched?",
            "follow_up": "This could be 'fruit of the poisonous tree' if the initial search was illegal."
        },
        {
            "question": "Were any searches conducted without your consent or a warrant?",
            "follow_up": "If yes, exactly what was searched and what was found?"
        }
    ],
    "timeline_questions": [
        {
            "question": "What date were you arrested or charged?",
            "follow_up": "This establishes when your speedy trial clock started."
        },
        {
            "question": "How many days passed between arrest and first court appearance?",
            "follow_up": "Delays here could violate state speedy appearance laws."
        },
        {
            "question": "Have there been any continuances or delays in your case?",
            "follow_up": "Who requested them? The prosecution's delays count against speedy trial rights."
        },
        {
            "question": "How long have you been waiting for trial?",
            "follow_up": "Different jurisdictions have different speedy trial timelines, typically 60-180 days."
        }
    ],
    "evidence_questions": [
        {
            "question": "Was any evidence obtained after you requested a lawyer?",
            "follow_up": "Any questioning after requesting counsel violates your rights."
        },
        {
            "question": "Did officers claim to have evidence they didn't show you?",
            "follow_up": "This could indicate fabricated probable cause."
        },
        {
            "question": "Was any evidence obtained through electronic surveillance?",
            "follow_up": "Was there a warrant specifically for this surveillance?"
        },
        {
            "question": "Were any witnesses pressured or coerced into giving statements?",
            "follow_up": "This could make their testimony fruit of the poisonous tree."
        }
    ],
    "system_bias_questions": [
        {
            "question": "Was your public defender provided by the same government entity that pays the prosecutors and judge?",
            "follow_up": "This inherent conflict of interest may justify self-representation with our tools."
        },
        {
            "question": "Has your public defender suggested you take a plea deal without investigating suppression issues?",
            "follow_up": "This could indicate the conflict of interest at work."
        },
        {
            "question": "Have you been given full access to all evidence against you?",
            "follow_up": "Brady violations (withholding exculpatory evidence) are grounds for dismissal."
        },
        {
            "question": "Have you been treated differently because of race, gender, economic status, or other characteristics?",
            "follow_up": "Equal protection violations may exist."
        }
    ]
}

@client_interview.route('/case/<int:case_id>/interview', methods=['GET', 'POST'])
@login_required
def case_interview(case_id):
    """Display and process client interview questions"""
    # Get case details
    case = Case.query.get_or_404(case_id)
    
    # Security check - make sure the current user owns this case
    if case.user_id != current_user.id:
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check for existing interview answers
    interview_results = LegalAnalysis.query.filter_by(
        case_id=case_id, 
        analysis_type='interview_results'
    ).first()
    
    # Initialize answers dict
    answers = {}
    
    # Load existing answers if available
    if interview_results:
        try:
            answers = json.loads(interview_results.content)
        except:
            logging.error("Failed to parse interview results JSON")
    
    # Handle POST request - Save interview answers
    if request.method == 'POST':
        # Process form submission to save answers
        new_answers = {}
        
        # Process each question category
        for category in INTERVIEW_QUESTIONS:
            category_answers = []
            for i, _ in enumerate(INTERVIEW_QUESTIONS[category]):
                question_key = f"{category}_{i}"
                answer = request.form.get(question_key, "")
                category_answers.append(answer)
            new_answers[category] = category_answers
        
        # Save answers to database
        if interview_results:
            interview_results.content = json.dumps(new_answers)
            db.session.commit()
        else:
            LegalAnalysis.create_analysis(
                case_id=case_id,
                analysis_type='interview_results',
                content=json.dumps(new_answers)
            )
        
        # Generate rights violation analysis if requested
        if 'analyze_answers' in request.form:
            return redirect(url_for('client_interview.analyze_interview', case_id=case_id))
        
        flash('Your answers have been saved.', 'success')
        return redirect(url_for('client_interview.case_interview', case_id=case_id))
    
    # Render the interview template
    return render_template(
        'client_interview.html',
        case=case,
        questions=INTERVIEW_QUESTIONS,
        answers=answers
    )

@client_interview.route('/case/<int:case_id>/interview/analyze', methods=['GET'])
@login_required
def analyze_interview(case_id):
    """Analyze interview answers to identify rights violations and defense strategies"""
    # Get case details
    case = Case.query.get_or_404(case_id)
    
    # Security check - make sure the current user owns this case
    if case.user_id != current_user.id:
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check for existing interview answers
    interview_results = LegalAnalysis.query.filter_by(
        case_id=case_id, 
        analysis_type='interview_results'
    ).first()
    
    if not interview_results:
        flash('Please complete the interview before requesting analysis.', 'warning')
        return redirect(url_for('client_interview.case_interview', case_id=case_id))
    
    try:
        # Load interview answers
        answers = json.loads(interview_results.content)
        
        # Check for existing analysis
        analysis = LegalAnalysis.query.filter_by(
            case_id=case_id, 
            analysis_type='interview_analysis'
        ).first()
        
        # Perform new analysis if needed
        if not analysis:
            # Generate new analysis
            analysis_result = generate_interview_analysis(case, answers)
            
            if analysis_result:
                # Create new analysis record
                LegalAnalysis.create_analysis(
                    case_id=case_id,
                    analysis_type='interview_analysis',
                    content=json.dumps(analysis_result)
                )
                flash('Interview analysis has been generated successfully.', 'success')
            else:
                flash('Failed to generate analysis. Please try again.', 'danger')
        
        # Redirect to view the analysis
        return redirect(url_for('client_interview.view_analysis', case_id=case_id))
        
    except Exception as e:
        flash(f'Error analyzing interview answers: {str(e)}', 'danger')
        return redirect(url_for('client_interview.case_interview', case_id=case_id))

@client_interview.route('/case/<int:case_id>/interview/analysis', methods=['GET'])
@login_required
def view_analysis(case_id):
    """View the analysis of interview answers"""
    # Get case details
    case = Case.query.get_or_404(case_id)
    
    # Security check - make sure the current user owns this case
    if case.user_id != current_user.id:
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check for existing analysis
    analysis = LegalAnalysis.query.filter_by(
        case_id=case_id, 
        analysis_type='interview_analysis'
    ).first()
    
    if not analysis:
        flash('No analysis found. Please complete the interview and generate an analysis.', 'warning')
        return redirect(url_for('client_interview.case_interview', case_id=case_id))
    
    try:
        # Load analysis results
        analysis_result = json.loads(analysis.content)
        
        # Render the analysis template
        return render_template(
            'interview_analysis.html',
            case=case,
            analysis=analysis_result
        )
        
    except Exception as e:
        flash(f'Error loading analysis: {str(e)}', 'danger')
        return redirect(url_for('client_interview.case_interview', case_id=case_id))

def generate_interview_analysis(case, answers):
    """Generate analysis of interview answers using AI"""
    try:
        # Try Anthropic first if available
        if anthropic_helper.is_available():
            prompt = create_analysis_prompt(case, answers)
            result = anthropic_helper.analyze_case_text(prompt, json_format=True)
            if result:
                return result
        
        # Fall back to OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"error": "No AI provider available"}
        
        # Prepare the prompt
        prompt = create_analysis_prompt(case, answers)
        
        # Call OpenAI API
        client = OpenAI(api_key=api_key)
        MODEL = "gpt-4o"  # The newest OpenAI model
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert legal analyst identifying constitutional violations, fruit of the poisonous tree evidence, and speedy trial violations based on client interview answers. Provide detailed, strategic analysis with accurate, well-structured JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content
        if content:
            return json.loads(content)
        else:
            return {"error": "Empty response from AI provider"}
            
    except Exception as e:
        return {"error": f"Analysis generation failed: {str(e)}"}

def create_analysis_prompt(case, answers):
    """Create prompt for AI analysis of interview answers"""
    # Format answers for the prompt
    formatted_answers = ""
    
    for category, category_answers in answers.items():
        formatted_answers += f"\n{category.upper()} QUESTIONS:\n"
        
        for i, answer in enumerate(category_answers):
            if i < len(INTERVIEW_QUESTIONS.get(category, [])):
                question = INTERVIEW_QUESTIONS[category][i]["question"]
                formatted_answers += f"Q: {question}\nA: {answer}\n"
    
    # Create the analysis prompt
    prompt = f"""
    You are an expert legal analyst helping identify constitutional violations, evidence suppression opportunities,
    and speedy trial violations based on a client interview. The client may have been subjected to rights violations
    that they're not aware of, particularly in a system where public defenders are paid by the same entity as
    prosecutors and judges.
    
    CASE DETAILS:
    Title: {case.title}
    Issue Type: {case.issue_type}
    Court Type: {case.court_type}
    Description: {case.description}
    
    CLIENT INTERVIEW ANSWERS:
    {formatted_answers}
    
    Based on these answers, identify:
    1. Any Fourth Amendment violations that could lead to evidence suppression
    2. Any "fruit of the poisonous tree" evidence that stems from initial constitutional violations
    3. Any speedy trial rights violations based on timeline information
    4. Any systemic bias or conflict of interest issues in the legal representation
    5. Specific motions the client should file to assert these rights
    6. Supreme Court cases that support suppression or dismissal based on these violations
    
    Format your response as a JSON object with these sections:
    {{
      "constitutional_violations": [
        {{
          "violation_type": "Fourth Amendment - Illegal Search",
          "description": "Based on answers about the search, there appears to be a warrantless search without exception",
          "supporting_case_law": ["Case v. Example", "Another v. Case"],
          "recommended_action": "File Motion to Suppress all evidence obtained from the search",
          "suppressible_evidence": ["Evidence items 1, 2 that should be suppressed"],
          "motion_language": "Exact language to use in the suppression motion",
          "probability_of_success": "High/Medium/Low"
        }}
      ],
      "speedy_trial_violations": [
        {{
          "violation_description": "Based on timeline answers, 180+ days have passed without trial",
          "jurisdiction_rule": "This jurisdiction requires trial within 90 days",
          "supporting_case_law": ["Relevant speedy trial cases"],
          "recommended_action": "File Motion to Dismiss for speedy trial violation",
          "motion_language": "Exact language to use in the dismissal motion",
          "probability_of_success": "High/Medium/Low"
        }}
      ],
      "fruit_of_poisonous_tree": [
        {{
          "initial_violation": "The original constitutional violation",
          "tainted_evidence": ["Evidence that stems from the initial violation"],
          "suppression_argument": "Why this evidence should be suppressed as fruit",
          "supporting_case_law": ["Wong Sun v. United States", "Other relevant cases"],
          "motion_language": "Exact language to use in the suppression motion"
        }}
      ],
      "systemic_bias_issues": [
        {{
          "bias_type": "Conflict of interest in legal representation",
          "description": "Public defender paid by same entity as prosecutor",
          "legal_basis": "Constitutional right to effective counsel",
          "recommended_action": "File motion asserting conflict and requesting independent counsel"
        }}
      ],
      "defense_strategy": {{
        "primary_approach": "Focus on suppressing evidence through Fourth Amendment challenge",
        "secondary_approach": "Simultaneously pursue speedy trial dismissal",
        "key_motions": ["Motion to Suppress", "Motion to Dismiss"],
        "filing_priority": "File suppression motion first, then immediately file speedy trial motion",
        "overall_assessment": "Assessment of case strength after applying these strategies"
      }}
    }}
    
    Provide detailed, legally sound analysis that will help the client navigate the legal system without relying on potentially compromised public defenders.
    """
    
    return prompt