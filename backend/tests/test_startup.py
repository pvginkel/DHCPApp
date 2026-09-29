"""Tests for the services started before the server binds."""

from unittest.mock import Mock

from dependency_injector import providers

from app.services.container import start_background_services


def test_background_startup_builds_dhcp_service(container) -> None:
    """The lease cache is loaded at startup, not by the first request."""
    dhcp_service_factory = Mock()
    container.dhcp_service.override(providers.Singleton(dhcp_service_factory))

    try:
        start_background_services(container)
    finally:
        container.dhcp_service.reset_override()

    dhcp_service_factory.assert_called_once()
