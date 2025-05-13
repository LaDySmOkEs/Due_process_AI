from flask import Flask, render_template
import logging

def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Register routes
    @app.route("/")
    def home():
        return render_template("home.html")

    return app
