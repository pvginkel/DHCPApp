"""Tests for DhcpService."""

import logging
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


class TestStaticLeaseParsing:
    """Reservations, in both shapes dnsmasq accepts them.

    `dhcp-host=` lines live in the config files themselves; a `dhcp-hostsfile=`
    names a file whose lines are the same value with the directive left off.
    dnsmasq-config-generator writes the latter, so it is what production has.
    """

    LEASES = (
        "1755747132 20:43:a8:ee:1c:4b 10.1.0.30 coordinator *\n"
        "1755770757 28:00:af:c8:47:2b 10.1.1.27 IDH10018 01:28:00:af:c8:47:2b\n"
    )
    RESERVATION = "set:intranet,id:*,20:43:a8:ee:1c:4b,10.1.0.30,coordinator.home"

    @pytest.fixture
    def mock_mac_vendor(self) -> MacVendorService:
        mock = Mock(spec=MacVendorService)
        mock.get_vendor.return_value = None
        return mock

    def build_service(
        self, root: Path, mac_vendor: MacVendorService, main_config: str, files: dict[str, str]
    ) -> DhcpService:
        """Write a dnsmasq tree under root and point a service at it."""
        (root / "dnsmasq.leases").write_text(self.LEASES)
        (root / "dnsmasq.conf").write_text(main_config)
        for relative_path, content in files.items():
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

        app_settings = AppSettings(
            dnsmasq_config_file_path="/dnsmasq.conf",
            root_path=str(root),
            update_mac_vendor_database=False,
            dev_fake_lease_changes=False,
        )
        return DhcpService(app_settings, mac_vendor)

    def static_ips(self, service: DhcpService) -> set[str]:
        return {lease.ip_address for lease in service.get_all_leases() if lease.is_static}

    def test_hostsfile_from_main_config(self, tmp_path, mock_mac_vendor) -> None:
        service = self.build_service(
            tmp_path,
            mock_mac_vendor,
            "dhcp-leasefile=/dnsmasq.leases\ndhcp-hostsfile=/static.d/dhcp-hosts\n",
            {"static.d/dhcp-hosts": f"{self.RESERVATION}\n"},
        )
        assert self.static_ips(service) == {"10.1.0.30"}

    def test_hostsfile_from_included_config(self, tmp_path, mock_mac_vendor) -> None:
        service = self.build_service(
            tmp_path,
            mock_mac_vendor,
            "dhcp-leasefile=/dnsmasq.leases\nconf-dir=/dnsmasq.d/,*.conf\n",
            {
                "dnsmasq.d/10-dhcp.conf": "dhcp-hostsfile=/static.d/dhcp-hosts\n",
                "static.d/dhcp-hosts": f"{self.RESERVATION}\n",
            },
        )
        assert self.static_ips(service) == {"10.1.0.30"}

    def test_hostsfile_comments_and_blank_lines(self, tmp_path, mock_mac_vendor) -> None:
        service = self.build_service(
            tmp_path,
            mock_mac_vendor,
            "dhcp-leasefile=/dnsmasq.leases\ndhcp-hostsfile=/static.d/dhcp-hosts\n",
            {
                "static.d/dhcp-hosts": (
                    "# Automatically generated file.\n"
                    "\n"
                    f"{self.RESERVATION} # the Zigbee coordinator\n"
                ),
            },
        )
        assert self.static_ips(service) == {"10.1.0.30"}

    def test_missing_hostsfile_is_not_silent(self, tmp_path, mock_mac_vendor, caplog) -> None:
        """A named but absent hostsfile errors; it does not read as zero reservations."""
        with caplog.at_level(logging.ERROR):
            service = self.build_service(
                tmp_path,
                mock_mac_vendor,
                "dhcp-leasefile=/dnsmasq.leases\ndhcp-hostsfile=/static.d/dhcp-hosts\n",
                {},
            )

        assert service.get_all_leases() == []
        assert "dhcp-hosts" in caplog.text

    def test_hostsfile_appearing_later_is_picked_up(self, tmp_path, mock_mac_vendor) -> None:
        """The sidecar that renders the hostsfile may not have run yet.

        A failed load must not leave the cache looking loaded, or the
        reservations stay missing for the life of the process.
        """
        service = self.build_service(
            tmp_path,
            mock_mac_vendor,
            "dhcp-leasefile=/dnsmasq.leases\ndhcp-hostsfile=/static.d/dhcp-hosts\n",
            {},
        )
        assert service.get_all_leases() == []

        hostsfile = tmp_path / "static.d" / "dhcp-hosts"
        hostsfile.parent.mkdir(parents=True, exist_ok=True)
        hostsfile.write_text(f"{self.RESERVATION}\n")

        service.reload_lease_cache()
        assert self.static_ips(service) == {"10.1.0.30"}

    def test_dhcp_host_directive(self, tmp_path, mock_mac_vendor) -> None:
        service = self.build_service(
            tmp_path,
            mock_mac_vendor,
            "dhcp-leasefile=/dnsmasq.leases\nconf-dir=/dnsmasq.d/,*.conf\n",
            {"dnsmasq.d/20-hosts.conf": f"dhcp-host={self.RESERVATION}\n"},
        )
        assert self.static_ips(service) == {"10.1.0.30"}

    def test_entry_without_address_is_no_reservation(self, tmp_path, mock_mac_vendor) -> None:
        service = self.build_service(
            tmp_path,
            mock_mac_vendor,
            "dhcp-leasefile=/dnsmasq.leases\ndhcp-hostsfile=/static.d/dhcp-hosts\n",
            {"static.d/dhcp-hosts": "set:intranet,20:43:a8:ee:1c:4b\n"},
        )
        assert self.static_ips(service) == set()

    def test_sample_tree_reservations_reach_the_leases(self, mock_mac_vendor) -> None:
        """The shipped sample tree is in production's format, so it must classify.

        Two hostsfiles, as the deployed pod has: the static set rendered from
        the operator's own list, and the dynamic set the management API owns.
        """
        test_data_dir = Path(__file__).parent / "data"
        app_settings = AppSettings(
            dnsmasq_config_file_path="/data/dnsmasq.conf",
            root_path=str(test_data_dir.parent),
            update_mac_vendor_database=False,
            dev_fake_lease_changes=False,
        )
        service = DhcpService(app_settings, mock_mac_vendor)
        assert self.static_ips(service) == {"10.1.0.30", "10.1.1.97"}
