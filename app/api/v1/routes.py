"""Basic API routes for v1."""

import logging
from flask import jsonify
from app.api.v1 import api_v1_bp
from app.utils import ResponseHelper

# Set up logging
logger = logging.getLogger(__name__)


@api_v1_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint.
    
    Returns:
        JSON response indicating service health
    """
    logger.info("Health check endpoint accessed")
    return jsonify(ResponseHelper.success_response(
        {'status': 'healthy', 'service': 'DHCP Backend API'}
    ))


@api_v1_bp.route('/status', methods=['GET'])
def status():
    """Basic status endpoint.
    
    Returns:
        JSON response with service status information
    """
    logger.info("Status endpoint accessed")
    return jsonify(ResponseHelper.success_response({
        'version': '1.0.0',
        'api_version': 'v1',
        'description': 'DHCP Network Management API'
    }))
