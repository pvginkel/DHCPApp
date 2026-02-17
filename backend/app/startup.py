"""App-specific startup hooks for DHCP monitoring.

Hook points called by create_app():
  - create_container()
  - register_blueprints()
  - register_root_blueprints()
  - register_error_handlers()

Hook points called by CLI command handlers:
  - register_cli_commands()
  - post_migration_hook()
  - load_test_data_hook()
"""

from __future__ import annotations

import click
from flask import Blueprint, Flask

from app.services.container import ServiceContainer


def create_container() -> ServiceContainer:
    """Create and configure the application's service container."""
    return ServiceContainer()


def register_blueprints(api_bp: Blueprint, app: Flask) -> None:
    """Register all app-specific blueprints."""
    # Register DHCP endpoints under /api/dhcp (OIDC-protected via api_bp)
    if not api_bp._got_registered_once:  # type: ignore[attr-defined]
        from app.api.dhcp import dhcp_bp

        api_bp.register_blueprint(dhcp_bp)


def register_root_blueprints(app: Flask) -> None:
    """Register app-specific blueprints directly on the app (not under /api prefix)."""
    from app.api.internal import internal_bp

    app.register_blueprint(internal_bp)


def register_error_handlers(app: Flask) -> None:
    """Register app-specific error handlers."""
    pass


def register_cli_commands(cli: click.Group) -> None:
    """Register app-specific CLI commands."""
    pass


def post_migration_hook(app: Flask) -> None:
    """Run after database migrations (e.g., sync master data)."""
    pass


def load_test_data_hook(app: Flask) -> None:
    """Load test fixtures after database recreation."""
    pass
