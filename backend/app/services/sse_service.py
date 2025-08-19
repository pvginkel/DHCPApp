"""Server-Sent Events service for DHCP lease updates."""

import json
import logging
import queue
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Response, current_app

from app.models.dhcp_lease import DhcpLease
from app.models.lease_update_event import LeaseUpdateEvent
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
        self._cached_leases: Dict[str, DhcpLease] = {}
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
        """Re-read leases, detect changes, and broadcast updates."""
        try:
            # Check if we're in development mode with fake lease changes enabled
            if self._is_dev_mode_with_fake_changes():
                current_leases = self._get_fake_modified_leases()
            else:
                # Get current leases from DHCP service normally
                current_leases = self.dhcp_service.get_all_leases()
            
            # Detect changes compared to cached state
            events = self._detect_lease_changes(current_leases)
            
            # Broadcast events if any changes detected
            if events:
                self.logger.info(f"Broadcasting {len(events)} lease change events")
                self.broadcast_lease_events(events)
            
            # Update cached state
            self._cache_current_leases(current_leases)
            
        except Exception as e:
            self.logger.error(f"Error processing lease change notification: {e}")
    
    def broadcast_lease_events(self, events: List[LeaseUpdateEvent]) -> None:
        """Send lease events to all connected clients.
        
        Args:
            events: List of lease update events to broadcast
        """
        if not self._active_connections:
            self.logger.debug("No active SSE connections to broadcast to")
            return
        
        # Format events as SSE messages and queue them for clients
        for event in events:
            sse_message = self._format_sse_message(event.event_type, event.to_dict())
            
            # Send to all connected clients
            failed_clients = []
            for client_id, connection_info in self._active_connections.items():
                try:
                    # Add message to client's queue
                    connection_info['queue'].put(sse_message)
                    self.logger.debug(f"Queued event {event.event_type} for client {client_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to queue event for client {client_id}: {e}")
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
    
    def _detect_lease_changes(self, current_leases: List[DhcpLease]) -> List[LeaseUpdateEvent]:
        """Compare current vs cached leases to detect changes.
        
        Args:
            current_leases: List of current leases from fresh file read
            
        Returns:
            List of detected lease update events
        """
        events = []
        current_time = datetime.now()
        
        # Create lookup dictionaries using IP address as key
        current_lease_dict = {lease.ip_address: lease for lease in current_leases}
        cached_lease_dict = self._cached_leases.copy()
        
        # Detect new leases (lease_added)
        for ip_address, lease in current_lease_dict.items():
            if ip_address not in cached_lease_dict:
                events.append(LeaseUpdateEvent('lease_added', lease, current_time))
        
        # Detect removed leases (lease_removed)
        for ip_address, lease in cached_lease_dict.items():
            if ip_address not in current_lease_dict:
                events.append(LeaseUpdateEvent('lease_removed', lease, current_time))
        
        # Detect updated and expired leases
        for ip_address, current_lease in current_lease_dict.items():
            if ip_address in cached_lease_dict:
                cached_lease = cached_lease_dict[ip_address]
                
                # Check for lease updates (same IP but different attributes)
                if self._lease_attributes_changed(current_lease, cached_lease):
                    events.append(LeaseUpdateEvent('lease_updated', current_lease, current_time))
                
                # Check for lease expiration
                if self._lease_became_expired(current_lease, cached_lease):
                    events.append(LeaseUpdateEvent('lease_expired', current_lease, current_time))
        
        return events
    
    def _lease_attributes_changed(self, current: DhcpLease, cached: DhcpLease) -> bool:
        """Check if lease attributes have changed.
        
        Args:
            current: Current lease state
            cached: Previously cached lease state
            
        Returns:
            True if attributes changed, False otherwise
        """
        return (
            current.mac_address != cached.mac_address or
            current.hostname != cached.hostname or
            current.lease_time != cached.lease_time or
            current.client_id != cached.client_id or
            current.is_static != cached.is_static
        )
    
    def _lease_became_expired(self, current: DhcpLease, cached: DhcpLease) -> bool:
        """Check if lease became expired since last check.
        
        Args:
            current: Current lease state
            cached: Previously cached lease state
            
        Returns:
            True if lease became expired, False otherwise
        """
        current_is_expired = not current.is_active()
        cached_was_active = cached.is_active()
        
        return current_is_expired and cached_was_active
    
    def _cache_current_leases(self, leases: List[DhcpLease]) -> None:
        """Update internal lease cache.
        
        Args:
            leases: List of current leases to cache
        """
        self._cached_leases = {lease.ip_address: lease for lease in leases}
        self.logger.debug(f"Cached {len(leases)} leases for change detection")
    
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
    
    def _get_fake_modified_leases(self) -> List[DhcpLease]:
        """Get fake modified leases for development mode.
        
        Returns:
            List of modified leases with fake changes applied
        """
        # Initialize dev lease modifier if not already done
        if self._dev_lease_modifier is None:
            dhcp_pools = self.dhcp_service.get_dns_pools()
            self._dev_lease_modifier = DevLeaseModifier(dhcp_pools)
        
        # Get base leases from file
        base_leases = self.dhcp_service.get_all_leases()
        
        # Apply fake modifications
        modified_leases = self._dev_lease_modifier.modify_leases(base_leases)
        
        # Cache the modified leases in DHCP service
        self.dhcp_service.set_modified_lease_data(modified_leases)
        
        self.logger.info(f"Generated {len(modified_leases)} fake modified leases")
        return modified_leases
