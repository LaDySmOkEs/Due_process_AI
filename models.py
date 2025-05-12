import json
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# User roles
ROLE_USER = 'user'        # General users (litigants)
ROLE_LEGAL = 'legal'      # Legal assistants/paralegals
ROLE_MOD = 'moderator'    # Moderators (review content)
ROLE_PREMIUM = 'premium'  # Pro/premium users with advanced tools

# Association table for case evidence
case_evidence = db.Table('case_evidence',
    db.Column('case_id', db.Integer, db.ForeignKey('case.id'), primary_key=True),
    db.Column('evidence_id', db.Integer, db.ForeignKey('evidence.id'), primary_key=True)
)

class Subscription(db.Model):
    """Model for tracking user subscriptions and payments."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Subscription status
    status = db.Column(db.String(20), default='pending')  # active, past_due, canceled, trialing, pending
    subscription_type = db.Column(db.String(20), default='premium')  # premium, basic, etc.
    
    # Premium pricing info - $50/month standard rate
    price_usd = db.Column(db.Float, default=50.00)
    original_price_usd = db.Column(db.Float, default=50.00)  # Store original price for reference
    
    # Fee waiver for indigent users
    fee_waiver = db.Column(db.Boolean, default=False)
    fee_waiver_reason = db.Column(db.Text, nullable=True)
    fee_waiver_approved = db.Column(db.Boolean, default=False)
    fee_waiver_reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    fee_waiver_notes = db.Column(db.Text, nullable=True)  # Admin notes on waiver review
    waiver_percentage = db.Column(db.Integer, default=0)  # Percentage of fee waived (0-100)
    
    # Income information for sliding scale fee waiver
    annual_income = db.Column(db.Float, nullable=True)
    household_size = db.Column(db.Integer, nullable=True)
    
    # Stripe integration
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    payment_method = db.Column(db.String(50), default='stripe')
    
    # Subscription dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    last_payment_date = db.Column(db.DateTime, nullable=True)
    next_payment_date = db.Column(db.DateTime, nullable=True)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, subscription_type='premium', price_usd=50.00, 
                 status='pending', stripe_subscription_id=None, stripe_customer_id=None):
        self.user_id = user_id
        self.subscription_type = subscription_type
        self.price_usd = price_usd
        self.original_price_usd = price_usd
        self.status = status
        self.stripe_subscription_id = stripe_subscription_id
        self.stripe_customer_id = stripe_customer_id
        self.start_date = datetime.utcnow()
        
        # Set next payment date (monthly by default)
        self.next_payment_date = self.start_date + timedelta(days=30)
    
    def apply_fee_waiver(self, reason, annual_income=None, household_size=None):
        """
        Apply for an indigent fee waiver using sliding scale based on poverty guidelines
        
        Args:
            reason: The applicant's explanation for requesting a fee waiver
            annual_income: The applicant's annual income
            household_size: The number of people in the applicant's household
        """
        self.fee_waiver = True
        self.fee_waiver_reason = reason
        self.fee_waiver_approved = False  # Requires review/approval
        
        # Store income information for sliding scale calculation
        if annual_income is not None:
            self.annual_income = annual_income
        if household_size is not None:
            self.household_size = household_size
            
        return True
    
    def approve_fee_waiver(self, reviewer_id, waiver_percentage=None):
        """
        Approve a fee waiver application with a specified waiver percentage
        
        If waiver_percentage is not specified, it will be calculated based on 
        the applicant's income relative to poverty guidelines
        """
        from fee_waiver_calculator import calculate_fee_waiver_percentage
        
        self.fee_waiver_approved = True
        self.fee_waiver_reviewed_by = reviewer_id
        
        # Calculate waiver percentage if not specified
        if waiver_percentage is None and self.annual_income and self.household_size:
            waiver_percentage = calculate_fee_waiver_percentage(
                self.annual_income, 
                self.household_size
            )
        elif waiver_percentage is None:
            # Default to 100% waiver if income information is not available
            waiver_percentage = 100
            
        self.waiver_percentage = waiver_percentage
        
        # Apply the waiver percentage to calculate the adjusted price
        discount = (waiver_percentage / 100) * self.original_price
        self.price = max(0, self.original_price - discount)
        
        return True
    
    def get_waiver_status_text(self):
        """Get human-readable waiver status text"""
        if not self.fee_waiver:
            return "No fee waiver applied"
        elif not self.fee_waiver_approved:
            return "Fee waiver pending review"
        elif self.waiver_percentage == 100:
            return "100% fee waiver approved"
        else:
            return f"{self.waiver_percentage}% fee waiver approved"
    
    def is_waiver_pending(self):
        """Check if a fee waiver application is pending review"""
        return self.fee_waiver and not self.fee_waiver_approved
    
    def cancel(self):
        """Cancel a subscription"""
        self.is_active = False
        self.end_date = datetime.utcnow()
        return True
    
    @classmethod
    def create_subscription(cls, user_id, subscription_type='monthly', price=50.00):
        """Create a new subscription for a user"""
        new_subscription = cls(user_id, subscription_type, price)
        db.session.add(new_subscription)
        db.session.commit()
        return new_subscription
    
    @classmethod
    def get_subscription(cls, user_id):
        """Get a user's active subscription if any"""
        return cls.query.filter_by(user_id=user_id, is_active=True).first()


