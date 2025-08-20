"""Flask application factory."""

import logging
from typing import Optional
from flask import Flask
from flask_cors import CORS
from config import get_config
from app.services.dhcp_service import DhcpService
from app.services.sse_service import SseService
from app.services.mac_vendor_service import MacVendorService
from app.api.openapi import OpenApiGenerator


class DHCPApp(Flask):
    """Extended Flask app with typed service attributes."""
    
    sse_service: SseService
    dhcp_service: DhcpService
    mac_vendor_service: MacVendorService
    openapi_generator: OpenApiGenerator


def create_app(config_name: Optional[str] = None) -> DHCPApp:
    """Application factory function to create Flask app instance.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = DHCPApp(__name__)
    
    # Load configuration
    config_instance = get_config()
    app.config.from_object(config_instance)
    
    # Set up CORS for future SPA integration
    CORS(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    mac_vendor_service = MacVendorService(
        update_database=app.config.get('UPDATE_MAC_VENDOR_DATABASE', True)
    )
    dhcp_service = DhcpService(
        app.config['DNSMASQ_CONFIG_FILE_PATH'],
        mac_vendor_service=mac_vendor_service
    )
    sse_service = SseService(dhcp_service)
    openapi_generator = OpenApiGenerator()
    
    # Store services in app context for access across modules
    app.sse_service = sse_service
    app.dhcp_service = dhcp_service
    app.mac_vendor_service = mac_vendor_service
    app.openapi_generator = openapi_generator
    
    # Register blueprints
    from app.api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f'Internal server error: {error}')
        return {'error': 'Internal server error'}, 500
    
    return app
