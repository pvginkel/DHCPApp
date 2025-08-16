"""API v1 package initialization."""

from flask import Blueprint

# Create API v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__)

# Import routes to register them with the blueprint
from app.api.v1 import routes
from app.api.v1 import dhcp_routes
