import os
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
import json
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize the database
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# Upload configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 75 * 1024 * 1024  # 75MB max upload
app.config['MAX_CONTENT_PATH'] = 2 * 1024 * 1024  # 2MB max for URL/form data

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Import routes after app initialization to avoid circular imports
from models import User, Case, Evidence, Document, LegalAnalysis
from auth import auth as auth_blueprint, create_demo_users
from cases import cases as cases_blueprint
from documents import documents as documents_blueprint
from ai_analysis import ai as ai_blueprint
from settings import settings_bp
from evidence_analysis import evidence_ai
from client_interview import client_interview
from court_script import court_script
from case_timeline import timeline
from legal_jargon import legal_jargon as legal_jargon_blueprint
from ad_tracking import ad_tracking
from stripe_integration import stripe_bp

# Register blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(cases_blueprint)
app.register_blueprint(documents_blueprint)
app.register_blueprint(ai_blueprint)
app.register_blueprint(settings_bp)
app.register_blueprint(evidence_ai)
app.register_blueprint(client_interview)
app.register_blueprint(court_script)
app.register_blueprint(timeline)
app.register_blueprint(legal_jargon_blueprint)
app.register_blueprint(ad_tracking)
app.register_blueprint(stripe_bp, url_prefix='/stripe')

# Create all database tables and demo users
with app.app_context():
    db.create_all()
    create_demo_users()
    
    # Populate the legal terms database
    try:
        # Import here to avoid circular imports
        from legal_terms_database import LEGAL_TERMS
        from models import LegalTerm
        
        # Track progress
        added_count = 0
        existing_count = 0
        
        # Add each term to the database if it doesn't already exist
        for term, explanation in LEGAL_TERMS.items():
            # Check if term already exists
            existing_term = LegalTerm.get_term(term)
            
            if not existing_term:
                # Add the new term
                try:
                    LegalTerm.create_term(
                        term=term,
                        simple_explanation=explanation['simple_explanation'],
                        fun_explanation=explanation['fun_explanation'],
                        cartoon_description=explanation['cartoon_description'],
                        ai_generated=False,  # These are our predefined terms
                        verified=True        # These are verified as accurate
                    )
                    added_count += 1
                except Exception as e:
                    app.logger.error(f"Error adding term '{term}': {str(e)}")
            else:
                existing_count += 1
        
        app.logger.info(f"Legal jargon database: {added_count} terms added, {existing_count} terms already exist")
    except Exception as e:
        app.logger.error(f"Error populating legal terms database: {str(e)}")

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))  # Use SQLAlchemy query directly
    except:
        return None

# Base route
@app.route('/')
def home():
    return render_template('home.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(f"404 error: {e}")
    return render_template('errors/404.html'), 404

@app.errorhandler(413)
def request_entity_too_large(e):
    app.logger.error(f"413 error: {e}")
    return render_template('upload_error.html', max_size_mb=int(app.config['MAX_CONTENT_LENGTH']/(1024*1024))), 413

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"500 error: {e}")
    # Include more details in dev mode
    error_details = str(e) if app.debug else "Internal server error"
    return render_template('errors/500.html', error=error_details), 500

# Template context processors
@app.context_processor
def utility_processor():
    return {
        'now': datetime.utcnow,
        'user': current_user
    }

# Add custom template filters
@app.template_filter('fromjson')
def from_json(value):
    """Convert a JSON string to Python object"""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}
