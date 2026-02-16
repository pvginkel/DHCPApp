"""DHCP Pool data model."""

import ipaddress
from typing import Any


class DhcpPool:
    """Model representing a DHCP pool/range configuration."""

    def __init__(
        self,
        pool_name: str,
        start_ip: str,
        end_ip: str,
        netmask: str,
        lease_duration: int | None = None,
    ) -> None:
        self.pool_name = pool_name
        self.start_ip = start_ip
        self.end_ip = end_ip
        self.netmask = netmask
        self.lease_duration = lease_duration
        self.total_addresses = self._calculate_total_addresses()

    def _calculate_total_addresses(self) -> int:
        """Calculate total number of addresses in the pool range."""
        try:
            start = ipaddress.IPv4Address(self.start_ip)
            end = ipaddress.IPv4Address(self.end_ip)
            return int(end) - int(start) + 1
        except Exception:
            return 0

    def contains_ip(self, ip_address: str) -> bool:
        """Check if an IP address falls within this pool's range."""
        try:
            ip = ipaddress.IPv4Address(ip_address)
            start = ipaddress.IPv4Address(self.start_ip)
            end = ipaddress.IPv4Address(self.end_ip)
            return start <= ip <= end
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        """Convert pool object to dictionary for JSON serialization."""
        return {
            "pool_name": self.pool_name,
            "start_ip": self.start_ip,
            "end_ip": self.end_ip,
            "netmask": self.netmask,
            "lease_duration": self.lease_duration,
            "total_addresses": self.total_addresses,
        }

    def __repr__(self) -> str:
        return f"DhcpPool(name='{self.pool_name}', range={self.start_ip}-{self.end_ip})"
