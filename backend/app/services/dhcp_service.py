"""DHCP Service for reading and parsing DHCP lease files."""

import logging
import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from pathlib import Path

from app.models.dhcp_lease import DhcpLease


class DhcpService:
    """Service for reading and parsing DHCP lease files."""
    
    def __init__(self, lease_file_path: str, config_folder_path: str) -> None:
        """Initialize with lease file path and config folder path from configuration.
        
        Args:
            lease_file_path: Path to the DHCP lease file
            config_folder_path: Path to the dnsmasq configuration folder
        """
        self.lease_file_path = lease_file_path
        self.config_folder_path = config_folder_path
        self.logger = logging.getLogger(__name__)
        self._static_leases_cache: Dict[str, Dict[str, str]] = {}
    
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
        
        # Check if static leases cache is populated, if not load it
        if not self._static_leases_cache:
            self._load_static_leases()
        
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
            
            # Determine if this is a static lease
            is_static = self._is_static_lease(mac_address, ip_address)
            
            return DhcpLease(
                ip_address=ip_address,
                mac_address=mac_address,
                hostname=hostname,
                lease_time=lease_time,
                client_id=client_id,
                is_static=is_static
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
    
    def _load_static_leases(self) -> None:
        """Load static lease configurations from dnsmasq config files.
        
        Reads all configuration files in the config folder following dnsmasq's 
        default filtering rules and extracts dhcp-host directives.
        """
        self.logger.info(f"Loading static leases from config folder: {self.config_folder_path}")
        
        # Initialize cache with mac_to_ip and ip_to_mac mappings
        self._static_leases_cache = {
            'mac_to_ip': {},
            'ip_to_mac': {}
        }
        
        config_folder = Path(self.config_folder_path)
        if not config_folder.exists():
            self.logger.warning(f"Config folder does not exist: {self.config_folder_path}")
            return
        
        if not config_folder.is_dir():
            self.logger.warning(f"Config path is not a directory: {self.config_folder_path}")
            return
        
        static_count = 0
        
        try:
            # Read all files in config folder following dnsmasq filtering rules
            for file_path in config_folder.iterdir():
                if not file_path.is_file():
                    continue
                
                filename = file_path.name
                
                # Apply dnsmasq's default filtering rules
                # Exclude files ending with ~ (backup files)
                if filename.endswith('~'):
                    continue
                
                # Exclude files starting with . (hidden files)
                if filename.startswith('.'):
                    continue
                
                # Exclude files both starting and ending with # (commented out)
                if filename.startswith('#') and filename.endswith('#'):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        for line_num, line in enumerate(file, 1):
                            line = line.strip()
                            
                            # Skip empty lines and comments
                            if not line or line.startswith('#'):
                                continue
                            
                            # Look for dhcp-host directives
                            if 'dhcp-host=' in line:
                                parsed_lease = self._parse_dhcp_host_line(line)
                                if parsed_lease:
                                    mac_address, ip_address = parsed_lease
                                    self._static_leases_cache['mac_to_ip'][mac_address] = ip_address
                                    self._static_leases_cache['ip_to_mac'][ip_address] = mac_address
                                    static_count += 1
                                    
                except Exception as e:
                    self.logger.warning(f"Error reading config file {file_path}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error accessing config folder {self.config_folder_path}: {e}")
            return
        
        self.logger.info(f"Loaded {static_count} static lease configurations")
    
    def _parse_dhcp_host_line(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse dhcp-host configuration line to extract MAC and IP address.
        
        Args:
            line: Configuration line containing dhcp-host directive
            
        Returns:
            Tuple of (normalized_mac_address, ip_address) or None if parsing fails
        """
        try:
            # Find dhcp-host= directive
            dhcp_host_match = re.search(r'dhcp-host=([^#\s]+)', line)
            if not dhcp_host_match:
                return None
            
            # Extract content after dhcp-host=
            dhcp_host_content = dhcp_host_match.group(1)
            
            # Split by commas to get components
            components = [comp.strip() for comp in dhcp_host_content.split(',')]
            
            mac_address = None
            ip_address = None
            
            # Identify MAC address and IP address components
            for component in components:
                # Check if component is a MAC address (xx:xx:xx:xx:xx:xx or xx-xx-xx-xx-xx-xx)
                if re.match(r'^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$', component):
                    mac_address = self._normalize_mac_address(component)
                
                # Check if component is an IP address (xxx.xxx.xxx.xxx)
                elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', component):
                    # Basic IP validation
                    parts = component.split('.')
                    if all(0 <= int(part) <= 255 for part in parts):
                        ip_address = component
            
            # Return tuple if both MAC and IP were found
            if mac_address and ip_address:
                return (mac_address, ip_address)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error parsing dhcp-host line: {line}. Error: {e}")
            return None
    
    def _is_static_lease(self, mac_address: str, ip_address: str) -> bool:
        """Check if a lease matches static configuration.
        
        Args:
            mac_address: MAC address of the lease (normalized)
            ip_address: IP address of the lease
            
        Returns:
            True if lease matches static configuration, False otherwise
        """
        # Check if MAC address exists in static leases cache
        if mac_address in self._static_leases_cache.get('mac_to_ip', {}):
            expected_ip = self._static_leases_cache['mac_to_ip'][mac_address]
            # Cross-validate that MAC and IP pair match expected static assignment
            if expected_ip == ip_address:
                return True
        
        # Check if IP address exists in static leases cache
        if ip_address in self._static_leases_cache.get('ip_to_mac', {}):
            expected_mac = self._static_leases_cache['ip_to_mac'][ip_address]
            # Cross-validate that MAC and IP pair match expected static assignment
            if expected_mac == mac_address:
                return True
        
        return False
