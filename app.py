"""Main Flask application entry point."""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # This block only runs when the script is executed directly
    # Not when imported as a module
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    app.logger.info(f"Starting Flask application on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
