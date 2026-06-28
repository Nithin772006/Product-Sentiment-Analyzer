from flask import Flask
from flask_cors import CORS

from config import Config
from routes.api_routes import api_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS allows the React frontend to call the Flask API during development.
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    app.register_blueprint(api_bp, url_prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":
    # Local development entry point. Production servers should import `app`.
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
    )
