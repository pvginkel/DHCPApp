"""Marshmallow schema for DHCP lease objects."""

from marshmallow import fields
from app.schemas.base_schema import BaseSchema


class DhcpLeaseSchema(BaseSchema):
    """Schema for DHCP lease data model."""
    
    ip_address = fields.String(
        required=True,
        description="IPv4 address assigned to the client",
        example="192.168.1.100"
    )
    
    mac_address = fields.String(
        required=True,
        description="MAC address of the client device",
        example="aa:bb:cc:dd:ee:ff"
    )
    
    hostname = fields.String(
        allow_none=True,
        description="Hostname of the client device, null if unknown",
        example="laptop-001"
    )
    
    lease_time = fields.String(
        required=True,
        description="Lease expiration time in ISO 8601 format with Z timezone",
        example="2024-01-15T14:30:00Z"
    )
    
    client_id = fields.String(
        allow_none=True,
        description="Optional client identifier, null if not available",
        example="01:aa:bb:cc:dd:ee:ff"
    )
    
    is_active = fields.Boolean(
        required=True,
        description="Whether the lease is currently active (not expired)",
        example=True
    )
    
    is_static = fields.Boolean(
        required=True,
        description="Whether this is a static DHCP assignment from configuration",
        example=False
    )