class User(UserMixin, db.Model):
    """User model for authentication and role-based access."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default=ROLE_USER, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cases = db.relationship('Case', backref='user', lazy=True)
    documents = db.relationship('Document', backref='user', lazy=True)
    subscriptions = db.relationship('Subscription', foreign_keys='Subscription.user_id', backref='subscriber', lazy=True)
    waiver_reviews = db.relationship('Subscription', foreign_keys='Subscription.fee_waiver_reviewed_by', backref='reviewer', lazy=True)
    
    def __init__(self, username, email, password, role=ROLE_USER):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_legal_assistant(self):
        return self.role == ROLE_LEGAL
    
    def is_moderator(self):
        return self.role == ROLE_MOD
    
    def is_premium(self):
        """Check if user has premium access either by role or active subscription"""
        if self.role == ROLE_PREMIUM:
            return True
            
        # Check for active subscription with either payment or approved fee waiver
        subscription = Subscription.get_subscription(self.id)
        if subscription and subscription.is_active:
            if subscription.fee_waiver_approved or subscription.next_payment_date > datetime.utcnow():
                return True
                
        return False
    
    def get_active_subscription(self):
        """Get user's current subscription if any"""
        return Subscription.get_subscription(self.id)
    
    @classmethod
    def create_user(cls, username, email, password, role=ROLE_USER):
        new_user = cls(username, email, password, role)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.get(user_id)
    
    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

