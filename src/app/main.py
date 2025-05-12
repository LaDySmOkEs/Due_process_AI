from flask import Flask
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def home():
    return "Due Process AI is live!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
