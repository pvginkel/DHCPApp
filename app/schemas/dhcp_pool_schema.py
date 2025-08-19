"""Schema for DHCP Pool serialization."""

from marshmallow import Schema, fields
from app.schemas.base_schema import BaseSchema


class DhcpPoolSchema(BaseSchema):
    """Schema for serializing DHCP Pool objects."""
    
    pool_name = fields.Str(required=True, description="Pool identifier/tag name")
    start_ip = fields.Str(required=True, description="Starting IP address of the pool range")
    end_ip = fields.Str(required=True, description="Ending IP address of the pool range")
    netmask = fields.Str(required=True, description="Subnet mask for the pool")
    lease_duration = fields.Int(allow_none=True, description="Lease duration in seconds")
    total_addresses = fields.Int(required=True, description="Total number of addresses in the pool")


class DhcpPoolUsageSchema(BaseSchema):
    """Schema for serializing DHCP Pool usage statistics."""
    
    pool_name = fields.Str(required=True, description="Pool identifier/tag name")
    start_ip = fields.Str(required=True, description="Starting IP address of the pool range")
    end_ip = fields.Str(required=True, description="Ending IP address of the pool range")
    netmask = fields.Str(required=True, description="Subnet mask for the pool")
    lease_duration = fields.Int(allow_none=True, description="Lease duration in seconds")
    total_addresses = fields.Int(required=True, description="Total number of addresses in the pool")
    used_addresses = fields.Int(required=True, description="Number of addresses currently in use")
    available_addresses = fields.Int(required=True, description="Number of available addresses")
    usage_percentage = fields.Float(required=True, description="Percentage of pool utilization")