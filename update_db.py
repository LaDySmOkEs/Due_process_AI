from app import app, db
import models

# Run database update to create new columns
with app.app_context():
    db.create_all()
    print("Database schema updated successfully!")