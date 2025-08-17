"""Marshmallow schemas for OpenAPI documentation generation."""

from app.schemas.base_schema import BaseSchema
from app.schemas.dhcp_lease_schema import DhcpLeaseSchema
from app.schemas.error_schema import ErrorSchema
from app.schemas.sse_schema import (
    LeaseUpdateEventSchema,
    SseConnectionEstablishedSchema,
    SseHeartbeatSchema
)

__all__ = [
    'BaseSchema',
    'DhcpLeaseSchema',
    'ErrorSchema',
    'LeaseUpdateEventSchema',
    'SseConnectionEstablishedSchema',
    'SseHeartbeatSchema'
]
