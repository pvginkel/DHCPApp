"""Flask application entry point for both development and production."""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    # Determine if we're in development mode
    is_dev = app.config.get('FLASK_ENV') == 'development' or debug
    
    # Log startup information
    mode = "development" if is_dev else "production"
    app.logger.info(f"Starting Flask application in {mode} mode on http://{host}:{port}")
    if is_dev:
        app.logger.info(f"Debug mode: {debug}")
    
    # Run with appropriate settings for environment
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=is_dev,
        threaded=True
    )
