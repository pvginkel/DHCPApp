"""DHCP API blueprint."""

import logging
from typing import Any

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify

from app.services.container import ServiceContainer
from app.services.dhcp_service import DhcpService

logger = logging.getLogger(__name__)

dhcp_bp = Blueprint("dhcp", __name__, url_prefix="/dhcp")


@dhcp_bp.route("/leases", methods=["GET"])
@inject
def get_leases(
    dhcp_service: DhcpService = Provide[ServiceContainer.dhcp_service],
) -> Any:
    """Get all DHCP leases."""
    leases = dhcp_service.get_all_leases()
    return jsonify([lease.to_dict() for lease in leases])


@dhcp_bp.route("/pools", methods=["GET"])
@inject
def get_pools(
    dhcp_service: DhcpService = Provide[ServiceContainer.dhcp_service],
) -> Any:
    """Get all DHCP pools."""
    pools = dhcp_service.get_dns_pools()
    return jsonify([pool.to_dict() for pool in pools])


@dhcp_bp.route("/pools/usage", methods=["GET"])
@inject
def get_pool_usage(
    dhcp_service: DhcpService = Provide[ServiceContainer.dhcp_service],
) -> Any:
    """Get DHCP pool usage statistics."""
    stats = dhcp_service.get_pool_usage_statistics()
    return jsonify(stats)
