from flask import Flask, render_template
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
