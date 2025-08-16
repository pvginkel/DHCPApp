"""DHCP Service for reading and parsing DHCP lease files."""

import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from app.models.dhcp_lease import DhcpLease


class DhcpService:
    """Service for reading and parsing DHCP lease files."""
    
    def __init__(self, lease_file_path: str) -> None:
        """Initialize with lease file path from configuration.
        
        Args:
            lease_file_path: Path to the DHCP lease file
        """
        self.lease_file_path = lease_file_path
        self.logger = logging.getLogger(__name__)
    
    def get_all_leases(self) -> List[DhcpLease]:
        """Read lease file and return list of DhcpLease objects.
        
        Returns:
            List of parsed DHCP lease objects
            
        Raises:
            FileNotFoundError: If lease file does not exist
            PermissionError: If lease file cannot be read
            Exception: For other file access or parsing errors
        """
        self.logger.info(f"Reading DHCP lease file: {self.lease_file_path}")
        
        # Check if file exists
        lease_file = Path(self.lease_file_path)
        if not lease_file.exists():
            self.logger.error(f"DHCP lease file not found: {self.lease_file_path}")
            raise FileNotFoundError(f"DHCP lease file not found: {self.lease_file_path}")
        
        try:
            return self.parse_lease_file()
        except PermissionError as e:
            self.logger.error(f"Permission denied reading lease file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading lease file: {e}")
            raise
    
    def parse_lease_file(self) -> List[DhcpLease]:
        """Parse dnsmasq lease file format.
        
        The dnsmasq lease file format follows this structure per line:
        <expiration_timestamp> <mac_address> <ip_address> <hostname> <client_id>
        
        Where expiration_timestamp is a Unix timestamp indicating when the lease expires.
        A timestamp of 0 indicates a static lease that never expires.
        
        Returns:
            List of parsed DHCP lease objects
        """
        leases = []
        
        with open(self.lease_file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                try:
                    lease = self._parse_lease_line(line)
                    if lease:
                        leases.append(lease)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse lease line {line_num}: {line}. Error: {e}"
                    )
                    # Continue processing other lines even if one fails
                    continue
        
        self.logger.info(f"Successfully parsed {len(leases)} DHCP leases")
        return leases
    
    def _parse_lease_line(self, line: str) -> Optional[DhcpLease]:
        """Parse individual lease line into DhcpLease object.
        
        Args:
            line: Single line from the lease file
            
        Returns:
            DhcpLease object or None if parsing fails
        """
        parts = line.split()
        
        # dnsmasq lease format requires at least 4 parts
        if len(parts) < 4:
            self.logger.warning(f"Invalid lease line format: {line}")
            return None
        
        try:
            # Extract components
            timestamp_str = parts[0]
            mac_address = parts[1]
            ip_address = parts[2]
            hostname = parts[3]
            client_id = parts[4] if len(parts) > 4 else None
            
            # Convert Unix timestamp to datetime (expiration time)
            timestamp = int(timestamp_str)
            lease_time = datetime.fromtimestamp(timestamp)
            
            # Validate IP address format (basic check)
            self._validate_ip_address(ip_address)
            
            # Normalize MAC address format
            mac_address = self._normalize_mac_address(mac_address)
            
            return DhcpLease(
                ip_address=ip_address,
                mac_address=mac_address,
                hostname=hostname,
                lease_time=lease_time,
                client_id=client_id
            )
            
        except (ValueError, IndexError) as e:
            self.logger.warning(f"Error parsing lease line: {line}. Error: {e}")
            return None
    
    def _validate_ip_address(self, ip_address: str) -> None:
        """Validate IPv4 address format.
        
        Args:
            ip_address: IP address string to validate
            
        Raises:
            ValueError: If IP address format is invalid
        """
        parts = ip_address.split('.')
        if len(parts) != 4:
            raise ValueError(f"Invalid IP address format: {ip_address}")
        
        for part in parts:
            try:
                octet = int(part)
                if not 0 <= octet <= 255:
                    raise ValueError(f"Invalid IP address octet: {part}")
            except ValueError:
                raise ValueError(f"Invalid IP address format: {ip_address}")
    
    def _normalize_mac_address(self, mac_address: str) -> str:
        """Normalize MAC address format to lowercase with colons.
        
        Args:
            mac_address: MAC address in various formats
            
        Returns:
            Normalized MAC address in lowercase with colons
        """
        # Remove any existing separators and convert to lowercase
        mac_clean = mac_address.replace(':', '').replace('-', '').lower()
        
        # Validate length
        if len(mac_clean) != 12:
            raise ValueError(f"Invalid MAC address length: {mac_address}")
        
        # Add colons every two characters
        normalized = ':'.join(mac_clean[i:i+2] for i in range(0, 12, 2))
        
        return normalized
