"""Server-Sent Events service for DHCP lease updates."""

import json
import logging
import queue
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Response, current_app

from app.models.dhcp_lease import DhcpLease
from app.models.lease_update_event import DataChangeNotification
from app.services.dhcp_service import DhcpService
from app.services.dev_lease_modifier import DevLeaseModifier


class SseService:
    """Service for managing SSE connections and broadcasting lease updates."""
    
    def __init__(self, dhcp_service: DhcpService) -> None:
        """Initialize SSE service with DHCP service reference.
        
        Args:
            dhcp_service: DhcpService instance for reading lease data
        """
        self.dhcp_service = dhcp_service
        self.logger = logging.getLogger(__name__)
        self._active_connections: Dict[str, Dict[str, Any]] = {}
        self._message_id_counter = 0
        self._dev_lease_modifier: Optional[DevLeaseModifier] = None
    
    def add_client(self, client_id: str) -> queue.Queue:
        """Register new SSE client connection.
        
        Args:
            client_id: Unique identifier for the client connection
            
        Returns:
            Message queue for the client
        """
        message_queue = queue.Queue()
        self._active_connections[client_id] = {
            'connected_at': datetime.now(),
            'last_heartbeat': datetime.now(),
            'queue': message_queue
        }
        self.logger.info(f"SSE client connected: {client_id}")
        return message_queue
    
    def remove_client(self, client_id: str) -> None:
        """Unregister SSE client connection.
        
        Args:
            client_id: Unique identifier for the client connection
        """
        if client_id in self._active_connections:
            del self._active_connections[client_id]
            self.logger.info(f"SSE client disconnected: {client_id}")
    
    def get_active_connections_count(self) -> int:
        """Get count of active SSE connections.
        
        Returns:
            Number of active connections
        """
        return len(self._active_connections)
    
    def process_lease_change_notification(self) -> None:
        """Process lease change notification and update cache."""
        try:
            # Check if we're in development mode with fake lease changes enabled
            if self._is_dev_mode_with_fake_changes():
                self._apply_fake_changes_to_cache()
            else:
                # Reload lease cache from disk
                self.dhcp_service.reload_lease_cache()
            
            # Always broadcast a simple data change notification
            self.logger.info("Broadcasting data change notification")
            notification = DataChangeNotification(datetime.utcnow())
            self.broadcast_data_change_notification(notification)
            
        except Exception as e:
            self.logger.error(f"Error processing lease change notification: {e}")
    
    def broadcast_data_change_notification(self, notification: DataChangeNotification) -> None:
        """Send data change notification to all connected clients.
        
        Args:
            notification: Data change notification to broadcast
        """
        if not self._active_connections:
            self.logger.debug("No active SSE connections to broadcast to")
            return
        
        # Format notification as SSE message and queue for clients
        sse_message = self._format_sse_message(notification.event_type, notification.to_dict())
        
        # Send to all connected clients
        failed_clients = []
        for client_id, connection_info in self._active_connections.items():
            try:
                # Add message to client's queue
                connection_info['queue'].put(sse_message)
                self.logger.debug(f"Queued data change notification for client {client_id}")
            except Exception as e:
                self.logger.warning(f"Failed to queue notification for client {client_id}: {e}")
                failed_clients.append(client_id)
        
        # Clean up failed connections
        for client_id in failed_clients:
            self.remove_client(client_id)
    
    def _format_sse_message(self, event_type: str, data: Dict[str, Any]) -> str:
        """Format data as SSE message.
        
        Args:
            event_type: Type of SSE event
            data: Event data dictionary
            
        Returns:
            Properly formatted SSE message string
        """
        self._message_id_counter += 1
        message_id = str(self._message_id_counter)
        
        # Format according to SSE specification
        sse_message = f"event: {event_type}\n"
        sse_message += f"data: {json.dumps(data)}\n"
        sse_message += f"id: {message_id}\n"
        sse_message += "\n"  # Empty line to terminate the message
        
        return sse_message
    
    
    def generate_client_id(self) -> str:
        """Generate unique client ID for new SSE connection.
        
        Returns:
            Unique client identifier
        """
        return str(uuid.uuid4())
    
    def _is_dev_mode_with_fake_changes(self) -> bool:
        """Check if development mode with fake lease changes is enabled.
        
        Returns:
            True if dev mode with fake changes is enabled
        """
        try:
            return (
                current_app.config.get('FLASK_ENV') == 'development' and
                current_app.config.get('DEV_FAKE_LEASE_CHANGES', False)
            )
        except RuntimeError:
            # Outside of Flask app context
            return False
    
    def _apply_fake_changes_to_cache(self) -> None:
        """Apply fake changes directly to the lease cache for development mode."""
        # Initialize dev lease modifier if not already done
        if self._dev_lease_modifier is None:
            dhcp_pools = self.dhcp_service.get_dns_pools()
            self._dev_lease_modifier = DevLeaseModifier(dhcp_pools)
        
        # Get current cached leases
        current_leases = self.dhcp_service.get_all_leases()
        
        # Apply fake modifications
        modified_leases = self._dev_lease_modifier.modify_leases(current_leases)
        
        # Update the cache with modified leases
        self.dhcp_service.update_lease_cache(modified_leases)
        
        self.logger.info(f"Applied fake changes to cache: {len(modified_leases)} leases")
