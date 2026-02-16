"""Tests for DhcpService."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from app.app_config import AppSettings
from app.models.dhcp_pool import DhcpPool
from app.services.dhcp_service import DhcpService
from app.services.mac_vendor_service import MacVendorService


class TestDhcpService:
    """Test cases for DhcpService class."""

    @pytest.fixture
    def test_data_dir(self) -> Path:
        return Path(__file__).parent / "data"

    @pytest.fixture
    def app_settings(self, test_data_dir: Path) -> AppSettings:
        return AppSettings(
            dnsmasq_config_file_path="/data/dnsmasq.conf",
            root_path=str(test_data_dir.parent),
            update_mac_vendor_database=False,
            dev_fake_lease_changes=False,
        )

    @pytest.fixture
    def mock_mac_vendor(self) -> MacVendorService:
        mock = Mock(spec=MacVendorService)
        mock.get_vendor.return_value = None
        return mock

    @pytest.fixture
    def service(self, app_settings, mock_mac_vendor):
        return DhcpService(app_settings, mock_mac_vendor)

    def test_parse_config(self, service) -> None:
        assert service.lease_file_path is not None
        assert len(service.config_directories) > 0

    def test_discover_pools(self, service) -> None:
        pools = service.get_dns_pools()
        assert len(pools) > 0
        for pool in pools:
            assert isinstance(pool, DhcpPool)
            assert pool.total_addresses > 0

    def test_get_leases(self, service) -> None:
        leases = service.get_all_leases()
        assert isinstance(leases, list)
        assert len(leases) > 0

    def test_lease_fields(self, service) -> None:
        leases = service.get_all_leases()
        for lease in leases:
            assert lease.ip_address
            assert lease.mac_address
            assert lease.lease_time is not None

    def test_pool_usage_statistics(self, service) -> None:
        stats = service.get_pool_usage_statistics()
        pools = service.get_dns_pools()
        assert len(stats) == len(pools)
        for stat in stats:
            assert stat["used_addresses"] + stat["available_addresses"] == stat["total_addresses"]

    def test_with_vendor_lookup(self, app_settings) -> None:
        mock_vendor = Mock(spec=MacVendorService)
        mock_vendor.get_vendor.return_value = "Apple, Inc."
        service = DhcpService(app_settings, mock_vendor)
        leases = service.get_all_leases()
        if leases:
            assert mock_vendor.get_vendor.call_count > 0

    def test_reload_lease_cache(self, service) -> None:
        initial_count = len(service.get_all_leases())
        service.reload_lease_cache()
        assert len(service.get_all_leases()) == initial_count

    def test_update_lease_cache(self, service) -> None:
        service.update_lease_cache([])
        assert len(service.get_all_leases()) == 0
        service.reload_lease_cache()
        assert len(service.get_all_leases()) > 0


class TestDhcpPool:
    """Test DhcpPool model."""

    def test_total_addresses(self) -> None:
        pool = DhcpPool("test", "192.168.1.10", "192.168.1.20", "255.255.255.0", 86400)
        assert pool.total_addresses == 11

    def test_contains_ip(self) -> None:
        pool = DhcpPool("test", "192.168.1.10", "192.168.1.20", "255.255.255.0")
        assert pool.contains_ip("192.168.1.15")
        assert pool.contains_ip("192.168.1.10")
        assert pool.contains_ip("192.168.1.20")
        assert not pool.contains_ip("192.168.1.9")
        assert not pool.contains_ip("192.168.1.21")

    def test_to_dict(self) -> None:
        pool = DhcpPool("test", "192.168.1.10", "192.168.1.20", "255.255.255.0", 86400)
        d = pool.to_dict()
        assert d["pool_name"] == "test"
        assert d["total_addresses"] == 11
        assert d["lease_duration"] == 86400
