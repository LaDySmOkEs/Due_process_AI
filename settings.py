from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
import os
import sys

import anthropic_helper

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    if request.method == 'POST':
        # Handle API key updates
        if 'anthropic_api_key' in request.form:
            anthropic_key = request.form['anthropic_api_key'].strip()
            
            if anthropic_key:
                # In a real deployment, you would store this securely in a database
                # For the demo, we'll set it as an environment variable
                os.environ['ANTHROPIC_API_KEY'] = anthropic_key
                
                # Reinitialize the Anthropic helper with the new key
                import importlib
                importlib.reload(anthropic_helper)
                
                flash('Anthropic API key set successfully! Claude AI is now available as a backup.', 'success')
            else:
                flash('Please enter a valid API key.', 'danger')
                
        return redirect(url_for('settings.settings'))
        
    # Check if keys are configured
    anthropic_configured = anthropic_helper.is_available()
    
    return render_template(
        'settings.html',
        anthropic_configured=anthropic_configured
    )