"""DHCP Pool data model."""

from typing import Dict, Any, Optional
import ipaddress


class DhcpPool:
    """Model representing a DHCP pool/range configuration."""
    
    def __init__(
        self,
        pool_name: str,
        start_ip: str,
        end_ip: str,
        netmask: str,
        lease_duration: Optional[int] = None
    ) -> None:
        """Initialize DHCP pool with required fields.
        
        Args:
            pool_name: Name/tag identifier for the pool (e.g., 'intranet', 'iot')
            start_ip: Starting IP address of the pool range
            end_ip: Ending IP address of the pool range
            netmask: Subnet mask for the pool
            lease_duration: Lease duration in seconds (optional)
        """
        self.pool_name = pool_name
        self.start_ip = start_ip
        self.end_ip = end_ip
        self.netmask = netmask
        self.lease_duration = lease_duration
        
        # Calculate total addresses in the pool
        self.total_addresses = self._calculate_total_addresses()
    
    def _calculate_total_addresses(self) -> int:
        """Calculate total number of addresses in the pool range.
        
        Returns:
            Total number of IP addresses in the range
        """
        try:
            start = ipaddress.IPv4Address(self.start_ip)
            end = ipaddress.IPv4Address(self.end_ip)
            return int(end) - int(start) + 1
        except Exception:
            return 0
    
    def contains_ip(self, ip_address: str) -> bool:
        """Check if an IP address falls within this pool's range.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            True if IP address is within the pool range, False otherwise
        """
        try:
            ip = ipaddress.IPv4Address(ip_address)
            start = ipaddress.IPv4Address(self.start_ip)
            end = ipaddress.IPv4Address(self.end_ip)
            return start <= ip <= end
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pool object to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the pool
        """
        return {
            'pool_name': self.pool_name,
            'start_ip': self.start_ip,
            'end_ip': self.end_ip,
            'netmask': self.netmask,
            'lease_duration': self.lease_duration,
            'total_addresses': self.total_addresses
        }
    
    def __repr__(self) -> str:
        """String representation of the pool."""
        return f"DhcpPool(name='{self.pool_name}', range={self.start_ip}-{self.end_ip})"