from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('cases.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('You have been logged in successfully!', 'success')
            return redirect(next_page or url_for('cases.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('cases.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Create demo users for testing (would be removed in production)
def create_demo_users():
    # Only create if no users exist
    if not User.get_user_by_email('user@example.com'):
        User.create_user('demouser', 'user@example.com', 'password', 'user')
        User.create_user('demolegal', 'legal@example.com', 'password', 'legal')
        User.create_user('demomod', 'mod@example.com', 'password', 'moderator')
        User.create_user('demopremium', 'premium@example.com', 'password', 'premium')
        
        # Create a test account specifically for brother
        User.create_user('tester', 'tester@test.com', 'testing123', 'premium')
