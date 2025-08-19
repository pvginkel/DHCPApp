"""DHCP Service for reading and parsing DHCP lease files."""

import logging
import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from flask import current_app

from app.models.dhcp_lease import DhcpLease
from app.models.dhcp_pool import DhcpPool


class DhcpService:
    """Service for reading and parsing DHCP lease files and configuration."""
    
    def __init__(self, config_file_path: str) -> None:
        """Initialize with main dnsmasq configuration file path.
        
        Args:
            config_file_path: Path to the main dnsmasq configuration file
        """
        self.config_file_path = config_file_path
        self.logger = logging.getLogger(__name__)
        
        # Configuration discovery results
        self.lease_file_path: Optional[str] = None
        self.config_directories: List[Tuple[str, str]] = []  # (directory, extension_pattern)
        self.config_files: List[str] = []
        self.dhcp_pools: List[DhcpPool] = []
        
        # Cache for static leases
        self._static_leases_cache: Dict[str, Dict[str, str]] = {}
        
        # Main lease cache
        self._lease_cache: Optional[List[DhcpLease]] = None
        
        # Parse main configuration on initialization
        self._parse_main_config()
        self._discover_config_files()
        self._parse_dhcp_ranges()
        
        # Load initial lease cache
        self._load_lease_cache()
    
    def _resolve_path(self, path: str) -> str:
        """Resolve path with ROOT_PATH prefix.
        
        Args:
            path: Original path
            
        Returns:
            Path prefixed with ROOT_PATH
        """
        try:
            root_path = current_app.config.get('ROOT_PATH', '')
        except RuntimeError:
            root_path = os.environ.get('ROOT_PATH', '')
        return os.path.join(root_path, path.lstrip('/')) if root_path else path
    
    def _parse_main_config(self) -> None:
        """Parse the main dnsmasq configuration file to extract paths and settings.
        
        Extracts:
        - dhcp-leasefile path
        - conf-dir directives with directory paths and extensions
        """
        self.logger.info(f"Parsing main config file: {self.config_file_path}")
        
        resolved_config_path = self._resolve_path(self.config_file_path)
        config_file = Path(resolved_config_path)
        if not config_file.exists():
            self.logger.error(f"Main config file not found: {self.config_file_path}")
            raise FileNotFoundError(f"Main config file not found: {self.config_file_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse dhcp-leasefile directive
                    if line.startswith('dhcp-leasefile='):
                        self.lease_file_path = line.split('=', 1)[1].strip()
                        self.logger.info(f"Found lease file path: {self.lease_file_path}")
                    
                    # Parse conf-dir directives
                    elif line.startswith('conf-dir='):
                        conf_dir_content = line.split('=', 1)[1].strip()
                        self._parse_conf_dir(conf_dir_content)
                        
        except Exception as e:
            self.logger.error(f"Error reading main config file: {e}")
            raise
    
    def _parse_conf_dir(self, conf_dir_content: str) -> None:
        """Parse conf-dir directive content.
        
        Args:
            conf_dir_content: Content after 'conf-dir=' (e.g., '/etc/dnsmasq.d/,*.conf')
        """
        parts = conf_dir_content.split(',')
        if len(parts) >= 1:
            directory = parts[0].strip()
            extension = parts[1].strip() if len(parts) > 1 else '*'
            
            self.config_directories.append((directory, extension))
            self.logger.info(f"Found config directory: {directory} with extension: {extension}")
    
    def _discover_config_files(self) -> None:
        """Discover all configuration files based on conf-dir directives.
        
        Applies dnsmasq's default filtering rules:
        - Exclude files ending with ~ (backup files)
        - Exclude files starting with . (hidden files) 
        - Exclude files both starting and ending with # (commented out)
        """
        self.config_files = []
        
        for directory, extension in self.config_directories:
            resolved_directory = self._resolve_path(directory)
            dir_path = Path(resolved_directory)
            
            if not dir_path.exists():
                self.logger.warning(f"Config directory does not exist: {directory}")
                continue
            
            if not dir_path.is_dir():
                self.logger.warning(f"Config path is not a directory: {directory}")
                continue
            
            try:
                for file_path in dir_path.iterdir():
                    if not file_path.is_file():
                        continue
                    
                    filename = file_path.name
                    
                    # Apply dnsmasq's default filtering rules
                    if filename.endswith('~'):
                        continue
                    if filename.startswith('.'):
                        continue
                    if filename.startswith('#') and filename.endswith('#'):
                        continue
                    
                    # Apply extension filtering
                    if extension != '*':
                        # Handle glob patterns like *.conf
                        if extension.startswith('*.'):
                            expected_ext = extension[2:]  # Remove '*.'
                            if not filename.endswith(f'.{expected_ext}'):
                                continue
                        elif extension != filename:
                            continue
                    
                    self.config_files.append(str(file_path))
                    self.logger.debug(f"Discovered config file: {file_path}")
                    
            except Exception as e:
                self.logger.warning(f"Error accessing config directory {directory}: {e}")
                continue
        
        self.logger.info(f"Discovered {len(self.config_files)} configuration files")
    
    def _parse_dhcp_ranges(self) -> None:
        """Parse all configuration files to extract DHCP pool information.
        
        Looks for dhcp-range directives and creates DhcpPool objects.
        """
        self.dhcp_pools = []
        
        for config_file_path in self.config_files:
            try:
                with open(config_file_path, 'r', encoding='utf-8') as file:
                    for line_num, line in enumerate(file, 1):
                        line = line.strip()
                        
                        # Skip empty lines and comments
                        if not line or line.startswith('#'):
                            continue
                        
                        # Look for dhcp-range directives
                        if 'dhcp-range=' in line:
                            pool = self._parse_dhcp_range_line(line)
                            if pool:
                                self.dhcp_pools.append(pool)
                                self.logger.info(f"Found DHCP pool: {pool}")
                                
            except Exception as e:
                self.logger.warning(f"Error reading config file {config_file_path}: {e}")
                continue
        
        self.logger.info(f"Parsed {len(self.dhcp_pools)} DHCP pools")
    
    def _parse_dhcp_range_line(self, line: str) -> Optional[DhcpPool]:
        """Parse dhcp-range configuration line to create DhcpPool object.
        
        Args:
            line: Configuration line containing dhcp-range directive
            
        Returns:
            DhcpPool object or None if parsing fails
            
        Example formats:
        dhcp-range=set:intranet,10.1.1.10,10.1.1.199,255.255.0.0,86400
        dhcp-range=192.168.1.50,192.168.1.150,12h
        """
        try:
            # Find dhcp-range= directive
            dhcp_range_match = re.search(r'dhcp-range=([^#\s]+)', line)
            if not dhcp_range_match:
                return None
            
            # Extract content after dhcp-range=
            dhcp_range_content = dhcp_range_match.group(1)
            
            # Split by commas to get components
            components = [comp.strip() for comp in dhcp_range_content.split(',')]
            
            if len(components) < 2:
                return None
            
            pool_name = None
            start_ip = None
            end_ip = None
            netmask = None
            lease_duration = None
            
            # Parse components based on format
            if components[0].startswith('set:'):
                # Format: set:tag,start_ip,end_ip,netmask,duration
                pool_name = components[0][4:]  # Remove 'set:' prefix
                if len(components) >= 3:
                    start_ip = components[1]
                    end_ip = components[2]
                if len(components) >= 4:
                    netmask = components[3]
                if len(components) >= 5:
                    lease_duration = self._parse_lease_duration(components[4])
            else:
                # Format: start_ip,end_ip,[netmask],[duration]
                pool_name = "default"
                start_ip = components[0]
                end_ip = components[1]
                if len(components) >= 3 and self._is_netmask(components[2]):
                    netmask = components[2]
                    if len(components) >= 4:
                        lease_duration = self._parse_lease_duration(components[3])
                elif len(components) >= 3:
                    lease_duration = self._parse_lease_duration(components[2])
            
            # Validate required fields
            if not start_ip or not end_ip:
                return None
            
            # Default netmask if not specified
            if not netmask:
                netmask = "255.255.255.0"
            
            return DhcpPool(
                pool_name=pool_name,
                start_ip=start_ip,
                end_ip=end_ip,
                netmask=netmask,
                lease_duration=lease_duration
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing dhcp-range line: {line}. Error: {e}")
            return None
    
    def _is_netmask(self, value: str) -> bool:
        """Check if a value looks like a netmask.
        
        Args:
            value: String to check
            
        Returns:
            True if value appears to be a netmask
        """
        # Check for dotted decimal netmask (e.g., 255.255.255.0)
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value):
            parts = value.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        return False
    
    def _parse_lease_duration(self, duration_str: str) -> Optional[int]:
        """Parse lease duration string to seconds.
        
        Args:
            duration_str: Duration string (e.g., '86400', '12h', '1d')
            
        Returns:
            Duration in seconds or None if parsing fails
        """
        try:
            # Check for pure number (seconds)
            if duration_str.isdigit():
                return int(duration_str)
            
            # Check for time suffixes
            if duration_str.endswith('s'):
                return int(duration_str[:-1])
            elif duration_str.endswith('m'):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith('h'):
                return int(duration_str[:-1]) * 3600
            elif duration_str.endswith('d'):
                return int(duration_str[:-1]) * 86400
            
            return None
            
        except (ValueError, IndexError):
            return None
    
    def get_dns_pools(self) -> List[DhcpPool]:
        """Get all discovered DHCP pools.
        
        Returns:
            List of DhcpPool objects
        """
        return self.dhcp_pools.copy()
    
    def get_pool_usage_statistics(self) -> List[Dict]:
        """Calculate usage statistics for all pools.
        
        Returns:
            List of dictionaries containing pool usage information
        """
        statistics = []
        
        # Get current leases to calculate usage
        try:
            current_leases = self.get_all_leases()
        except Exception as e:
            self.logger.error(f"Error getting leases for statistics: {e}")
            current_leases = []
        
        for pool in self.dhcp_pools:
            # Count leases within this pool's range
            used_addresses = sum(
                1 for lease in current_leases 
                if lease.is_active() and pool.contains_ip(lease.ip_address)
            )
            
            available_addresses = pool.total_addresses - used_addresses
            usage_percentage = (used_addresses / pool.total_addresses * 100) if pool.total_addresses > 0 else 0
            
            pool_stats = pool.to_dict()
            pool_stats.update({
                'used_addresses': used_addresses,
                'available_addresses': available_addresses,
                'usage_percentage': round(usage_percentage, 2)
            })
            
            statistics.append(pool_stats)
        
        return statistics
    
    def get_all_leases(self) -> List[DhcpLease]:
        """Get all DHCP leases from cache.
        
        Returns:
            List of DHCP lease objects from cache
        """
        if self._lease_cache is None:
            self.logger.warning("Lease cache is empty, reloading from disk")
            self._load_lease_cache()
        
        return self._lease_cache.copy() if self._lease_cache else []
    
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
        
        resolved_lease_path = self._resolve_path(self.lease_file_path)  # type: ignore
        with open(resolved_lease_path, 'r', encoding='utf-8') as file:
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
            
            # Determine which pool this lease belongs to
            pool_name = self._get_pool_for_ip(ip_address)
            
            return DhcpLease(
                ip_address=ip_address,
                mac_address=mac_address,
                hostname=hostname,
                lease_time=lease_time,
                client_id=client_id,
                is_static=is_static,
                pool_name=pool_name
            )
            
        except (ValueError, IndexError) as e:
            self.logger.warning(f"Error parsing lease line: {line}. Error: {e}")
            return None
    
    def _get_pool_for_ip(self, ip_address: str) -> Optional[str]:
        """Determine which DHCP pool an IP address belongs to.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Pool name or None if IP doesn't belong to any known pool
        """
        for pool in self.dhcp_pools:
            if pool.contains_ip(ip_address):
                return pool.pool_name
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
        """Load static lease configurations from discovered dnsmasq config files.
        
        Reads all configuration files and extracts dhcp-host directives.
        """
        self.logger.info("Loading static leases from discovered config files")
        
        # Initialize cache with mac_to_ip and ip_to_mac mappings
        self._static_leases_cache = {
            'mac_to_ip': {},
            'ip_to_mac': {}
        }
        
        static_count = 0
        
        for config_file_path in self.config_files:
            try:
                with open(config_file_path, 'r', encoding='utf-8') as file:
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
                self.logger.warning(f"Error reading config file {config_file_path}: {e}")
                continue
        
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
    
    def _read_leases_from_disk(self) -> List[DhcpLease]:
        """Read leases from disk without using cache.
        
        Returns:
            List of parsed DHCP lease objects
            
        Raises:
            FileNotFoundError: If lease file does not exist
            PermissionError: If lease file cannot be read
            Exception: For other file access or parsing errors
        """
        if not self.lease_file_path:
            raise FileNotFoundError("No lease file path configured")
        
        self.logger.debug(f"Reading DHCP lease file from disk: {self.lease_file_path}")
        
        # Check if static leases cache is populated, if not load it
        if not self._static_leases_cache:
            self._load_static_leases()
        
        # Check if file exists
        resolved_lease_path = self._resolve_path(self.lease_file_path)  # type: ignore
        lease_file = Path(resolved_lease_path)
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
    
    def _load_lease_cache(self) -> None:
        """Load leases from disk into cache."""
        try:
            self._lease_cache = self._read_leases_from_disk()
            self.logger.info(f"Loaded {len(self._lease_cache)} leases into cache")
        except Exception as e:
            self.logger.error(f"Failed to load lease cache: {e}")
            self._lease_cache = []
    
    def reload_lease_cache(self) -> None:
        """Reload leases from disk into cache."""
        self._load_lease_cache()
    
    def update_lease_cache(self, leases: List[DhcpLease]) -> None:
        """Update the lease cache with new data.
        
        Args:
            leases: List of leases to cache
        """
        self._lease_cache = leases.copy() if leases else []
        self.logger.debug(f"Updated lease cache with {len(self._lease_cache)} leases")