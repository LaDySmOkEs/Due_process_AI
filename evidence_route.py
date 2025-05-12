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