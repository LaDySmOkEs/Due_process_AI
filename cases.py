import os
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Case, Evidence, db
from forms import CaseForm, EvidenceForm
from utils import allowed_file, get_file_type

cases = Blueprint('cases', __name__)

@cases.route('/dashboard')
@login_required
def dashboard():
    user_cases = Case.get_cases_by_user(current_user.id)
    return render_template('dashboard.html', cases=user_cases)

@cases.route('/case/new', methods=['GET', 'POST'])
@login_required
def new_case():
    form = CaseForm()
    if form.validate_on_submit():
        case = Case.create_case(
            user_id=current_user.id,
            title=form.title.data,
            court_type=form.court_type.data,
            issue_type=form.issue_type.data,
            description=form.description.data
        )
        flash(f'Your case "{form.title.data}" has been created!', 'success')
        return redirect(url_for('cases.case_summary', case_id=case.id))
    
    return render_template('new_case.html', form=form)

@cases.route('/case/<int:case_id>')
@login_required
def case_summary(case_id):
    case = Case.get_case_by_id(case_id)
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    if case.user_id != current_user.id and not current_user.is_moderator() and not current_user.is_legal_assistant():
        flash('You do not have permission to view this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    evidence_list = case.get_evidence()
    return render_template('case_summary.html', case=case, evidence=evidence_list)

@cases.route('/case/<int:case_id>/evidence/upload', methods=['GET', 'POST'])
@login_required
def upload_evidence(case_id):
    # Get the case and create the form outside the try block
    case = Case.get_case_by_id(case_id)
    if not case:
        flash('Case not found.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    if case.user_id != current_user.id and not current_user.is_legal_assistant():
        flash('You do not have permission to add evidence to this case.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    form = EvidenceForm()
    
    # Handle form submission
    if request.method == 'POST':
        try:
            # Try to validate the form
            if not form.validate():
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error in {field}: {error}", 'danger')
                return render_template('upload_evidence.html', form=form, case=case)
            
            print(f"Evidence form submitted with data: {form.data}")  # Debug logging
            
            # Handle two types of evidence: file uploads and social media/external links
            if form.evidence_type.data == 'file':
                file = form.file.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp or random string to ensure uniqueness
                    unique_filename = f"{case_id}_{current_user.id}_{filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    
                    print(f"Uploading file: {filename} as {unique_filename}")  # Debug logging
                    
                    # Get file type for processing
                    file_type = get_file_type(filename)
                    
                    # Create evidence record
                    evidence = Evidence.create_evidence(
                        case_id=case_id,
                        filename=unique_filename,
                        original_filename=filename,
                        description=form.description.data,
                        file_type=file_type
                    )
                    
                    # Check if it's an audio or video file that needs transcription
                    if file_type in ['audio', 'video']:
                        # Import audio processor here to avoid circular imports
                        from audio_processor import transcribe_audio, analyze_transcript
                        
                        # Schedule transcription in background
                        evidence.transcript_status = 'pending'
                        evidence.analysis_status = 'pending'
                        db.session.commit()
                        
                        # Process the audio file in a background thread
                        try:
                            # Get the full path to the audio file
                            audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                            
                            # Log that we're starting transcription
                            logging.info(f"Starting automatic transcription for file: {unique_filename}")
                            
                            # Transcribe the audio (this could be moved to a background task for large files)
                            result = transcribe_audio(audio_path)
                            
                            if result and 'text' in result:
                                # Update the evidence record with the transcript
                                evidence.transcript = result['text']
                                evidence.transcript_status = 'completed'
                                evidence.processed_at = datetime.utcnow()
                                db.session.commit()
                                logging.info(f"Automatic transcription completed for file: {unique_filename}")
                                
                                # Now analyze the transcript
                                try:
                                    case = Case.get_case_by_id(case_id)
                                    if case:
                                        analysis_result = analyze_transcript(
                                            result['text'],  # Use text key instead of transcript
                                            case.description,
                                            case.issue_type,
                                            case.court_type
                                        )
                                        
                                        if analysis_result:
                                            evidence.transcript_analysis = json.dumps(analysis_result)
                                            evidence.analysis_status = 'completed'
                                        else:
                                            evidence.analysis_status = 'failed'
                                            logging.error("Analysis failed to generate valid results")
                                    else:
                                        # Handle the case where case is not found
                                        evidence.analysis_status = 'failed'
                                        logging.error("Case not found during analysis")
                                except Exception as e:
                                    evidence.analysis_status = 'failed'
                                    logging.error(f"Analysis error: {str(e)}")
                                    
                                # Commit changes regardless of analysis result
                                db.session.commit()
                            else:
                                evidence.transcript_status = 'failed'
                                logging.error(f"Transcription failed: {str(result) if result else 'No response from transcription service'}")
                            
                            db.session.commit()
                        except Exception as e:
                            # Log the error with proper logging
                            logging.error(f"Error processing audio/video file: {str(e)}")
                            
                            # Update the evidence status
                            evidence.transcript_status = 'failed'
                            evidence.analysis_status = 'failed'
                            
                            # Add error information to transcript field
                            evidence.transcript = f"Error transcribing file: {str(e)}\n\nYou can try again by clicking 'Generate Transcript' on the case summary page."
                            
                            # Save changes
                            db.session.commit()
                            
                            # No need to flash error message during upload - just log it
                            # The user will see a "Generate Transcript" button in the UI
                    
                    # Add appropriate upload message based on file type
                    if file_type in ['audio', 'video']:
                        flash('Evidence file uploaded successfully! Transcription has started and will continue in the background. You can leave this page and check back later - the transcript will be available when processing completes.', 'success')
                    else:
                        flash('Evidence file uploaded successfully!', 'success')
                    return redirect(url_for('cases.case_summary', case_id=case_id))
                else:
                    flash('Invalid file type. Please upload a supported file format.', 'danger')
                    return render_template('upload_evidence.html', form=form, case=case)
            
            elif form.evidence_type.data == 'link':
                # Handle social media or external link
                link_url = form.link_url.data
                platform = form.platform.data if form.platform.data else None
                
                print(f"Adding link evidence: {link_url} from platform: {platform}")  # Debug logging
                
                # Create link evidence
                evidence = Evidence.create_link_evidence(
                    case_id=case_id,
                    link_url=link_url,
                    description=form.description.data,
                    platform=platform
                )
                
                # Special handling for YouTube URLs - they can be transcribed
                if link_url and ('youtube.com' in link_url or 'youtu.be' in link_url):
                    try:
                        # Import needed for YouTube transcript analysis
                        from audio_processor import analyze_transcript
                        
                        # Mark for transcription like audio/video files
                        evidence.transcript_status = 'pending'
                        evidence.analysis_status = 'pending'
                        db.session.commit()
                        
                        # Extract the YouTube ID
                        youtube_id = ''
                        if 'youtube.com/watch?v=' in link_url:
                            youtube_id = link_url.split('youtube.com/watch?v=')[1].split('&')[0]
                        elif 'youtu.be/' in link_url:
                            youtube_id = link_url.split('youtu.be/')[1].split('?')[0]
                        
                        if youtube_id:
                            # Generate a placeholder transcript for now
                            # In a real implementation, we would call a YouTube transcription API
                            evidence.transcript = f"YouTube video ID: {youtube_id}\n\nTranscript for this video would be retrieved from YouTube's API in a production environment."
                            evidence.transcript_status = 'completed'
                            
                            # Now analyze the transcript
                            if case:
                                try:
                                    analysis_result = analyze_transcript(
                                        evidence.transcript,
                                        case.description,
                                        case.issue_type,
                                        case.court_type
                                    )
                                    
                                    if analysis_result:
                                        evidence.transcript_analysis = json.dumps(analysis_result)
                                        evidence.analysis_status = 'completed'
                                    else:
                                        evidence.analysis_status = 'failed'
                                except Exception as e:
                                    logging.error(f"YouTube analysis error: {str(e)}")
                                    evidence.analysis_status = 'failed'
                        
                        db.session.commit()
                        flash(f'YouTube link added with automatic transcript generation! Processing will continue in the background. You can leave this page and check back later - the analysis will be available when processing completes.', 'success')
                    except Exception as e:
                        logging.error(f"Error processing YouTube link: {str(e)}")
                        evidence.transcript_status = 'failed'
                        db.session.commit()
                        flash(f'YouTube link added! You can generate the transcript manually.', 'success')
                else:
                    flash(f'Social media/link evidence added successfully!', 'success')
                return redirect(url_for('cases.case_summary', case_id=case_id))
                
        except Exception as e:
            # Check if this is a file size error
            if "RequestEntityTooLarge" in str(e) or "413" in str(e):
                flash('Error: The uploaded file exceeds the maximum size limit (50MB).', 'danger')
            else:
                # Handle other errors
                print(f"ERROR in evidence form processing: {str(e)}")  # Debug logging
                import traceback
                traceback.print_exc()
                flash(f'Error processing evidence: {str(e)}', 'danger')
    
    return render_template('upload_evidence.html', form=form, case=case)
@cases.route('/evidence/transcript/<int:evidence_id>')
@login_required
def view_transcript(evidence_id):
    """Display transcript and analysis of an audio evidence item"""
    from audio_processor import transcribe_audio, analyze_transcript as audio_analyze_transcript
    from datetime import datetime
    import os
    import json
    
    # Rename the imported function to avoid name collision
    analyze_transcript = audio_analyze_transcript
    
    evidence = Evidence.get_evidence_by_id(evidence_id)
    
    if not evidence:
        flash('Evidence item not found.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Get the case this evidence belongs to
    case = evidence.cases.first()
    if not case:
        flash('Case not found for this evidence.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check if user has access
    if case.user_id != current_user.id and not current_user.is_moderator() and not current_user.is_legal_assistant():
        flash('You do not have permission to view this evidence.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check if this is an audio or video file or YouTube link
    is_youtube = evidence.evidence_type == 'link' and evidence.platform == 'YouTube'
    if evidence.file_type not in ['audio', 'video'] and not is_youtube:
        flash('This feature is only available for audio, video, and YouTube evidence.', 'warning')
        return redirect(url_for('cases.case_summary', case_id=case.id))
    
    # Check if user wants to process the audio
    process = request.args.get('process', False)
    regenerate = request.args.get('regenerate', False)
    analyze = request.args.get('analyze', False)
    
    # Process audio/video/YouTube for transcription
    if (process or regenerate) and (evidence.transcript_status != 'pending'):
        # Check if this is a YouTube link
        is_youtube = evidence.evidence_type == 'link' and evidence.platform == 'YouTube'
        
        if is_youtube:
            try:
                # Update status to pending
                evidence.transcript_status = 'pending'
                db.session.commit()
                
                # We would fetch the YouTube transcript here using an API
                # For now, create a placeholder result with YouTube ID
                youtube_id = ''
                if 'youtube.com/watch?v=' in evidence.link_url:
                    youtube_id = evidence.link_url.split('youtube.com/watch?v=')[1].split('&')[0]
                elif 'youtu.be/' in evidence.link_url:
                    youtube_id = evidence.link_url.split('youtu.be/')[1].split('?')[0]
                    
                transcript_result = {
                    'text': f"YouTube video ID: {youtube_id}\n\nThis system will automatically retrieve the transcript from this YouTube video for legal analysis."
                }
            except Exception as e:
                flash(f'Error processing YouTube link: {str(e)}', 'danger')
                transcript_result = None
        elif not evidence.filename or not os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], evidence.filename)):
            flash('Audio/video file not found on server.', 'danger')
            transcript_result = None
        else:
            try:
                # Update status to pending
                evidence.transcript_status = 'pending'
                db.session.commit()
                
                # Start transcription (this would ideally be in a background task)
                transcript_result = transcribe_audio(os.path.join(current_app.config['UPLOAD_FOLDER'], evidence.filename))
                
                if transcript_result and 'text' in transcript_result:
                    evidence.transcript = transcript_result['text']
                    evidence.transcript_status = 'completed'
                    evidence.processed_at = datetime.utcnow()
                    
                    # Also generate analysis if transcript is successful
                    analysis_result = analyze_transcript(
                        evidence.transcript, 
                        case.description,
                        case.issue_type,
                        case.court_type
                    )
                    
                    if analysis_result:
                        evidence.transcript_analysis = json.dumps(analysis_result)
                        evidence.analysis_status = 'completed'
                    else:
                        evidence.analysis_status = 'failed'
                else:
                    evidence.transcript_status = 'failed'
                
                db.session.commit()
                
                if evidence.transcript_status == 'completed':
                    flash('Audio transcription completed successfully!', 'success')
                else:
                    flash('Failed to transcribe audio.', 'danger')
            except Exception as e:
                evidence.transcript_status = 'failed'
                db.session.commit()
                logging.error(f"Transcription error: {str(e)}")
                flash(f'Error processing audio: {str(e)}', 'danger')
    
    # Analyze transcript
    elif analyze and evidence.transcript and (evidence.analysis_status != 'pending'):
        try:
            # Update status to pending
            evidence.analysis_status = 'pending'
            db.session.commit()
            
            # Generate analysis
            analysis_result = analyze_transcript(
                evidence.transcript, 
                case.description,
                case.issue_type,
                case.court_type
            )
            
            if analysis_result:
                evidence.transcript_analysis = json.dumps(analysis_result)
                evidence.analysis_status = 'completed'
                flash('Analysis completed successfully!', 'success')
            else:
                evidence.analysis_status = 'failed'
                flash('Failed to analyze transcript.', 'danger')
            
            db.session.commit()
        except Exception as e:
            evidence.analysis_status = 'failed'
            db.session.commit()
            logging.error(f"Analysis error: {str(e)}")
            flash(f'Error analyzing transcript: {str(e)}', 'danger')
    
    return render_template('view_transcript.html', evidence=evidence, case=case)

@cases.route('/evidence/file/<int:evidence_id>')
@login_required
def get_evidence_file(evidence_id):
    """Retrieve an evidence file for display/playback in the browser"""
    evidence = Evidence.get_evidence_by_id(evidence_id)
    
    if not evidence or not evidence.filename:
        flash('Evidence file not found.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Check if user has access to the case this evidence belongs to
    if evidence.cases.first().user_id != current_user.id and not current_user.is_moderator() and not current_user.is_legal_assistant():
        flash('You do not have permission to access this file.', 'danger')
        return redirect(url_for('cases.dashboard'))
    
    # Get file extension to determine content type
    file_ext = evidence.original_filename.rsplit('.', 1)[-1].lower()
    
    # Map file extensions to MIME types
    mime_types = {
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'ogg': 'audio/ogg',
        'm4a': 'audio/mp4',
        'aac': 'audio/aac',
        'flac': 'audio/flac',
        'wma': 'audio/x-ms-wma',
        'mp4': 'video/mp4',
        'mov': 'video/quicktime',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain',
        'rtf': 'application/rtf'
    }
    
    # Get the appropriate MIME type or default to octet-stream
    content_type = mime_types.get(file_ext, 'application/octet-stream')
    
    # Return the file with the appropriate content type
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        evidence.filename,
        mimetype=content_type,
        as_attachment=False,
        download_name=evidence.original_filename
    )