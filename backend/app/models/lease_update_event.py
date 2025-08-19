"""Simple data change notification for SSE streaming."""

from datetime import datetime
from typing import Dict, Any


class DataChangeNotification:
    """Model representing a simple data change notification for SSE streaming."""
    
    def __init__(self, timestamp: datetime) -> None:
        """Initialize data change notification.
        
        Args:
            timestamp: When the change occurred
        """
        self.event_type = "data_changed"
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the notification
        """
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }
