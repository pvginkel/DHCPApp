"""Marshmallow schema for error responses."""

from marshmallow import fields
from app.schemas.base_schema import BaseSchema


class ErrorSchema(BaseSchema):
    """Schema for API error responses."""
    
    error = fields.String(
        required=True,
        metadata={"description": "Error message describing what went wrong", "example": "Unable to read DHCP lease file"}
    )
    
    details = fields.String(
        allow_none=True,
        metadata={"description": "Additional error details or technical information", "example": "FileNotFoundError: /var/lib/dhcp/dhcpd.leases not found"}
    )