class Case(db.Model):
    """Case model for storing case information."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    court_type = db.Column(db.String(50), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ai_analysis = db.Column(db.Text, nullable=True)  # AI-generated case analysis
    legal_strategy = db.Column(db.Text, nullable=True)  # AI-generated legal strategy
    precedent_cases = db.Column(db.Text, nullable=True)  # Related case law
    success_probability = db.Column(db.Float, nullable=True)  # AI-calculated probability of success
    
    # Relationships
    evidence_items = db.relationship('Evidence', secondary=case_evidence, 
                            backref=db.backref('cases', lazy='dynamic'))
    documents = db.relationship('Document', backref='case', lazy=True)
    
    def __init__(self, user_id, title, court_type, issue_type, description):
        self.user_id = user_id
        self.title = title
        self.court_type = court_type
        self.issue_type = issue_type
        self.description = description
    
    @classmethod
    def create_case(cls, user_id, title, court_type, issue_type, description):
        new_case = cls(user_id, title, court_type, issue_type, description)
        db.session.add(new_case)
        db.session.commit()
        return new_case
    
    @classmethod
    def get_case_by_id(cls, case_id):
        return cls.query.get(case_id)
    
    @classmethod
    def get_cases_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()
    
    def add_evidence(self, evidence):
        if evidence not in self.evidence_items:
            self.evidence_items.append(evidence)
            db.session.commit()
    
    def get_evidence(self):
        return self.evidence_items

class Evidence(db.Model):
    """Evidence model for storing uploaded files or social media links."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))  # Secure filename on server
    original_filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    evidence_type = db.Column(db.String(20), default='file')  # 'file' or 'link'
    link_url = db.Column(db.String(512))  # URL for social media or external links
    platform = db.Column(db.String(50))  # Social media platform (YouTube, Facebook, etc.)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    transcript = db.Column(db.Text)  # For audio file transcripts
    transcript_status = db.Column(db.String(50))  # 'pending', 'completed', 'failed'
    transcript_analysis = db.Column(db.Text)  # JSON analysis of audio transcripts
    analysis_status = db.Column(db.String(50))  # 'pending', 'completed', 'failed'
    processed_at = db.Column(db.DateTime)  # When transcript was processed
    
    def __init__(self, filename, original_filename, description, file_type, evidence_type='file', 
              link_url=None, platform=None, transcript=None, transcript_status=None, 
              transcript_analysis=None, analysis_status=None, processed_at=None):
        self.filename = filename
        self.original_filename = original_filename
        self.description = description
        self.file_type = file_type
        self.evidence_type = evidence_type
        self.link_url = link_url
        self.platform = platform
        self.transcript = transcript
        self.transcript_status = transcript_status
        self.transcript_analysis = transcript_analysis
        self.analysis_status = analysis_status
        self.processed_at = processed_at
    
    @classmethod
    def create_evidence(cls, case_id, filename, original_filename, description, file_type, evidence_type='file', 
                       link_url=None, platform=None, transcript=None, transcript_status=None, 
                       transcript_analysis=None, analysis_status=None, processed_at=None):
        new_evidence = cls(
            filename=filename,
            original_filename=original_filename,
            description=description,
            file_type=file_type,
            evidence_type=evidence_type,
            link_url=link_url,
            platform=platform,
            transcript=transcript,
            transcript_status=transcript_status,
            transcript_analysis=transcript_analysis,
            analysis_status=analysis_status,
            processed_at=processed_at
        )
        
        db.session.add(new_evidence)
        db.session.commit()
        
        # Add evidence to case
        case = Case.get_case_by_id(case_id)
        if case:
            case.add_evidence(new_evidence)
        
        return new_evidence
        
    @classmethod
    def create_link_evidence(cls, case_id, link_url, description, platform=None):
        """Create a new evidence entry from a social media or external link."""
        # Extract platform from URL if not specified
        if not platform:
            if 'youtube.com' in link_url or 'youtu.be' in link_url:
                platform = 'YouTube'
            elif 'facebook.com' in link_url:
                platform = 'Facebook'
            elif 'twitter.com' in link_url or 'x.com' in link_url:
                platform = 'Twitter/X'
            elif 'instagram.com' in link_url:
                platform = 'Instagram'
            elif 'tiktok.com' in link_url:
                platform = 'TikTok'
            elif 'linkedin.com' in link_url:
                platform = 'LinkedIn'
            else:
                platform = 'External Link'
        
        # Use the platform name as the "original filename"
        original_filename = f"{platform} Link"
        
        return cls.create_evidence(
            case_id=case_id,
            filename=None,  # No actual file
            original_filename=original_filename,
            description=description,
            file_type='link',
            evidence_type='link',
            link_url=link_url,
            platform=platform
        )
    
    @classmethod
    def get_evidence_by_id(cls, evidence_id):
        return cls.query.get(evidence_id)
    
    @classmethod
    def get_evidence_by_case(cls, case_id):
        case = Case.query.get(case_id)
        if case:
            return case.evidence_items
        return []

