"""Pydantic schemas for DHCP API responses."""

from pydantic import BaseModel, Field


class DhcpLeaseResponse(BaseModel):
    """Schema for a single DHCP lease in API responses."""

    ip_address: str = Field(description="IPv4 address assigned to the client")
    mac_address: str = Field(description="MAC address of the client device")
    hostname: str | None = Field(description="Hostname of the client device")
    lease_time: str = Field(description="Lease expiration time in ISO 8601 format")
    client_id: str | None = Field(description="Optional client identifier")
    is_active: bool = Field(description="Whether the lease is currently active")
    is_static: bool = Field(description="Whether this is a static DHCP assignment")
    pool_name: str | None = Field(description="Name of the DHCP pool this lease belongs to")
    vendor: str | None = Field(description="Device manufacturer from MAC OUI lookup")


class DhcpPoolResponse(BaseModel):
    """Schema for a single DHCP pool in API responses."""

    pool_name: str = Field(description="Pool identifier/tag name")
    start_ip: str = Field(description="Starting IP address of the pool range")
    end_ip: str = Field(description="Ending IP address of the pool range")
    netmask: str = Field(description="Subnet mask for the pool")
    lease_duration: int | None = Field(description="Lease duration in seconds")
    total_addresses: int = Field(description="Total number of addresses in the pool")


class DhcpPoolUsageResponse(DhcpPoolResponse):
    """Schema for DHCP pool usage statistics."""

    used_addresses: int = Field(description="Number of addresses currently in use")
    available_addresses: int = Field(description="Number of available addresses")
    usage_percentage: float = Field(description="Percentage of pool utilization")
