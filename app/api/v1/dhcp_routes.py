"""DHCP API routes for v1."""

import logging
from flask import jsonify, current_app
from app.api.v1 import api_v1_bp
from app.services.dhcp_service import DhcpService
from app.utils import ResponseHelper

# Set up logging
logger = logging.getLogger(__name__)


@api_v1_bp.route('/leases', methods=['GET'])
def get_dhcp_leases():
    """Get all DHCP lease information.
    
    Returns:
        JSON response with array of DHCP lease objects or error information
    """
    logger.info("DHCP leases endpoint accessed")
    
    try:
        # Use shared DHCP service instance from app context
        dhcp_service = current_app.dhcp_service
        logger.debug(f"Using shared DHCP service instance")
        
        # Get all leases
        leases = dhcp_service.get_all_leases()
        
        # Convert leases to dictionary format for JSON serialization
        lease_data = [lease.to_dict() for lease in leases]
        
        logger.info(f"Successfully retrieved {len(lease_data)} DHCP leases")
        return jsonify(ResponseHelper.success_response(lease_data))
        
    except FileNotFoundError as e:
        logger.error(f"DHCP lease file not found: {e}")
        return jsonify(ResponseHelper.error_response(
            "Unable to read DHCP lease file",
            str(e)
        )), 500
        
    except PermissionError as e:
        logger.error(f"Permission denied accessing DHCP lease file: {e}")
        return jsonify(ResponseHelper.error_response(
            "Permission denied accessing DHCP lease file",
            str(e)
        )), 500
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving DHCP leases: {e}")
        return jsonify(ResponseHelper.error_response(
            "Internal server error while retrieving DHCP leases",
            str(e)
        )), 500
