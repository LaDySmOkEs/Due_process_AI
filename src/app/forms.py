from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, SubmitField, RadioField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, URL
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.get_user_by_username(username.data)
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.get_user_by_email(email.data)
        if user:
            raise ValidationError('Email already registered. Please use another one or login.')

class CaseForm(FlaskForm):
    title = StringField('Case Title', validators=[DataRequired(), Length(max=100)])
    court_type = SelectField('Court Type', choices=[
        ('', 'Select Court Type'),
        ('federal', 'Federal Court'),
        ('state', 'State Court'),
        ('appellate', 'Appellate Court'),
        ('municipal', 'Municipal Court'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    issue_type = SelectField('Issue Type', choices=[
        ('', 'Select Issue Type'),
        ('civil', 'Civil'),
        ('criminal', 'Criminal'),
        ('family', 'Family'),
        ('immigration', 'Immigration'),
        ('bankruptcy', 'Bankruptcy'),
        ('intellectual_property', 'Intellectual Property'),
        ('personal_injury', 'Personal Injury'),
        ('contract', 'Contract Dispute'),
        ('housing', 'Housing/Eviction'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Case Description', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Create Case')

class EvidenceForm(FlaskForm):
    evidence_type = RadioField(
        'Evidence Type', 
        choices=[('file', 'Upload File'), ('link', 'Social Media/External Link')],
        default='file',
        validators=[DataRequired()]
    )
    file = FileField('File', validators=[
        Optional()
    ])
    link_url = StringField('URL', validators=[
        Optional(),
        URL(message="Please enter a valid URL including http:// or https://")
    ])
    platform = SelectField('Platform', choices=[
        ('', 'Select Platform (Optional)'),
        ('YouTube', 'YouTube'),
        ('Facebook', 'Facebook'),
        ('Twitter/X', 'Twitter/X'),
        ('Instagram', 'Instagram'),
        ('TikTok', 'TikTok'),
        ('LinkedIn', 'LinkedIn'), 
        ('Other', 'Other Website/Link')
    ], validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit Evidence')
    
    def validate(self, extra_validators=None):
        """Custom validation to ensure either file or link is provided based on evidence type."""
        if not super().validate(extra_validators=extra_validators):
            return False
            
        if self.evidence_type.data == 'file':
            if not self.file.data:
                self.file.errors = list(self.file.errors) + ['Please upload a file.']
                return False
        elif self.evidence_type.data == 'link':
            if not self.link_url.data:
                self.link_url.errors = list(self.link_url.errors) + ['Please provide a URL.']
                return False
                
        return True

class FilingToolkitForm(FlaskForm):
    case_id = SelectField('Select Case', validators=[DataRequired()])
    state = SelectField('State', choices=[
        ('', 'Select State'),
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
        ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'District of Columbia')
    ], validators=[DataRequired()])
    
    court_type = SelectField('Court Type', choices=[
        ('', 'Select Court Type'),
        ('federal_district', 'Federal District Court'),
        ('federal_appeals', 'Federal Court of Appeals'),
        ('state_trial', 'State Trial Court'),
        ('state_appeals', 'State Court of Appeals'),
        ('state_supreme', 'State Supreme Court'),
        ('municipal', 'Municipal Court'),
        ('small_claims', 'Small Claims Court')
    ], validators=[DataRequired()])
    
    form_type = SelectField('Form Type', choices=[
        ('', 'Select Form Type'),
        ('motion_to_quash', 'Motion to Quash Warrant'),
        ('civil_cover_sheet', 'Civil Cover Sheet'),
        ('section_1983', '§1983 Complaint (Civil Rights)'),
        ('habeas_corpus', 'Habeas Corpus Petition'),
        ('discovery_request', 'Discovery Request'),
        ('motion_to_dismiss', 'Motion to Dismiss'),
        ('answer_complaint', 'Answer to Complaint')
    ], validators=[DataRequired()])
    
    deadline_date = DateField('Filing Deadline', format='%Y-%m-%d')
    submit = SubmitField('Generate Document')

class SubscriptionForm(FlaskForm):
    """Form for managing premium subscriptions"""
    subscription_type = SelectField('Subscription Plan', choices=[
        ('monthly', 'Monthly - $50/month'),
        ('annual', 'Annual - $500/year (Save $100)'),
        ('lifetime', 'Lifetime - $1,500 (Best Value)')
    ], validators=[DataRequired()])
    submit = SubmitField('Subscribe', name='subscribe_submit')

class FeeWaiverForm(FlaskForm):
    """Form for applying for an indigent fee waiver using sliding scale based on poverty guidelines"""
    annual_income = StringField('Annual Household Income ($)', 
                              validators=[DataRequired()])
    household_size = SelectField('Household Size', choices=[
        ('1', '1 person'),
        ('2', '2 people'),
        ('3', '3 people'),
        ('4', '4 people'),
        ('5', '5 people'),
        ('6', '6 people'),
        ('7', '7 people'),
        ('8', '8 people'),
        ('9', '9 people'),
        ('10', '10+ people')
    ], validators=[DataRequired()])
    reason = TextAreaField('Please explain your financial situation that qualifies you for an indigent fee waiver', 
                         validators=[DataRequired(), Length(min=100, max=2000)])
    certify = RadioField('I certify that:', choices=[
        ('true', 'The financial information I have provided is true and accurate.')
    ], validators=[DataRequired()])
    certify_income = RadioField('I also certify that:', choices=[
        ('true', 'I understand that I may be asked to provide documentation of my income.')
    ], validators=[DataRequired()])
    submit = SubmitField('Apply for Fee Waiver', name='waiver_submit')

class WaiverReviewForm(FlaskForm):
    """Form for moderators to review fee waiver applications"""
    notes = TextAreaField('Review Notes (Optional)', validators=[Optional(), Length(max=1000)])
    waiver_percentage = SelectField('Fee Waiver Percentage', choices=[
        ('100', '100% - Full Fee Waiver (At or below 100% of poverty line)'),
        ('0', '0% - No Fee Waiver (Above 100% of poverty line)')
    ], validators=[DataRequired()])
    decision = RadioField('Decision', choices=[
        ('approve', 'Approve 100% Fee Waiver (Verified at/below poverty line)'),
        ('auto', 'Check Eligibility Based on Income (100% or 0%)'),
        ('deny', 'Deny Fee Waiver (Above poverty line)')
    ], validators=[DataRequired()])
    income_verified = BooleanField('Income Information Verified', default=False)
    request_documentation = BooleanField('Request Additional Documentation', default=False)
    submit = SubmitField('Submit Decision')
