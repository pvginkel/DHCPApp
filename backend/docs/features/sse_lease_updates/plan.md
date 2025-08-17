# Server-Sent Events for DHCP Lease Updates - Technical Plan

## Brief Description

Implement Server-Sent Events (SSE) real-time streaming for DHCP lease updates as specified in the product brief. The feature includes two main components: an internal notification endpoint that receives change notifications from companion containers (containing no lease data), and an SSE endpoint that streams lease updates to connected clients. When notified of changes, the app must re-read the lease file and compare against previous state to determine what changed. This enables real-time monitoring of IP address allocations and device connectivity changes without requiring clients to poll the API.

## Files and Functions to Create or Modify

### New Files to Create

1. **`app/services/sse_service.py`**
   - Create `SseService` class to manage SSE connections and event broadcasting
   - `__init__(self, dhcp_service: DhcpService) -> None` - Initialize service with connection tracking and DHCP service reference
   - `add_client(self, client_id: str) -> None` - Register new SSE client connection
   - `remove_client(self, client_id: str) -> None` - Unregister SSE client connection
   - `process_lease_change_notification(self) -> None` - Re-read leases, detect changes, and broadcast updates
   - `broadcast_lease_events(self, events: List[LeaseUpdateEvent]) -> None` - Send lease events to all connected clients
   - `get_active_connections_count(self) -> int` - Get count of active SSE connections
   - `_format_sse_message(self, event_type: str, data: Dict[str, Any]) -> str` - Format data as SSE message
   - `_detect_lease_changes(self, current_leases: List[DhcpLease]) -> List[LeaseUpdateEvent]` - Compare current vs cached leases to detect changes
   - `_cache_current_leases(self, leases: List[DhcpLease]) -> None` - Update internal lease cache

2. **`app/models/lease_update_event.py`**
   - Create `LeaseUpdateEvent` class to represent lease change events
   - `__init__(self, event_type: str, lease: DhcpLease, timestamp: datetime) -> None` - Initialize event
   - `to_dict(self) -> Dict[str, Any]` - Convert event to dictionary for JSON serialization
   - Event types: `lease_added`, `lease_updated`, `lease_removed`, `lease_expired`

3. **`app/api/v1/sse_routes.py`**
   - Create SSE-specific route handlers
   - `lease_updates_stream()` - SSE endpoint for streaming lease updates (`/api/v1/leases/stream`)
   - `notify_lease_change()` - Internal notification endpoint that triggers lease re-read (`/api/v1/internal/notify-lease-change`)

### Files to Modify

1. **`app/api/v1/__init__.py`**
   - Import new sse_routes module to register SSE routes with blueprint

2. **`app/services/__init__.py`**
   - Add import for SseService to make it available package-wide

3. **`requirements.txt`**
   - No additional dependencies required - Flask natively supports SSE

4. **`app/__init__.py`**
   - Initialize global SseService instance in application factory
   - Store SseService instance in Flask app context for access across modules

## Step-by-Step Algorithm Implementation

### 1. SSE Connection Management Algorithm

**Method: `SseService.add_client()` and `SseService.remove_client()`**
1. Maintain a dictionary of active client connections: `{client_id: connection_info}`
2. For `add_client()`: Generate unique client ID using UUID, store connection details
3. For `remove_client()`: Remove client from active connections dictionary
4. Implement connection health checking to automatically remove stale connections

### 2. Lease Change Detection Algorithm

**Method: `SseService._detect_lease_changes()`**
1. Accept current lease list from fresh file read
2. Compare against cached previous lease state (stored in instance variable)
3. Identify changes by comparing lease dictionaries:
   - **lease_added**: Leases in current but not in cache
   - **lease_updated**: Leases with same IP/MAC but different hostname, lease_time, or is_static
   - **lease_removed**: Leases in cache but not in current
   - **lease_expired**: Leases in current with lease_time < current_time (and wasn't expired in cache)
4. Create LeaseUpdateEvent objects for each detected change
5. Return list of LeaseUpdateEvent objects

### 3. SSE Message Broadcasting Algorithm

**Method: `SseService.broadcast_lease_events()`**
1. Accept list of LeaseUpdateEvent objects
2. For each event, format as SSE message using `_format_sse_message()`
3. Iterate through all active client connections
4. Send formatted SSE message to each connected client
5. Remove any clients that fail to receive the message (connection cleanup)

### 4. SSE Message Formatting Algorithm

**Method: `SseService._format_sse_message()`**
1. Accept event type (`lease_added`, `lease_updated`, `lease_removed`, `lease_expired`) and data dictionary
2. Format according to SSE specification:
   ```
   event: {event_type}
   data: {json_serialized_data}
   id: {unique_message_id}
   
   ```
3. Include timestamp and event ID for client-side message tracking
4. Return properly formatted SSE message string

### 5. Lease Change Notification Algorithm

**Method: `notify_lease_change()` endpoint**
1. Accept POST request from companion container (no payload data expected)
2. Retrieve global SseService instance from Flask app context
3. Call `process_lease_change_notification()` to trigger lease re-read and change detection
4. Return success response to companion container

**Method: `SseService.process_lease_change_notification()`**
1. Use injected DhcpService to call `get_all_leases()` for fresh lease data
2. Call `_detect_lease_changes()` with current leases vs cached leases
3. If changes detected, call `broadcast_lease_events()` with detected events
4. Call `_cache_current_leases()` to update cached state for next comparison

### 6. SSE Stream Endpoint Algorithm

**Method: `lease_updates_stream()` endpoint**
1. Generate unique client ID for new connection
2. Set appropriate SSE response headers:
   - `Content-Type: text/event-stream`
   - `Cache-Control: no-cache`
   - `Connection: keep-alive`
3. Register client with SseService using `add_client()`
4. Send initial connection confirmation event to client
5. Maintain connection by sending periodic heartbeat events
6. Handle client disconnection by calling `remove_client()`

### 7. Event Type Determination Algorithm

**Method: Event type classification logic in `_detect_lease_changes()`**
1. **lease_added**: New lease appears in current leases that doesn't exist in cached lease state (compare by IP address as primary key)
2. **lease_updated**: Existing lease (same IP) has changes in MAC address, hostname, lease_time, client_id, or is_static status
3. **lease_removed**: Previously cached lease no longer appears in current leases
4. **lease_expired**: Lease exists in current state with lease_time < current_time, but was not expired in previous cached state

## Implementation Phases

### Phase 1: Core SSE Infrastructure
- Implement `SseService` class with connection management and lease caching
- Create `LeaseUpdateEvent` model
- Add SSE stream endpoint (`/api/v1/leases/stream`)
- Implement basic SSE message formatting and broadcasting

### Phase 2: Change Detection and Notification Integration
- Implement lease change detection algorithm (`_detect_lease_changes()`)
- Add internal notification endpoint (`/api/v1/internal/notify-lease-change`)
- Integrate notification endpoint with lease re-reading and change detection
- Add error handling for file access and parsing during change detection

### Phase 3: Connection Management and Reliability
- Implement connection health checking and cleanup
- Add heartbeat mechanism for maintaining connections
- Implement automatic reconnection handling on client side
- Add logging and monitoring for SSE connection statistics

### Phase 4: Testing and Optimization
- Add comprehensive error handling for network failures
- Implement connection limits and rate limiting if needed
- Add detailed logging for debugging SSE issues
- Performance testing with multiple concurrent connections
