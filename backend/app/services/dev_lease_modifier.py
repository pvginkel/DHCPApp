"""Development mode fake lease modifier service."""

import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import ipaddress

from app.models.dhcp_lease import DhcpLease
from app.models.dhcp_pool import DhcpPool


class DevLeaseModifier:
    """Service for applying fake lease modifications in development mode."""
    
    def __init__(self, dhcp_pools: List[DhcpPool]) -> None:
        """Initialize with DHCP pool information.
        
        Args:
            dhcp_pools: List of DHCP pools for generating realistic IP addresses
        """
        self.dhcp_pools = dhcp_pools
        self.logger = logging.getLogger(__name__)
        self._modification_counter = 0
        self._generated_devices = []
        
        # Initialize random seed for consistent test behavior
        random.seed(42)
        
    def modify_leases(self, base_leases: List[DhcpLease]) -> List[DhcpLease]:
        """Apply random modifications to the lease data.
        
        Args:
            base_leases: Original lease data to modify
            
        Returns:
            Modified lease data with fake changes applied
        """
        if not base_leases:
            self.logger.info("No base leases to modify, returning empty list")
            return []
        
        # Work with a copy to avoid modifying original data
        modified_leases = [self._copy_lease(lease) for lease in base_leases]
        
        # Determine modification type based on rotation logic
        modification_type = self._get_next_modification_type()
        
        self.logger.info(f"Applying {modification_type} modification to leases")
        
        try:
            if modification_type == "add":
                new_lease = self._generate_fake_lease()
                if new_lease:
                    modified_leases.append(new_lease)
                    
            elif modification_type == "remove":
                self._remove_random_dynamic_lease(modified_leases)
                
            elif modification_type == "expire":
                self._modify_lease_expiration(modified_leases)
                
            elif modification_type == "hostname":
                self._modify_hostname(modified_leases)
                
        except Exception as e:
            self.logger.error(f"Error applying {modification_type} modification: {e}")
            
        self.logger.info(f"Modified leases: {len(modified_leases)} total")
        return modified_leases
    
    def _get_next_modification_type(self) -> str:
        """Get the next modification type using rotation logic."""
        modification_types = ["add", "remove", "expire", "hostname"]
        self._modification_counter += 1
        return modification_types[self._modification_counter % len(modification_types)]
    
    def _generate_fake_lease(self) -> Optional[DhcpLease]:
        """Generate a fake lease with realistic data.
        
        Returns:
            New DhcpLease object or None if generation fails
        """
        if not self.dhcp_pools:
            self.logger.warning("No DHCP pools available for generating fake lease")
            return None
            
        try:
            # Select a random pool
            pool = random.choice(self.dhcp_pools)
            
            # Generate random IP within pool range
            ip_address = self._generate_random_ip_in_pool(pool)
            if not ip_address:
                return None
            
            # Generate fake MAC address
            mac_address = self._generate_fake_mac()
            
            # Generate test hostname
            device_number = len(self._generated_devices) + 1
            hostname = f"test-device-{device_number}"
            self._generated_devices.append(hostname)
            
            # Set lease expiration time (1-4 hours from now)
            hours_offset = random.randint(1, 4)
            lease_time = datetime.now() + timedelta(hours=hours_offset)
            
            return DhcpLease(
                ip_address=ip_address,
                mac_address=mac_address,
                hostname=hostname,
                lease_time=lease_time,
                client_id=None,
                is_static=False,  # Generated leases are always dynamic
                pool_name=pool.pool_name
            )
            
        except Exception as e:
            self.logger.error(f"Error generating fake lease: {e}")
            return None
    
    def _generate_random_ip_in_pool(self, pool: DhcpPool) -> Optional[str]:
        """Generate a random IP address within the specified pool range.
        
        Args:
            pool: DHCP pool to generate IP within
            
        Returns:
            Random IP address string or None if generation fails
        """
        try:
            start_ip = ipaddress.IPv4Address(pool.start_ip)
            end_ip = ipaddress.IPv4Address(pool.end_ip)
            
            # Generate random offset within the range
            ip_range = int(end_ip) - int(start_ip)
            random_offset = random.randint(0, ip_range)
            
            random_ip = start_ip + random_offset
            return str(random_ip)
            
        except Exception as e:
            self.logger.error(f"Error generating random IP for pool {pool.pool_name}: {e}")
            return None
    
    def _generate_fake_mac(self) -> str:
        """Generate a fake MAC address.
        
        Returns:
            Fake MAC address in normalized format
        """
        # Generate random MAC with a reserved OUI prefix for testing
        # Using 02:xx:xx:xx:xx:xx (locally administered)
        mac_parts = ['02']
        for _ in range(5):
            mac_parts.append(f"{random.randint(0, 255):02x}")
        
        return ':'.join(mac_parts)
    
    def _remove_random_dynamic_lease(self, leases: List[DhcpLease]) -> None:
        """Remove a random dynamic lease from the list.
        
        Args:
            leases: List of leases to modify (modified in place)
        """
        # Find dynamic leases (not static)
        dynamic_leases = [i for i, lease in enumerate(leases) if not lease.is_static]
        
        if not dynamic_leases:
            self.logger.info("No dynamic leases found to remove")
            return
        
        # Select random dynamic lease to remove
        lease_index = random.choice(dynamic_leases)
        removed_lease = leases.pop(lease_index)
        
        self.logger.info(f"Removed dynamic lease: {removed_lease.ip_address} ({removed_lease.hostname})")
    
    def _modify_lease_expiration(self, leases: List[DhcpLease]) -> None:
        """Modify expiration time of a random lease.
        
        Args:
            leases: List of leases to modify (modified in place)
        """
        if not leases:
            return
        
        # Select random lease to modify
        lease = random.choice(leases)
        
        # Don't modify static leases (they have timestamp 0)
        if lease.is_static:
            return
        
        # Apply random time change (-30 minutes to +2 hours)
        minutes_change = random.randint(-30, 120)
        new_lease_time = lease.lease_time + timedelta(minutes=minutes_change)
        
        old_time = lease.lease_time
        lease.lease_time = new_lease_time
        
        self.logger.info(f"Modified expiration for {lease.ip_address}: {old_time} -> {new_lease_time}")
    
    def _modify_hostname(self, leases: List[DhcpLease]) -> None:
        """Modify hostname of a random lease.
        
        Args:
            leases: List of leases to modify (modified in place)
        """
        if not leases:
            return
        
        # Select random lease to modify
        lease = random.choice(leases)
        
        # Generate modified hostname
        old_hostname = lease.hostname
        lease.hostname = f"modified-hostname-{random.randint(1, 999)}"
        
        self.logger.info(f"Modified hostname for {lease.ip_address}: {old_hostname} -> {lease.hostname}")
    
    def _copy_lease(self, lease: DhcpLease) -> DhcpLease:
        """Create a deep copy of a DhcpLease object.
        
        Args:
            lease: Original lease object
            
        Returns:
            Copy of the lease object
        """
        return DhcpLease(
            ip_address=lease.ip_address,
            mac_address=lease.mac_address,
            hostname=lease.hostname,
            lease_time=lease.lease_time,
            client_id=lease.client_id,
            is_static=lease.is_static,
            pool_name=lease.pool_name
        )