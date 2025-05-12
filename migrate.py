from flask_migrate import Migrate, upgrade, init, migrate as make_migrations
from app import app, db
from models import User, Case, Evidence, Document, LegalAnalysis

# Create the Flask-Migrate instance
migrate = Migrate(app, db)

if __name__ == '__main__':
    print("Running database migrations...")
    with app.app_context():
        # Initialize migrations
        try:
            init()
            print("Migration directory initialized")
        except:
            print("Migration directory already exists")

        # Create migration
        try:
            make_migrations(message="Initial migration")
            print("Created migration")
            
            # Apply migrations
            upgrade()
            print("Applied migrations")
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            raise e