class LegalAnalysis(db.Model):
    """AI-powered legal analysis that replaces attorney expertise."""
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # Type: 'case_law', 'strategy', 'risk', etc.
    content = db.Column(db.Text, nullable=False)  # Analysis content
    references = db.Column(db.Text, nullable=True)  # Citations and references
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float, nullable=True)  # AI confidence level
    
    # Premium feature fields
    success_probability = db.Column(db.Float, nullable=True)  # Premium feature - probability of success (0-1)
    probability_factors = db.Column(db.Text, nullable=True)  # Factors influencing probability as JSON
    probability_suggestions = db.Column(db.Text, nullable=True)  # Improvement suggestions as JSON
    
    # Relationship back to the case
    case = db.relationship('Case', backref=db.backref('analysis', lazy='dynamic'))
    
    def __init__(self, case_id, analysis_type, content, references=None, confidence_score=None,
                 success_probability=None, probability_factors=None, probability_suggestions=None):
        self.case_id = case_id
        self.analysis_type = analysis_type
        self.content = content
        self.references = references
        self.confidence_score = confidence_score
        self.success_probability = success_probability
        
        # Convert list to JSON string if needed
        if probability_factors and isinstance(probability_factors, list):
            self.probability_factors = json.dumps(probability_factors)
        else:
            self.probability_factors = probability_factors
            
        # Convert list to JSON string if needed
        if probability_suggestions and isinstance(probability_suggestions, list):
            self.probability_suggestions = json.dumps(probability_suggestions)
        else:
            self.probability_suggestions = probability_suggestions
    
    @classmethod
    def create_analysis(cls, case_id, analysis_type, content, references=None, confidence_score=None,
                       success_probability=None, probability_factors=None, probability_suggestions=None):
        # Ensure references is not an empty list, as it causes parsing issues
        if references == '[]':
            # Default empty structure based on analysis type
            if analysis_type == 'case_law':
                references = json.dumps({
                    "rights_assessment": [
                        {
                            "right_violated": "Analysis in Progress",
                            "explanation": "Your rights analysis is being generated. Please check back soon.",
                            "severity": "Medium",
                            "supporting_legal_principle": "Analysis preparation in progress"
                        }
                    ],
                    "case_law_suggestions": [
                        {
                            "case_name": "Analysis in Progress",
                            "year": "2025",
                            "court": "Supreme Court",
                            "relevance": "Case law analysis is being generated",
                            "principles": "Analysis in progress",
                            "key_quotes": ["Please check back soon"],
                            "strategic_application": "Try regenerating the analysis",
                            "counter_arguments": "Analysis preparation in progress"
                        }
                    ],
                    "winning_strategy": {
                        "primary_approach": "Proven Winning Strategy: Comprehensive legal attack on procedural and evidentiary weaknesses",
                        "attack_defense_tactics": [
                            "Identify and exploit ALL procedural errors by law enforcement and prosecution",
                            "Develop aggressive challenges to evidence chain of custody and collection methods", 
                            "Analysis of additional tactics in progress..."
                        ],
                        "procedural_motions": [
                            "File powerful Brady motions demanding complete disclosure of ALL evidence", 
                            "Additional strategic motions being prepared..."
                        ],
                        "evidence_challenges": "Aggressively challenge EVERY piece of evidence using both technical and constitutional grounds",
                        "hearing_objections": "Object to ALL prosecution statements with precision timing to disrupt their case flow",
                        "timing_strategy": "Deploy legal maneuvers in precisely calculated sequence for maximum impact and guaranteed success"
                    }
                })
            elif analysis_type == 'document_recommendations':
                references = json.dumps({
                    "document_recommendations": [
                        {
                            "document_type": "Analysis in Progress",
                            "rationale": "Document recommendations are being generated",
                            "strategic_guidance": "Please check back soon",
                            "key_elements": ["Analysis in progress"],
                            "timing": "Try again soon",
                            "importance": "Medium",
                            "impact": "Analysis preparation in progress"
                        }
                    ]
                })
            elif analysis_type == 'success_probability':
                if not probability_factors:
                    probability_factors = json.dumps([
                        "Analysis in progress",
                        "Detailed factors will be shown after processing"
                    ])
                if not probability_suggestions:
                    probability_suggestions = json.dumps([
                        "Analysis in progress",
                        "Improvement suggestions will be provided after processing"
                    ])
                
        new_analysis = cls(
            case_id=case_id, 
            analysis_type=analysis_type, 
            content=content, 
            references=references, 
            confidence_score=confidence_score,
            success_probability=success_probability,
            probability_factors=probability_factors,
            probability_suggestions=probability_suggestions
        )
        db.session.add(new_analysis)
        db.session.commit()
        return new_analysis
    
    @classmethod
    def get_by_case_and_type(cls, case_id, analysis_type):
        return cls.query.filter_by(case_id=case_id, analysis_type=analysis_type).order_by(cls.generated_at.desc()).first()
    
    @classmethod
    def get_all_by_case(cls, case_id):
        return db.session.query(cls).filter_by(case_id=case_id).order_by(cls.analysis_type, cls.generated_at.desc()).all()


