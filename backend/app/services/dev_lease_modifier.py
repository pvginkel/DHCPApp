"""Development mode fake lease modifier service."""

import ipaddress
import logging
import random
from datetime import datetime, timedelta

from app.models.dhcp_lease import DhcpLease
from app.models.dhcp_pool import DhcpPool


class DevLeaseModifier:
    """Service for applying fake lease modifications in development mode."""

    def __init__(self, dhcp_pools: list[DhcpPool]) -> None:
        self.dhcp_pools = dhcp_pools
        self.logger = logging.getLogger(__name__)
        self._modification_counter = 0
        self._generated_devices: list[str] = []

        random.seed(42)

    def modify_leases(self, base_leases: list[DhcpLease]) -> list[DhcpLease]:
        """Apply random modifications to the lease data."""
        modified_leases = [self._copy_lease(lease) for lease in base_leases]
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

    def _generate_fake_lease(self) -> DhcpLease | None:
        """Generate a fake lease with realistic data."""
        if not self.dhcp_pools:
            self.logger.warning("No DHCP pools available for generating fake lease")
            return None

        try:
            pool = random.choice(self.dhcp_pools)
            ip_address = self._generate_random_ip_in_pool(pool)
            if not ip_address:
                return None

            mac_address = self._generate_fake_mac()
            device_number = len(self._generated_devices) + 1
            hostname = f"test-device-{device_number}"
            self._generated_devices.append(hostname)

            hours_offset = random.randint(1, 4)
            lease_time = datetime.now() + timedelta(hours=hours_offset)

            return DhcpLease(
                ip_address=ip_address,
                mac_address=mac_address,
                hostname=hostname,
                lease_time=lease_time,
                client_id=None,
                is_static=False,
                pool_name=pool.pool_name,
            )

        except Exception as e:
            self.logger.error(f"Error generating fake lease: {e}")
            return None

    def _generate_random_ip_in_pool(self, pool: DhcpPool) -> str | None:
        """Generate a random IP address within the specified pool range."""
        try:
            start_ip = ipaddress.IPv4Address(pool.start_ip)
            end_ip = ipaddress.IPv4Address(pool.end_ip)

            ip_range = int(end_ip) - int(start_ip)
            random_offset = random.randint(0, ip_range)

            return str(start_ip + random_offset)

        except Exception as e:
            self.logger.error(f"Error generating random IP for pool {pool.pool_name}: {e}")
            return None

    def _generate_fake_mac(self) -> str:
        """Generate a fake MAC address with locally-administered OUI prefix."""
        mac_parts = ["02"]
        for _ in range(5):
            mac_parts.append(f"{random.randint(0, 255):02x}")
        return ":".join(mac_parts)

    def _remove_random_dynamic_lease(self, leases: list[DhcpLease]) -> None:
        """Remove a random dynamic lease from the list (modified in place)."""
        dynamic_leases = [i for i, lease in enumerate(leases) if not lease.is_static]

        if not dynamic_leases:
            self.logger.info("No dynamic leases found to remove")
            return

        lease_index = random.choice(dynamic_leases)
        removed_lease = leases.pop(lease_index)
        self.logger.info(f"Removed dynamic lease: {removed_lease.ip_address} ({removed_lease.hostname})")

    def _modify_lease_expiration(self, leases: list[DhcpLease]) -> None:
        """Modify expiration time of a random lease (modified in place)."""
        if not leases:
            return

        lease = random.choice(leases)
        if lease.is_static:
            return

        minutes_change = random.randint(-30, 120)
        new_lease_time = lease.lease_time + timedelta(minutes=minutes_change)

        old_time = lease.lease_time
        lease.lease_time = new_lease_time
        self.logger.info(f"Modified expiration for {lease.ip_address}: {old_time} -> {new_lease_time}")

    def _modify_hostname(self, leases: list[DhcpLease]) -> None:
        """Modify hostname of a random lease (modified in place)."""
        if not leases:
            return

        lease = random.choice(leases)
        old_hostname = lease.hostname
        lease.hostname = f"modified-hostname-{random.randint(1, 999)}"
        self.logger.info(f"Modified hostname for {lease.ip_address}: {old_hostname} -> {lease.hostname}")

    def _copy_lease(self, lease: DhcpLease) -> DhcpLease:
        """Create a deep copy of a DhcpLease object."""
        return DhcpLease(
            ip_address=lease.ip_address,
            mac_address=lease.mac_address,
            hostname=lease.hostname,
            lease_time=lease.lease_time,
            client_id=lease.client_id,
            is_static=lease.is_static,
            pool_name=lease.pool_name,
        )
