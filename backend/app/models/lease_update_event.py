"""Lease update event model for SSE notifications."""

from datetime import datetime
from typing import Dict, Any

from app.models.dhcp_lease import DhcpLease


class LeaseUpdateEvent:
    """Model representing a lease change event for SSE streaming."""
    
    def __init__(self, event_type: str, lease: DhcpLease, timestamp: datetime) -> None:
        """Initialize lease update event.
        
        Args:
            event_type: Type of event (lease_added, lease_updated, lease_removed, lease_expired)
            lease: The lease object associated with the event
            timestamp: When the event occurred
        """
        self.event_type = event_type
        self.lease = lease
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            'event_type': self.event_type,
            'lease': self.lease.to_dict(),
            'timestamp': self.timestamp.isoformat() + 'Z'
        }
