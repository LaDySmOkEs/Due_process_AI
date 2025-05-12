from flask import Flask
import logging

# Initialize Flask app
app = Flask(__name__)

# Optional: Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Example route
@app.route("/")
def home():
    return "Due Process AI is live!"

# Run locally — Render uses gunicorn for deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
