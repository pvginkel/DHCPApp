"""DHCP Lease data model."""

from datetime import datetime
from typing import Any


class DhcpLease:
    """Model representing a single DHCP lease entry."""

    def __init__(
        self,
        ip_address: str,
        mac_address: str,
        hostname: str,
        lease_time: datetime,
        client_id: str | None = None,
        is_static: bool = False,
        pool_name: str | None = None,
        vendor: str | None = None,
    ) -> None:
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.hostname = hostname
        self.lease_time = lease_time
        self.client_id = client_id
        self.is_static = is_static
        self.pool_name = pool_name
        self.vendor = vendor

    def to_dict(self) -> dict[str, Any]:
        """Convert lease object to dictionary for JSON serialization."""
        return {
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "hostname": self.hostname if self.hostname != "*" else None,
            "lease_time": self.lease_time.isoformat() + "Z",
            "client_id": self.client_id if self.client_id != "*" else None,
            "is_active": self.is_active(),
            "is_static": self.is_static,
            "pool_name": self.pool_name,
            "vendor": self.vendor,
        }

    def is_active(self) -> bool:
        """Determine if lease is currently active.

        Static leases (timestamp 0) are always active.
        Regular leases are active if current time is before expiration.
        """
        if self.lease_time.timestamp() == 0:
            return True
        return datetime.now() < self.lease_time
