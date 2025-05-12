"""
Ad Tracking and Analytics module for campaign attribution and tracking
"""
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, session, redirect, url_for
from models import db
from models import AdClick

# Create blueprint
ad_tracking = Blueprint('ad_tracking', __name__)

# Dictionary of ad messages corresponding to campaign IDs
AD_MESSAGES = {
    'legal_partner': "Your AI Legal Partner That Fights For You",
    'lost_system': "Feeling Lost In The Legal System? We'll Guide You Through.",
    'evidence': "Evidence Analysis That Leaves Nothing Unexamined",
    'jargon': "Legal Jargon Simplified - Complex Terms Made Simple",
    'rights': "Your Rights Matter. We Help You Protect Them.",
    'defender': "The Public Defender Alternative That Works For You",
    'win_case': "Win Your Case Without A Law Degree",
    'overlooked': "Don't Let Critical Evidence Be Overlooked",
    'faith_justice': "Justice For All: Faith-Based Principles In Legal Advocacy"
}

@ad_tracking.route('/from/<campaign_id>')
def ad_landing(campaign_id):
    """
    Landing page for ad campaigns with tracking
    Records analytics data and shows customized landing page
    """
    # Get UTM parameters for better attribution
    source = request.args.get('utm_source', 'direct')
    medium = request.args.get('utm_medium', 'none')
    content = request.args.get('utm_content', 'none')
    
    # Store campaign in session for conversion tracking later
    session['ad_campaign'] = campaign_id
    session['ad_source'] = source
    session['ad_medium'] = medium
    session['ad_timestamp'] = datetime.utcnow().isoformat()
    
    # Record click in database
    try:
        click = AdClick()
        click.campaign_id = campaign_id
        click.source = source
        click.medium = medium
        click.content = content
        click.ip_address = request.remote_addr
        click.user_agent = request.user_agent.string
        click.timestamp = datetime.utcnow()
        db.session.add(click)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error recording ad click: {str(e)}")
        db.session.rollback()
    
    # Get ad message for this campaign
    ad_message = AD_MESSAGES.get(campaign_id, "Your AI-Powered Legal Assistant")
    
    # Special handling for faith-based campaign
    if campaign_id == 'faith_justice':
        return render_template(
            'ad_landing.html', 
            ad_message=ad_message,
            show_faith_content=True
        )
    
    # Render landing page with campaign-specific content
    return render_template('ad_landing.html', ad_message=ad_message)

@ad_tracking.route('/admin/campaigns')
def view_campaigns():
    """Admin interface to view campaign performance"""
    # Could be implemented later if needed
    return redirect(url_for('home'))

@ad_tracking.route('/ad-documentation')
def ad_documentation():
    """Documentation page for setting up ad campaigns"""
    return render_template('ad_documentation.html')