class Document(db.Model):
    """Document model for storing generated legal documents."""
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doc_type = db.Column(db.String(100), nullable=False)  # E.g., "Motion to Quash", "Civil Cover Sheet"
    state = db.Column(db.String(2), nullable=False)  # State jurisdiction (two-letter code)
    court_type = db.Column(db.String(50), nullable=False)  # Federal, State, etc.
    content = db.Column(db.Text, nullable=False)  # Document content/data
    filename = db.Column(db.String(255), nullable=False)  # Generated filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, case_id, user_id, doc_type, state, court_type, content, filename):
        self.case_id = case_id
        self.user_id = user_id
        self.doc_type = doc_type
        self.state = state
        self.court_type = court_type
        self.content = content
        self.filename = filename
    
    @classmethod
    def create_document(cls, case_id, user_id, doc_type, state, court_type, content, filename):
        new_doc = cls(case_id, user_id, doc_type, state, court_type, content, filename)
        db.session.add(new_doc)
        db.session.commit()
        return new_doc
    
    @classmethod
    def get_document_by_id(cls, doc_id):
        return cls.query.get(doc_id)
    
    @classmethod
    def get_documents_by_case(cls, case_id):
        return cls.query.filter_by(case_id=case_id).all()
    
    @classmethod
    def get_documents_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()


class LegalTerm(db.Model):
    """Model for storing legal jargon terms and their explanations."""
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), unique=True, nullable=False)
    simple_explanation = db.Column(db.Text, nullable=False)
    fun_explanation = db.Column(db.Text, nullable=False)
    cartoon_description = db.Column(db.Text, nullable=False)
    
    # Metadata
    ai_generated = db.Column(db.Boolean, default=True)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    search_count = db.Column(db.Integer, default=1)  # Track popularity
    
    def __init__(self, term, simple_explanation, fun_explanation, cartoon_description, 
                ai_generated=True, verified=False):
        self.term = term.lower()
        self.simple_explanation = simple_explanation
        self.fun_explanation = fun_explanation
        self.cartoon_description = cartoon_description
        self.ai_generated = ai_generated
        self.verified = verified
    
    @classmethod
    def create_term(cls, term, simple_explanation, fun_explanation, cartoon_description,
                   ai_generated=True, verified=False):
        """Create a new legal term with explanations."""
        new_term = cls(
            term=term.lower(),
            simple_explanation=simple_explanation,
            fun_explanation=fun_explanation,
            cartoon_description=cartoon_description,
            ai_generated=ai_generated,
            verified=verified
        )
        db.session.add(new_term)
        db.session.commit()
        return new_term
    
    @classmethod
    def get_term(cls, term):
        """Get a legal term by its exact name."""
        return cls.query.filter_by(term=term.lower()).first()
    
    @classmethod
    def get_similar_terms(cls, term, limit=5):
        """Get terms containing the search phrase (for autocomplete)."""
        return cls.query.filter(cls.term.contains(term.lower())).order_by(cls.search_count.desc()).limit(limit).all()
    
    @classmethod
    def get_popular_terms(cls, limit=10):
        """Get most frequently searched terms."""
        return cls.query.order_by(cls.search_count.desc()).limit(limit).all()
    
    @classmethod
    def increment_search_count(cls, term_id):
        """Increment the search count for a term."""
        term = cls.query.get(term_id)
        if term:
            term.search_count += 1
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'id': self.id,
            'term': self.term,
            'simple_explanation': self.simple_explanation,
            'fun_explanation': self.fun_explanation,
            'cartoon_description': self.cartoon_description,
            'search_count': self.search_count
        }


# Ad Tracking Models
class AdCampaign(db.Model):
    """Model for tracking ad campaigns"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # No relationship here to avoid circular dependency issues
    
    def __repr__(self):
        return f'<AdCampaign {self.campaign_id}>'


class AdClick(db.Model):
    """Model for tracking ad clicks and conversions"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(50), nullable=True)  # utm_source
    medium = db.Column(db.String(50), nullable=True)  # utm_medium
    content = db.Column(db.String(50), nullable=True)  # utm_content
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    converted = db.Column(db.Boolean, default=False)
    conversion_type = db.Column(db.String(50), nullable=True)  # registration, premium, etc.
    conversion_timestamp = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<AdClick {self.id} - {self.campaign_id}>'
