"""Pytest configuration and fixtures.

Infrastructure fixtures (app, client, OIDC, SSE) are defined in
conftest_infrastructure.py. This file re-exports them and adds app-specific
domain fixtures.
"""

from pathlib import Path

import pytest

from app.app_config import AppSettings

# Import all infrastructure fixtures
from tests.conftest_infrastructure import *  # noqa: F401, F403


@pytest.fixture
def test_app_settings() -> AppSettings:
    """Override infrastructure test_app_settings with DHCP-specific config.

    Points dnsmasq config at the test data directory.
    """
    test_dir = Path(__file__).parent
    return AppSettings(
        dnsmasq_config_file_path="/data/dnsmasq.conf",
        root_path=str(test_dir),
        update_mac_vendor_database=False,
        dev_fake_lease_changes=False,
    )
