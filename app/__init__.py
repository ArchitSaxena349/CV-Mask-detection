import os
from flask import Flask
from config import config
from core.logger import setup_logging
from core.validators import validate_config

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Validate configuration
    try:
        validate_config(app.config)
    except Exception as e:
        app.logger.warning(f"Configuration validation warning: {e}")
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    from app.main import main_bp
    from app.errors import errors_bp
    from app.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(api_bp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
