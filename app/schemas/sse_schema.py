"""Marshmallow schemas for SSE event types."""

from marshmallow import fields
from app.schemas.base_schema import BaseSchema


class DataChangeNotificationSchema(BaseSchema):
    """Schema for simple data change notification SSE events."""
    
    event_type = fields.String(
        required=True,
        metadata={
            "description": "Type of notification event",
            "example": "data_changed",
            "enum": ["data_changed"]
        }
    )
    
    timestamp = fields.String(
        required=True,
        metadata={"description": "When the change occurred in ISO 8601 format with Z timezone", "example": "2024-01-15T14:30:00Z"}
    )


class SseConnectionEstablishedSchema(BaseSchema):
    """Schema for SSE connection established event."""
    
    client_id = fields.String(
        required=True,
        metadata={"description": "Unique identifier for this SSE client connection", "example": "client_abc123def456"}
    )
    
    message = fields.String(
        required=True,
        metadata={"description": "Connection confirmation message", "example": "Successfully connected to lease updates stream"}
    )
    
    active_connections = fields.Integer(
        required=True,
        metadata={"description": "Number of currently active SSE connections", "example": 1}
    )


class SseHeartbeatSchema(BaseSchema):
    """Schema for SSE heartbeat events."""
    
    timestamp = fields.Float(
        required=True,
        metadata={"description": "Unix timestamp when heartbeat was sent", "example": 1705324200.123}
    )
    
    active_connections = fields.Integer(
        required=True,
        metadata={"description": "Number of currently active SSE connections", "example": 2}
    )
