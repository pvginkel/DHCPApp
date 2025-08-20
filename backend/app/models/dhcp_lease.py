"""DHCP Lease data model."""

from datetime import datetime
from typing import Dict, Any, Optional


class DhcpLease:
    """Model representing a single DHCP lease entry."""
    
    def __init__(
        self,
        ip_address: str,
        mac_address: str,
        hostname: str,
        lease_time: datetime,
        client_id: Optional[str] = None,
        is_static: bool = False,
        pool_name: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> None:
        """Initialize DHCP lease with required fields.
        
        Args:
            ip_address: IPv4 address assigned to the client
            mac_address: MAC address of the client device
            hostname: Hostname of the client (may be '*' if unknown)
            lease_time: Lease expiration time (Unix timestamp converted to datetime)
            client_id: Optional client identifier
            is_static: Whether this lease is a static assignment (from dhcp-host config)
            pool_name: Name of the DHCP pool this lease belongs to
            vendor: Vendor/manufacturer name from MAC address lookup
        """
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.hostname = hostname
        self.lease_time = lease_time
        self.client_id = client_id
        self.is_static = is_static
        self.pool_name = pool_name
        self.vendor = vendor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lease object to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the lease
        """
        return {
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname if self.hostname != '*' else None,
            'lease_time': self.lease_time.isoformat() + 'Z',
            'client_id': self.client_id if self.client_id != '*' else None,
            'is_active': self.is_active(),
            'is_static': self.is_static,
            'pool_name': self.pool_name,
            'vendor': self.vendor
        }
    
    def is_active(self) -> bool:
        """Determine if lease is currently active based on timestamp.
        
        For dnsmasq leases, the timestamp represents when the lease expires.
        A lease is considered active if:
        1. The current time is before the lease expiration time
        2. The lease expiration time is not 0 (which indicates a static lease)
        
        Returns:
            True if lease is considered active, False if expired
        """
        # Get current time for comparison
        current_time = datetime.now()
        
        # Check if this is a static lease (timestamp 0 means never expires)
        # Static leases are always considered active
        if self.lease_time.timestamp() == 0:
            return True
        
        # For regular leases, check if current time is before expiration
        return current_time < self.lease_time
