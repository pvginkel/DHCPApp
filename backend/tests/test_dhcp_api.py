"""Tests for DHCP API endpoints."""

from flask.testing import FlaskClient


class TestDhcpLeases:
    """Tests for GET /api/dhcp/leases."""

    def test_list_leases(self, client: FlaskClient) -> None:
        response = client.get("/api/dhcp/leases")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_lease_structure(self, client: FlaskClient) -> None:
        response = client.get("/api/dhcp/leases")
        data = response.get_json()
        for lease in data:
            assert "ip_address" in lease
            assert "mac_address" in lease
            assert "hostname" in lease
            assert "lease_time" in lease
            assert "is_active" in lease
            assert "is_static" in lease
            assert "pool_name" in lease
            assert "vendor" in lease


class TestDhcpPools:
    """Tests for GET /api/dhcp/pools."""

    def test_list_pools(self, client: FlaskClient) -> None:
        response = client.get("/api/dhcp/pools")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_pool_structure(self, client: FlaskClient) -> None:
        response = client.get("/api/dhcp/pools")
        data = response.get_json()
        for pool in data:
            assert "pool_name" in pool
            assert "start_ip" in pool
            assert "end_ip" in pool
            assert "netmask" in pool
            assert "total_addresses" in pool


class TestPoolUsage:
    """Tests for GET /api/dhcp/pools/usage."""

    def test_pool_usage(self, client: FlaskClient) -> None:
        response = client.get("/api/dhcp/pools/usage")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_usage_fields(self, client: FlaskClient) -> None:
        response = client.get("/api/dhcp/pools/usage")
        data = response.get_json()
        for stat in data:
            assert "used_addresses" in stat
            assert "available_addresses" in stat
            assert "usage_percentage" in stat
            assert 0 <= stat["usage_percentage"] <= 100
            assert stat["used_addresses"] + stat["available_addresses"] == stat["total_addresses"]
