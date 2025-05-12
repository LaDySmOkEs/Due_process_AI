"""
Case Timeline module for tracking events, deadlines, and identifying
procedural violations including speedy trial rights.
"""
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Case, LegalAnalysis, db
from app import db

# Create blueprint
timeline = Blueprint('timeline', __name__)

@timeline.route('/case/<int:case_id>/timeline')
@login_required
def case_timeline(case_id):
    """Display interactive timeline for a specific case"""
    case = Case.get_case_by_id(case_id)
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Get existing timeline data if available
    timeline_analysis = LegalAnalysis.get_by_case_and_type(case_id, 'timeline_events')
    timeline_data = {}
    
    if timeline_analysis and timeline_analysis.references:
        try:
            timeline_data = json.loads(timeline_analysis.references)
        except json.JSONDecodeError:
            timeline_data = {}
    
    # If no timeline data exists, create default structure with example events
    if not timeline_data or not timeline_data.get('events'):
        timeline_data = {
            'courtType': case.court_type,
            'issueType': case.issue_type,
            'events': []
        }
    
    return render_template(
        'case_timeline.html',
        case=case,
        timeline_data=json.dumps(timeline_data)
    )

@timeline.route('/case/<int:case_id>/timeline/add-event', methods=['POST'])
@login_required
def add_timeline_event(case_id):
    """Add a new event to the case timeline"""
    case = Case.get_case_by_id(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        return jsonify({'error': 'Permission denied'}), 403
    
    # Get event data from form
    try:
        event_title = request.form.get('title')
        event_date = request.form.get('date')
        event_type = request.form.get('type', 'regular')
        event_description = request.form.get('description', '')
        
        if not event_title or not event_date:
            return jsonify({'error': 'Event title and date are required'}), 400
        
        # Parse date
        try:
            # Validate date format
            datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get existing timeline data
        timeline_analysis = LegalAnalysis.get_by_case_and_type(case_id, 'timeline_events')
        timeline_data = {}
        
        if timeline_analysis and timeline_analysis.references:
            try:
                timeline_data = json.loads(timeline_analysis.references)
            except json.JSONDecodeError:
                timeline_data = {
                    'courtType': case.court_type,
                    'issueType': case.issue_type,
                    'events': []
                }
        else:
            timeline_data = {
                'courtType': case.court_type,
                'issueType': case.issue_type,
                'events': []
            }
        
        # Add new event
        new_event = {
            'id': len(timeline_data.get('events', [])) + 1,
            'title': event_title,
            'date': event_date,
            'type': event_type,
            'description': event_description
        }
        
        # Auto-detect potential violations
        if event_type == 'arrest' or 'arrest' in event_title.lower():
            if case.issue_type == 'criminal':
                new_event['description'] += " (Starting date for speedy trial rights)"
        
        # Add to events list
        if 'events' not in timeline_data:
            timeline_data['events'] = []
            
        timeline_data['events'].append(new_event)
        
        # Save updated timeline data
        if timeline_analysis:
            timeline_analysis.references = json.dumps(timeline_data)
            db.session.commit()
        else:
            # Create new analysis record
            LegalAnalysis.create_analysis(
                case_id=case_id,
                analysis_type='timeline_events',
                content="Case Timeline Events",
                references=json.dumps(timeline_data),
                confidence_score=1.0
            )
        
        return jsonify({
            'success': True,
            'event': new_event,
            'timeline_data': timeline_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timeline.route('/case/<int:case_id>/timeline/events', methods=['GET'])
@login_required
def get_timeline_events(case_id):
    """Get all timeline events for a case"""
    case = Case.get_case_by_id(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        return jsonify({'error': 'Permission denied'}), 403
    
    # Get timeline data
    timeline_analysis = LegalAnalysis.get_by_case_and_type(case_id, 'timeline_events')
    
    if timeline_analysis and timeline_analysis.references:
        try:
            timeline_data = json.loads(timeline_analysis.references)
            return jsonify(timeline_data)
        except json.JSONDecodeError:
            return jsonify({'events': []})
    
    return jsonify({'events': []})

@timeline.route('/case/<int:case_id>/timeline/delete-event/<int:event_id>', methods=['POST'])
@login_required
def delete_timeline_event(case_id, event_id):
    """Delete an event from the case timeline"""
    case = Case.get_case_by_id(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        return jsonify({'error': 'Permission denied'}), 403
    
    # Get timeline data
    timeline_analysis = LegalAnalysis.get_by_case_and_type(case_id, 'timeline_events')
    
    if not timeline_analysis or not timeline_analysis.references:
        return jsonify({'error': 'Timeline not found'}), 404
    
    try:
        timeline_data = json.loads(timeline_analysis.references)
        
        # Remove event
        timeline_data['events'] = [e for e in timeline_data.get('events', []) if e.get('id') != event_id]
        
        # Save updated timeline data
        timeline_analysis.references = json.dumps(timeline_data)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timeline.route('/case/<int:case_id>/save-timeline-analysis', methods=['POST'])
@login_required
def save_timeline_analysis(case_id):
    """Save speedy trial analysis to the case"""
    case = Case.get_case_by_id(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        analysis_content = request.form.get('analysis')
        if not analysis_content:
            return jsonify({'error': 'Analysis content is required'}), 400
        
        # Get existing analysis or create new
        speedy_trial_analysis = LegalAnalysis.get_by_case_and_type(case_id, 'speedy_trial_analysis')
        
        if speedy_trial_analysis:
            speedy_trial_analysis.content = analysis_content
            db.session.commit()
        else:
            LegalAnalysis.create_analysis(
                case_id=case_id,
                analysis_type='speedy_trial_analysis',
                content=analysis_content,
                references=json.dumps({'analysisDate': datetime.now().isoformat()}),
                confidence_score=0.9
            )
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500