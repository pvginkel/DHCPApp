"""Internal endpoints for companion container notifications."""

import logging
from datetime import UTC, datetime

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify

from app.app_config import AppSettings
from app.services.container import ServiceContainer
from app.services.dev_lease_modifier import DevLeaseModifier
from app.services.dhcp_service import DhcpService
from app.services.sse_connection_manager import SSEConnectionManager

logger = logging.getLogger(__name__)

internal_bp = Blueprint("internal", __name__)

# Lazy-initialized DevLeaseModifier for dev mode
_dev_lease_modifier: DevLeaseModifier | None = None


@internal_bp.route("/internal/notify-lease-change", methods=["POST"])
@inject
def notify_lease_change(
    dhcp_service: DhcpService = Provide[ServiceContainer.dhcp_service],
    sse_connection_manager: SSEConnectionManager = Provide[ServiceContainer.sse_connection_manager],
    app_settings: AppSettings = Provide[ServiceContainer.app_config],
) -> tuple:
    """Internal notification endpoint for lease file changes.

    Called by companion containers when dnsmasq lease file changes.
    Reloads lease cache and broadcasts data_changed to all SSE clients.
    """
    logger.info("Received lease change notification from companion container")

    if app_settings.dev_fake_lease_changes:
        _apply_fake_changes(dhcp_service)
    else:
        dhcp_service.reload_lease_cache()

    # Broadcast data_changed event via SSE Gateway
    event_data = {
        "event_type": "data_changed",
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    sse_connection_manager.send_event(None, event_data, "data_changed", "dhcp")

    return jsonify({
        "status": "success",
        "message": "Lease change notification processed successfully",
    }), 200


def _apply_fake_changes(dhcp_service: DhcpService) -> None:
    """Apply fake lease modifications for development mode."""
    global _dev_lease_modifier
    if _dev_lease_modifier is None:
        _dev_lease_modifier = DevLeaseModifier(dhcp_service.dhcp_pools)

    current_leases = dhcp_service.get_all_leases()
    modified_leases = _dev_lease_modifier.modify_leases(current_leases)
    dhcp_service.update_lease_cache(modified_leases)
    logger.info(f"Applied fake changes to cache: {len(modified_leases)} leases")
