"""
Court script generator for self-represented litigants.
Generates step-by-step court appearance scripts based on case details,
rights violations, and evidence suppression opportunities.
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Case, User, LegalAnalysis, db
import anthropic_helper
from openai import OpenAI

# Create blueprint
court_script = Blueprint('court_script', __name__)

@court_script.route('/case/<int:case_id>/court-script', methods=['GET', 'POST'])
@login_required
def generate_script(case_id):
    """Generate or view court script for a specific case"""
    # Get case details
    case = Case.query.get_or_404(case_id)
    
    # Security check - make sure the current user owns this case
    if case.user_id != current_user.id:
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check for rights violation interview analysis
    interview_analysis = LegalAnalysis.query.filter_by(
        case_id=case_id, 
        analysis_type='interview_analysis'
    ).first()
    
    has_interview_analysis = (interview_analysis is not None)
    script = None
    selected_proceeding = None
    
    # Check for existing court script
    court_script_analysis = LegalAnalysis.query.filter_by(
        case_id=case_id, 
        analysis_type='court_script'
    ).first()
    
    # Process form submission for generating new script
    if request.method == 'POST':
        proceeding_type = request.form.get('proceeding_type')
        additional_context = request.form.get('additional_context', '')
        selected_proceeding = proceeding_type
        
        try:
            # Load interview analysis if available
            interview_data = None
            if interview_analysis:
                try:
                    interview_data = json.loads(interview_analysis.content)
                except:
                    logging.error("Failed to parse interview analysis JSON")
            
            # Generate the court script
            script_content = create_court_script(
                case=case,
                proceeding_type=proceeding_type,
                interview_analysis=interview_data,
                additional_context=additional_context
            )
            
            if script_content:
                # Store or update the script
                if court_script_analysis:
                    court_script_analysis.content = json.dumps(script_content)
                    court_script_analysis.references = json.dumps({"proceeding_type": proceeding_type})
                    db.session.commit()
                else:
                    court_script_analysis = LegalAnalysis.create_analysis(
                        case_id=case_id,
                        analysis_type='court_script',
                        content=json.dumps(script_content),
                        references=json.dumps({"proceeding_type": proceeding_type})
                    )
                
                script = script_content
                flash('Court appearance script generated successfully!', 'success')
            else:
                flash('Failed to generate court script. Please try again.', 'danger')
                
        except Exception as e:
            logging.error(f"Error generating court script: {str(e)}")
            flash(f'Error generating script: {str(e)}', 'danger')
    
    # Display existing script if available
    elif court_script_analysis:
        try:
            script = json.loads(court_script_analysis.content)
            script_info = json.loads(court_script_analysis.references)
            selected_proceeding = script_info.get('proceeding_type')
        except:
            logging.error("Failed to parse existing court script JSON")
            flash('Error loading the saved court script.', 'warning')
    
    return render_template(
        'court_script.html',
        case=case,
        script=script,
        has_interview_analysis=has_interview_analysis,
        selected_proceeding=selected_proceeding
    )

def create_court_script(case, proceeding_type, interview_analysis=None, additional_context=''):
    """Generate a court script based on case details and analysis"""
    try:
        # Try Anthropic first if available
        if anthropic_helper.is_available():
            prompt = create_script_prompt(case, proceeding_type, interview_analysis, additional_context)
            result = anthropic_helper.analyze_case_text(prompt, json_format=True)
            if result:
                return result
        
        # Fall back to OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        
        # Prepare the prompt
        prompt = create_script_prompt(case, proceeding_type, interview_analysis, additional_context)
        
        # Call OpenAI API
        client = OpenAI(api_key=api_key)
        MODEL = "gpt-4o"  # The newest OpenAI model
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert legal strategist developing detailed court appearance scripts for self-represented litigants. Create comprehensive, step-by-step guidance for court proceedings with detailed instructions on what to do, what to say, when to say it, and how to assert constitutional rights effectively. Focus on challenging probable cause AND asserting speedy trial rights when applicable."},
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
            return None
            
    except Exception as e:
        logging.error(f"Court script generation failed: {str(e)}")
        return None

def create_script_prompt(case, proceeding_type, analysis_data, additional_context):
    """Create prompt for generating court script"""
    # Get proceeding-specific guidance to include in the prompt
    proceeding_guidance = get_proceeding_guidance(proceeding_type)
    
    # Format any constitutional violations from the interview analysis
    violations_text = ""
    if analysis_data and isinstance(analysis_data, dict):
        # Format constitutional violations
        if "constitutional_violations" in analysis_data and analysis_data["constitutional_violations"]:
            violations_text += "\nCONSTITUTIONAL VIOLATIONS IDENTIFIED:\n"
            for violation in analysis_data["constitutional_violations"]:
                violations_text += f"- {violation.get('violation_type', 'Unknown violation')}: {violation.get('description', '')}\n"
                violations_text += f"  Supporting case law: {', '.join(violation.get('supporting_case_law', ['']))}\n"
        
        # Format speedy trial violations
        if "speedy_trial_violations" in analysis_data and analysis_data["speedy_trial_violations"]:
            violations_text += "\nSPEEDY TRIAL VIOLATIONS IDENTIFIED:\n"
            for violation in analysis_data["speedy_trial_violations"]:
                violations_text += f"- {violation.get('violation_description', 'Unknown violation')}\n"
                violations_text += f"  Jurisdiction rule: {violation.get('jurisdiction_rule', '')}\n"
                violations_text += f"  Supporting case law: {', '.join(violation.get('supporting_case_law', ['']))}\n"
        
        # Format fruit of the poisonous tree evidence
        if "fruit_of_poisonous_tree" in analysis_data and analysis_data["fruit_of_poisonous_tree"]:
            violations_text += "\nFRUIT OF THE POISONOUS TREE EVIDENCE IDENTIFIED:\n"
            for evidence in analysis_data["fruit_of_poisonous_tree"]:
                violations_text += f"- Initial violation: {evidence.get('initial_violation', '')}\n"
                violations_text += f"  Tainted evidence: {', '.join(evidence.get('tainted_evidence', ['']))}\n"
    
    # Create the full prompt
    prompt = f"""
    Create a comprehensive, step-by-step court appearance script for a self-represented litigant appearing at a {proceeding_type.replace('_', ' ')} proceeding.
    
    CASE DETAILS:
    Title: {case.title}
    Court Type: {case.court_type}
    Issue Type: {case.issue_type}
    Description: {case.description}
    
    {violations_text}
    
    ADDITIONAL CONTEXT FROM LITIGANT:
    {additional_context if additional_context else "No additional context provided."}
    
    PROCEEDING-SPECIFIC GUIDANCE:
    {proceeding_guidance}
    
    Create a detailed court script that includes:
    1. Preparation before court (documents to bring, how to dress, what to prepare)
    2. Entering the courtroom (where to sit, how to address the court)
    3. Main proceeding (with each stage broken down into what to expect, what to say, what to do)
    4. How to assert constitutional rights and challenge evidence effectively
    5. How to handle potential challenges or pushback
    6. How to conclude the proceeding professionally
    
    Format your response as a JSON object with these sections:
    {{
      "script_title": "Court Appearance Script: [PROCEEDING TYPE]",
      "preparation": [
        {{
          "step": "Gather essential documents",
          "details": "Specific documents to bring and how to organize them",
          "importance": "Explanation of why this preparation step matters"
        }}
      ],
      "courtroom_entrance": [
        {{
          "action": "Specific action to take when entering",
          "explanation": "Explanation of why this matters"
        }}
      ],
      "main_proceeding": [
        {{
          "stage": "Name of this stage of the proceeding",
          "what_to_expect": "Detailed explanation of what will happen",
          "what_to_say": "Exact script of what to say, including formal language",
          "what_to_do": "Physical actions to take during this stage",
          "tips": "Strategic advice for this stage"
        }}
      ],
      "asserting_rights": [
        {{
          "right": "Specific right to assert",
          "when_to_assert": "Timing of when to bring this up",
          "what_to_say": "Exact wording to use when asserting this right",
          "possible_responses": "How the court might respond and how to handle it"
        }}
      ],
      "potential_challenges": [
        {{
          "challenge": "Potential obstacle that might arise",
          "how_to_handle": "Step-by-step approach to addressing this challenge",
          "fallback_strategy": "What to do if the primary approach fails"
        }}
      ],
      "conclusion": [
        {{
          "action": "Actions to take at conclusion",
          "what_to_say": "Final statements if applicable",
          "next_steps": "What to do immediately after the proceeding"
        }}
      ]
    }}
    
    Ensure the script is specific to a {proceeding_type.replace('_', ' ')} proceeding, addresses the identified constitutional violations (if any), and provides clear, actionable guidance that a non-lawyer can follow in court.
    """
    
    return prompt

def get_proceeding_guidance(proceeding_type):
    """Get guidance specific to the type of court proceeding"""
    guidance = {
        'arraignment': """
        An arraignment is your first formal court appearance where charges are read, and you enter a plea.
        
        KEY STRATEGIC CONSIDERATIONS:
        - This is typically NOT the time to argue your case but to understand charges and enter a plea
        - Pleading "not guilty" preserves all your rights and gives you time to build a defense
        - Listen carefully to the charges and ask for clarification if needed
        - Request discovery (evidence against you) at this stage
        - Assert your right to a speedy trial clearly and on the record
        - Take note of any deadlines mentioned by the judge
        """,
        
        'bail_hearing': """
        A bail hearing determines if you will be released pending trial and under what conditions.
        
        KEY STRATEGIC CONSIDERATIONS:
        - Focus on factors that show you're not a flight risk or danger to community
        - Highlight community ties, employment, family responsibilities, lack of criminal history
        - Be prepared to suggest alternative conditions to detention (ankle monitoring, check-ins)
        - Have a clear release plan to present (where you'll stay, how you'll support yourself)
        - If bail is set too high, argue for reduction based on financial circumstances
        - Request a bail source hearing if needed to verify legitimacy of bail funds
        """,
        
        'preliminary_hearing': """
        A preliminary hearing is where the prosecution must show probable cause that you committed the crime.
        
        KEY STRATEGIC CONSIDERATIONS:
        - This is a critical opportunity to challenge probable cause
        - Look for inconsistencies in witness testimony
        - Question whether evidence actually meets each element of the charged crime
        - Take detailed notes on testimony for later use in trial
        - The standard is low ("probable cause" not "beyond reasonable doubt")
        - You can often learn details about the prosecution's case
        - Challenge hearsay evidence that doesn't fall under exceptions
        """,
        
        'motion_hearing': """
        A motion hearing is where specific requests (motions) are argued before the judge.
        
        KEY STRATEGIC CONSIDERATIONS:
        - Be extremely prepared regarding the legal basis for your motion
        - Have relevant case law ready to cite (with copies for the judge)
        - Focus arguments on constitutional violations, not factual innocence
        - Be concise, organized, and respectful
        - Anticipate counter-arguments and be ready to respond
        - For suppression: focus on warrant defects, lack of probable cause, or unreasonable search
        - For dismissal: focus on speedy trial violations or failure to state a claim
        """,
        
        'suppression_hearing': """
        A suppression hearing specifically addresses whether evidence should be excluded due to constitutional violations.
        
        KEY STRATEGIC CONSIDERATIONS:
        - Challenge the initial basis for the stop/search/seizure
        - Question whether warrant (if any) was properly obtained and executed
        - Highlight how the evidence in question stems from the initial violation ("fruit of poisonous tree")
        - Be prepared to question officers about their actions and reasoning
        - Know the specific exceptions to warrant requirements and why they don't apply
        - Use timeline inconsistencies to challenge officer credibility
        - Show how the allegedly unconstitutional actions affected the evidence collection
        """,
        
        'trial': """
        A trial is where the facts are presented to a judge or jury to determine guilt or innocence.
        
        KEY STRATEGIC CONSIDERATIONS:
        - Opening statement should be simple, clear, and tell your narrative
        - Questions to witnesses should be concise and have a strategic purpose
        - Object to improper evidence promptly with specific legal grounds
        - Know rules of evidence, especially hearsay exceptions
        - Preserve issues for appeal by making clear objections
        - Focus on elements of crime prosecution must prove
        - Closing argument should highlight reasonable doubt
        - Consider requesting specific jury instructions
        """,
        
        'sentencing': """
        A sentencing hearing is where the judge determines punishment after a guilty plea or verdict.
        
        KEY STRATEGIC CONSIDERATIONS:
        - Focus on mitigating factors (personal circumstances, remorse, rehabilitation)
        - Prepare a specific sentencing proposal with alternatives to incarceration
        - Bring supporting character witnesses or letters
        - Address victim impact while showing understanding and remorse
        - Highlight positive steps taken since charges (treatment, education, employment)
        - Be prepared to address the statutory sentencing factors
        - Consider having a sentencing memorandum prepared in advance
        """
    }
    
    return guidance.get(proceeding_type, "No specific guidance available for this proceeding type.")