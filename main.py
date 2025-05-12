import os
import logging
from app import app

# Set up logging for easier debugging
logging.basicConfig(level=logging.DEBUG)

# Remove direct blueprint registrations from main.py since they are already in app.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
