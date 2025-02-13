from flask import Flask, jsonify
from flask_cors import CORS  # Import Flask-CORS
from .config import Config
from .extensions import db, redis_client
from .models.base import Base
from .api.routes import api_blueprint
from .services.rate_limit_service import init_rate_limiter
import logging
from .providers.provider_manager import ProviderManager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Initialize extensions
    db.init_app(app)
    redis_client.init_app(app)
    init_rate_limiter(app)

    # Enable CORS for all routes under /v1, allowing any origin.
    # This makes testing on different URLs (localhost, staging, production, etc.) easier.
    CORS(app, resources={r"/v1/*": {"origins": "*"}})

    provider_manager = ProviderManager()
    provider_manager.register_providers(app)
    app.provider_manager = provider_manager

    app.register_blueprint(api_blueprint, url_prefix='/v1')

    with app.app_context():
        if not app.config.get("DISABLE_AUTO_DB_INIT", False):
            try:
                Base.metadata.create_all(db.engine)
            except Exception as e:
                app.logger.error("Error during automatic table creation: %s", e)

    @app.route('/health')
    def health_check():
        return jsonify({"status": "OK"}), 200

    return app