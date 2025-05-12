import os
import sys
import subprocess
from app import app, db
import models

# Set required environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

print("Attempting to fix database connection and apply schema updates...")

try:
    # First, try to end any idle transactions
    subprocess.run(["python", "reset_db_connection.py"], check=True)
    
    # Apply schema updates within the application context
    with app.app_context():
        # Create all tables defined in the models
        db.create_all()
        print("Database schema updated successfully!")
    
    print("Migration completed successfully!")
    
except Exception as e:
    print(f"Error during migration: {e}")
    sys.exit(1)