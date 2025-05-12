#!/usr/bin/env python
"""
Script to create an admin user with specified email and password
"""

from app import app, db
from models import User, ROLE_MOD

def create_admin_user(email, username, password):
    """Create an admin user with moderator privileges"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.get_user_by_email(email)
        if existing_user:
            print(f"User with email {email} already exists.")
            
            # Update the user's role to moderator if not already
            if not existing_user.is_moderator():
                existing_user.role = ROLE_MOD
                db.session.commit()
                print(f"Updated user {email} to moderator role.")
            else:
                print(f"User {email} is already a moderator.")
            
            return existing_user
        
        # Create new admin user
        admin_user = User.create_user(
            username=username,
            email=email,
            password=password,
            role=ROLE_MOD
        )
        
        print(f"Created new admin user with email {email}")
        return admin_user

if __name__ == "__main__":
    # Create admin user with the specified email and password
    admin_email = "panterailovephil@gmail.com"
    admin_username = "admin"
    admin_password = "DanielOwen2023!"
    
    create_admin_user(admin_email, admin_username, admin_password)