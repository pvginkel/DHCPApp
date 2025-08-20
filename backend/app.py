"""Flask application entry point for both development and production."""

import os
from dotenv import load_dotenv
from app import create_app
from waitress import serve

# Load environment variables from .env file
load_dotenv(".env")        # load defaults
load_dotenv(".env.local")  # override

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
        # Development: Use Flask's built-in server with hot reload
        app.logger.info("Using Flask development server with hot reload")
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=True,
            threaded=True
        )
    else:
        # Production: Use Waitress WSGI server
        app.logger.info("Using Waitress WSGI server for production")
        serve(app, host=host, port=port, threads=20)
