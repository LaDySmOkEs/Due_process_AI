import os
import logging
from flask import Flask

# Initialize Flask app
app = Flask(__name__)

# Optional: Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define routes
@app.route('/')
def home():
    return "Due Process AI is running!"

# Run the app for local development (Render uses gunicorn for production)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
